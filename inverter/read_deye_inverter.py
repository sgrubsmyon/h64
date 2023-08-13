#!/usr/bin/env python3

import argparse
import logging
import sys
import os
import socket
import libscrc
import configparser
import pandas
import numpy as np
from datetime import datetime

# Based on: https://github.com/kbialek/deye-inverter-mqtt

# so that files like config.cfg are always found, no matter from where the script is being run
os.chdir(os.path.dirname(sys.argv[0]))


def load_config():
    config = configparser.ConfigParser()
    config.read("../config.cfg")
    config = config["DeyeInverter"]
    return config


# Define global variables:
log = logging.getLogger("DeyeInverter")
config = load_config()

# Load metadata:
all_metrics = pandas.read_csv("deye_sun-10k-sg04lp3_metrics.csv")
groups = np.unique(all_metrics["Group"])


def find_register_address_ranges(all_metrics):
    all_reg_addresses = []
    for _, row in all_metrics.iterrows():
        addr_first = row["Modbus first address"]
        addr_last = row["Modbus last address"]
        all_reg_addresses += list(range(addr_first, addr_last + 1))
    all_reg_addresses = sorted(all_reg_addresses)

    reg_addr_ranges = []
    addr = all_reg_addresses[0]
    range_low = addr
    for addr2 in all_reg_addresses[1:]:
        if addr2 > addr + 1:
            range_high = addr
            reg_addr_ranges.append((range_low, range_high))
            range_low = addr2
        addr = addr2
    # Append very last range
    range_high = addr
    reg_addr_ranges.append((range_low, range_high))

    return reg_addr_ranges


def modbus_read_request_frame(first_reg: int, last_reg: int) -> bytearray:
    # Credits: kbialek
    reg_count = last_reg - first_reg + 1
    return bytearray.fromhex("0103{:04x}{:04x}".format(first_reg, reg_count))


def modbus_request_frame(modbus_frame) -> bytearray:
    # Credits: kbialek
    start = bytearray.fromhex("A5")  # start
    length = (15 + len(modbus_frame) + 2).to_bytes(2, "little")  # datalength
    controlcode = bytearray.fromhex("1045")  # controlCode
    inverter_sn_prefix = bytearray.fromhex("0000")  # serial
    datafield = bytearray.fromhex("020000000000000000000000000000")
    modbus_crc = bytearray.fromhex(
        "{:04x}".format(libscrc.modbus(modbus_frame)))
    modbus_crc.reverse()
    checksum = bytearray.fromhex("00")  # checksum placeholder for outer frame
    end_code = bytearray.fromhex("15")
    inverter_sn = bytearray.fromhex(
        "{:10x}".format(int(config["inverter_serialnumber"])))
    inverter_sn.reverse()
    frame = (
        start
        + length
        + controlcode
        + inverter_sn_prefix
        + inverter_sn
        + datafield
        + modbus_frame
        + modbus_crc
        + checksum
        + end_code
    )

    checksum = 0
    for i in range(1, len(frame) - 2, 1):
        checksum += frame[i] & 255
    frame[len(frame) - 2] = int((checksum & 255))

    return frame


def send_request(req_frame) -> bytes | None:
    # Credits: kbialek
    try:
        sock_conn = socket.create_connection(
            (config["inverter_ip"], int(config["inverter_port"])), timeout=10
        )
    except OSError as e:
        log.error("Could not open socket on IP %s: %s",
                  config["inverter_ip"], e)
        return

    log.debug("Request frame: %s", req_frame.hex())
    sock_conn.sendall(req_frame)

    attempts = 5
    while attempts > 0:
        attempts = attempts - 1
        try:
            data = sock_conn.recv(1024)
            if data:
                log.debug(
                    "Received response frame in %s. attempt: %s", 5 - attempts, data.hex())
                return data
            log.warning("No data received")
        except socket.timeout:
            log.debug("Connection response timeout")
            if attempts == 0:
                log.warning("Too many connection timeouts")
        except OSError as e:
            log.error("Connection error: %s: %s",
                      config["inverter_ip"], e)
            return
        except Exception:
            log.exception("Unknown connection error")
            return
    return


def parse_response_error_code(frame: bytes) -> None:
    # Credits: kbialek
    error_frame = frame[25:-2]
    error_code = error_frame[0]
    if error_code == 0x05:
        log.error("Modbus device address does not match.")
    elif error_code == 0x06:
        log.error(
            "Logger Serial Number does not match. Check your configuration file.")
    else:
        log.error(
            "Unknown response error code. Error frame: %s", error_frame.hex())


def extract_modbus_response_frame(frame: bytes | None) -> bytes | None:
    # Credits: kbialek
    # 29 - outer frame, 2 - modbus addr and command, 2 - modbus crc
    if not frame:
        # Error was already logged in `send_request()` function
        return None
    if len(frame) == 29:
        parse_response_error_code(frame)
        return None
    if len(frame) < (29 + 4):
        log.error("Response frame is too short")
        return None
    if frame[0] != 0xA5:
        log.error("Response frame has invalid starting byte")
        return None
    if frame[-1] != 0x15:
        log.error("Response frame has invalid ending byte")
        return None
    return frame[25:-2]


