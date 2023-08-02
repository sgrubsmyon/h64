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
inverter_sn = int(config["inverter_sn"])
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
    inverter_sn = bytearray.fromhex("{:10x}".format(self.config.serial_number))
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


# Source: https://github.com/jlopez77/DeyeInverter/blob/main/InverterData.py

# import binascii
# import re
# import json
# # import paho.mqtt.client as paho

# def twosComplement_hex(hexval):
#     bits = 16
#     val = int(hexval, bits)
#     if val & (1 << (bits-1)):
#         val -= 1 << bits
#     return val

# # LOAD DEYE INVERTER REGISTERS

# with open("./deye_registers.json") as txtfile:
#     parameters = json.loads(txtfile.read())

# # PREPARE & SEND DATA TO THE INVERTER

# output = "{"  # initialise json output
# pini = 59
# pfin = 112
# chunks = 0
# while chunks < 2:
#     if chunks == -1:  # testing initialisation
#         pini = 235
#         pfin = 235
#         print("Initialise Connection")
#     start = binascii.unhexlify('A5')  # start
#     length = binascii.unhexlify('1700')  # datalength
#     controlcode = binascii.unhexlify('1045')  # controlCode
#     serial = binascii.unhexlify('0000')  # serial
#     # com.igen.localmode.dy.instruction.send.SendDataField
#     datafield = binascii.unhexlify('020000000000000000000000000000')
#     pos_ini = str(hex(pini)[2:4].zfill(4))
#     pos_fin = str(hex(pfin - pini + 1)[2:4].zfill(4))
#     businessfield = binascii.unhexlify(
#         '0103' + pos_ini + pos_fin)  # sin CRC16MODBUS
#     crc = binascii.unhexlify(str(hex(libscrc.modbus(businessfield))[
#                              4:6])+str(hex(libscrc.modbus(businessfield))[2:4]))  # CRC16modbus
#     checksum = binascii.unhexlify('00')  # checksum F2
#     endCode = binascii.unhexlify('15')

#     inverter_sn2 = bytearray.fromhex(hex(inverter_sn)[
#                                      8:10] + hex(inverter_sn)[6:8] + hex(inverter_sn)[4:6] + hex(inverter_sn)[2:4])
#     frame = bytearray(start + length + controlcode + serial +
#                       inverter_sn2 + datafield + businessfield + crc + checksum + endCode)

#     checksum = 0
#     frame_bytes = bytearray(frame)
#     for i in range(1, len(frame_bytes) - 2, 1):
#         checksum += frame_bytes[i] & 255
#     frame_bytes[len(frame_bytes) - 2] = int((checksum & 255))

#    # OPEN SOCKET

#     for res in socket.getaddrinfo(inverter_ip, inverter_port, socket.AF_INET, socket.SOCK_STREAM):
#         family, socktype, proto, canonname, sockadress = res
#         try:
#             clientSocket = socket.socket(family, socktype, proto)
#             clientSocket.settimeout(10)
#             clientSocket.connect(sockadress)
#         except socket.error as msg:
#             print("Could not open socket")
#             break

#     # SEND DATA
#     # print(chunks)
#     clientSocket.sendall(frame_bytes)

#     ok = False
#     while (not ok):
#         try:
#             data = clientSocket.recv(1024)
#             ok = True
#             try:
#                 print("data:")
#                 print(data)
#             except:
#                 print("No data - Die")
#                 sys.exit(1)  # die, no data
#         except socket.timeout as msg:
#             print("Connection timeout")
#             sys.exit(1)  # die

#     # PARSE RESPONSE (start position 56, end position 60)
#     totalpower = 0
#     i = pfin - pini
#     a = 0
#     while a <= i:
#         # why start at 56?
#         p1 = 56 + (a * 4)
#         p2 = 60 + (a * 4)
#         # p1 = 0 + (a * 4)
#         # p2 = 4 + (a * 4)
#         hexstring = str("".join(hex(ord(chr(x)))[2:].zfill(
#             2) for x in bytearray(data))+'  '+re.sub('[^\x20-\x7f]', '', ''))
#         hexval = hexstring[p1:p2]
#         print(hexstring, p1, p2)
#         # example hexstring: a5100010150013034221a50201704713003f010000be1a9f6406004115
#         print("a:", a, "  hexval:", hexval)
#         if hexval != "":
#             response = twosComplement_hex(hexval)
#             hexpos = str("0x") + str(hex(a + pini)[2:].zfill(4)).upper()
#             print("hexpos:", hexpos)
#             for parameter in parameters:
#                 for item in parameter["items"]:
#                     title = item["titleEN"]
#                     ratio = item["ratio"]
#                     unit = item["unit"]
#                     for register in item["registers"]:
#                         if register == hexpos and chunks != -1:
#                             print(hexpos+"-"+title+":" +
#                                   str(response*ratio)+unit)
#                             if title.find("Temperature") != -1:
#                                 response = round(response * ratio - 100, 2)
#                             else:
#                                 response = round(response * ratio, 2)
#                             output = output + "\"" + title + \
#                                 "(" + unit + ")" + "\":" + str(response)+","
#                             if hexpos == '0x00BA':
#                                 totalpower += response * ratio
#                             if hexpos == '0x00BB':
#                                 totalpower += response * ratio
#         a += 1
#     pini = 150
#     pfin = 195
#     chunks += 1
# output = output[:-1]+"}"

# print("output:", output)
