#!/usr/bin/env python3

import logging
import sys
import socket
import libscrc
import os
import configparser
import argparse

# Based on: https://github.com/kbialek/deye-inverter-mqtt

# so that files like config.cfg are always found, no matter from where the script is being run
os.chdir(os.path.dirname(sys.argv[0]))

# CONFIG

config = configparser.ConfigParser()
config.read("config.cfg")
config = config["DeyeInverter"]

inverter_ip = config["inverter_ip"]
inverter_port = int(config["inverter_port"])
inverter_serialnumber = int(config["inverter_serialnumber"])
installed_power = int(config["installed_power"])  # in full Watts (as integer)

# END CONFIG

log = logging.getLogger("DeyeInverter")


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
    inverter_sn = bytearray.fromhex("{:10x}".format(inverter_serialnumber))
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
            (inverter_ip, inverter_port), timeout=10
        )
        # if not self.__reachable:
        #     self.__reachable = True
        #     log.info("Re-connected to socket on IP %s",
        #                     inverter_ip)
    except OSError as e:
        # if self.__reachable:
        #     log.warning(
        #         "Could not open socket on IP %s: %s", inverter_ip, e)
        # else:
        log.error("Could not open socket on IP %s: %s",
                  inverter_ip, e)
        # self.__reachable = False
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
                      inverter_ip, e)
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


def parse_modbus_read_response(frame: bytes, first_reg: int, last_reg: int) -> dict[int, bytearray]:
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
    return parse_modbus_read_response(modbus_resp_frame, first_reg, last_reg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="read_deye_inverter",
        description="Read modbus registers from Deye inverter via TCP packets",
        epilog="Based on https://github.com/kbialek/deye-inverter-mqtt"
    )

    parser.add_argument('first_reg', metavar='FIRST_REG', type=int,
                        help='Integer number of first register to read, e.g. 625')
    parser.add_argument('last_reg', metavar='LAST_REG', type=int,
                        help='Integer number of last register to read, e.g. 625')

    args = parser.parse_args()

    registers = read_registers(args.first_reg, args.last_reg)

    if registers is None:
        print("Error: no registers read")
        sys.exit(1)
    for reg_address in registers:
        reg_bytes = registers[reg_address]
        reg_value_int = int.from_bytes(reg_bytes, "big")
        low_byte = reg_bytes[1]
        high_byte = reg_bytes[0]
        print(
            f"Register {reg_address}:   int: {reg_value_int}, l: {low_byte}, h: {high_byte}"
        )
        # Verified that it works: (run from deye-inverter-mqtt repo)
        #   $ sudo docker run --rm --env-file config.env ghcr.io/kbialek/deye-inverter-mqtt r 625; ../../read_deye_inverter.py 625 625
        # Both commands return the same values