def modbus_read_response_to_registers(frame: bytes, first_reg: int, last_reg: int) -> dict[int, bytearray]:
    # Credits: kbialek
    reg_count = last_reg - first_reg + 1
    registers = {}
    expected_frame_data_len = 2 + 1 + reg_count * 2
    if len(frame) < expected_frame_data_len + 2:  # 2 bytes for crc
        log.error("Modbus frame is too short")
        return registers
    actual_crc = int.from_bytes(
        frame[expected_frame_data_len: expected_frame_data_len + 2], "little")
    expected_crc = libscrc.modbus(frame[0:expected_frame_data_len])
    if actual_crc != expected_crc:
        log.error(
            "Modbus frame CRC is not valid. Expected {:04x}, got {:04x}".format(
                expected_crc, actual_crc)
        )
        return registers
    a = 0
    while a < reg_count:
        p1 = 3 + (a * 2)
        p2 = p1 + 2
        registers[a + first_reg] = frame[p1:p2]
        a += 1
    return registers


def read_registers(first_reg: int, last_reg: int) -> dict[int, bytearray]:
    # Credits: kbialek
    """
    Reads multiple modbus holding registers

    Args:
        first_reg (int): The address of the first register to read
        last_reg (int): The address of the last register to read

    Returns:
        dict[int, bytearray]: Map of register values, where the register address is the map key,
        and register value is the map value

    Credits: kbialek
    """
    modbus_frame = modbus_read_request_frame(first_reg, last_reg)
    req_frame = modbus_request_frame(modbus_frame)
    resp_frame = send_request(req_frame)
    modbus_resp_frame = extract_modbus_response_frame(resp_frame)
    if modbus_resp_frame is None:
        return {}
    return modbus_read_response_to_registers(modbus_resp_frame, first_reg, last_reg)


def register_to_value(reg_bytes_list, signed, factor, offset):
    # need to reverse the bytes list because of "big" endian
    # (double register has first byte in second reg_address and second byte in first reg_address,
    # see kbialek's code in deye_sensor.py, class DoubleRegisterSensor, method read_value():
    #   low_word_reg_address = self.reg_address
    #   high_word_reg_address = self.reg_address + 1
    #   high_word + low_word # not low_word + high_word!
    # `+` concatenates the bytes, so high_word comes first (left), low_word right
    bytes_sum = b''.join(reversed(reg_bytes_list))
    return int.from_bytes(bytes_sum, "big", signed=signed) * factor + offset


def metric_data(registers, metric_row):
    reg_address_first = metric_row["Modbus first address"]
    reg_address_last = metric_row["Modbus last address"]
    relevant_reg_addresses = list(filter(
        lambda reg_address: reg_address >= reg_address_first and reg_address <= reg_address_last,
        registers
    ))
    if len(relevant_reg_addresses) == 0:
        log.error("No registers read for: %s", metric_row["Metric"])
        return ""
    reg_bytes_list = list(map(
        lambda reg_address: registers[reg_address],
        relevant_reg_addresses
    ))
    value = register_to_value(
        reg_bytes_list, metric_row["Signed"], metric_row["Factor"], metric_row["Offset"]
    )
    digits = int(-np.log10(metric_row["Factor"]))
    value = round(value, digits)
    return {
        "metric": metric_row["Metric"],
        "value": value,
        "unit": metric_row["Unit"],
        "column_name": metric_row["column_name"]
    }


def metric_data_human_readable(data):
    return f"{'{0: <25}'.format(data['metric'] + ':')} {data['value']} {data['unit']}"


# Do this outside the function so that the code is executed only once when the script is loaded:
metrics, reg_address_ranges = {}, {}
for group in groups:
    metrics[group] = all_metrics.loc[all_metrics["Group"] == group]
    reg_address_ranges[group] = find_register_address_ranges(metrics[group])


def data_of_metric_group(group):
    all_registers = {}
    time = datetime.now().isoformat()

    for addr_range in reg_address_ranges[group]:
        registers = read_registers(addr_range[0], addr_range[1])
        if registers is None:
            log.error("No registers read for range %s", addr_range)
        else:
            all_registers.update(registers)

    data = []
    for _, row in metrics[group].iterrows():
        this_data = metric_data(all_registers, row)
        data.append(this_data)

    return (time, data)


def print_data_of_metric_group(group, data):
    print(f"Values changing {group}:")
    print("---------------------")
    for this_data in data:
        print(metric_data_human_readable(this_data))
    # print()
    # print(json.dumps(data))


def data_for_psql(group):
    time, data = data_of_metric_group(group)
    psql_data = {
        "time": time
    }
    for item in data:
        try:
            psql_data[item["column_name"]] = item["value"]
        except TypeError:
            # This item of data is not a dict, but a (probably empty) string.
            # This means the whole measurement has not succeeded, so do not
            # save anything in the DB
            return None
    return psql_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="read_deye_inverter",
        description="Read modbus registers from Deye inverter via TCP packets",
        epilog="Based on https://github.com/kbialek/deye-inverter-mqtt"
    )

    parser.add_argument("metric_group", metavar="METRIC_GROUP", type=str,
                        help="String, one of [\"slow\", \"fast\", \"faster\"]")

    args = parser.parse_args()

    time, data = data_of_metric_group(args.metric_group)
    print_data_of_metric_group(args.metric_group, data)
