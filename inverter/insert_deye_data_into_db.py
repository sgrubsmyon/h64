#!/usr/bin/env python3

import argparse
import configparser
from datetime import datetime
import json
import os
import sys
import signal
import time
import numpy as np
import psycopg2
import asyncio
import websockets
from read_deye_inverter import data_for_psql

# so that files like config.cfg are always found, no matter from where the script is being run
os.chdir(os.path.dirname(sys.argv[0]))

########################
### global variables ###
########################

# load config file

config = configparser.ConfigParser()
config.read("../config.cfg")
cfg_deye = config["DeyeInverter"]
cfg_psql = config["PostgreSQL"]
cfg_ws = config["WebSocket"]

start_point = {
    # 0 minutes, 0 seconds
    "faster": (float(cfg_deye["sampling_start_point_faster_minute"]), float(cfg_deye["sampling_start_point_faster_second"])),
    # 0 minutes, 4.5 seconds
    "fast": (float(cfg_deye["sampling_start_point_fast_minute"]), float(cfg_deye["sampling_start_point_fast_second"])),
    # 0 minutes, 1.5 seconds
    "slow": (float(cfg_deye["sampling_start_point_slow_minute"]), float(cfg_deye["sampling_start_point_slow_second"]))
}

interval = {
    # 3 seconds
    "faster": (float(cfg_deye["sampling_interval_faster_minute"]), float(cfg_deye["sampling_interval_faster_second"])),
    # 15 seconds
    "fast": (float(cfg_deye["sampling_interval_fast_minute"]), float(cfg_deye["sampling_interval_fast_second"])),
    # 5 minutes, 0 seconds
    "slow": (float(cfg_deye["sampling_interval_slow_minute"]), float(cfg_deye["sampling_interval_slow_second"]))
}

# slow sampling is privileged: if it would be skipped because
# previous sampling took too much time, it is done nevertheless
minute_of_last_slow_sampling = -999.0

sampling_points = {}  # sampling points are in minutes (within any one hour)
for group in start_point:
    minute_startpoint = start_point[group][0] + start_point[group][1] / 60
    minute_interval = interval[group][0] + interval[group][1] / 60
    sampling_points[group] = np.arange(
        minute_startpoint, 60, minute_interval)

# create connection to DB that shall be persisted throughout
conn = psycopg2.connect(
    host=cfg_psql["host"],
    port=cfg_psql["port"],
    user=cfg_psql["user"],
    database=cfg_psql["db"],
    password=cfg_psql["password"]
)
cur = conn.cursor()


# create connection to WebSocket server that shall be persisted throughout
ws_conn = None


async def connect_to_websocket_server():
    global ws_conn
    uri = f"ws://{cfg_ws['host']}:{cfg_ws['port']}"
    ws_conn = await websockets.connect(uri)


# close connection to database and WebSocket server when this script is terminated:
def close_connections():
    print("Received SIGTERM. Closing connection to database and WebSocket server.")
    cur.close()
    conn.close()
    ws_conn.close()


signal.signal(signal.SIGTERM, close_connections)

###################
### end globals ###
###################


def insert_into_psql(group, data, debug):
    query = f'''
        INSERT INTO metrics_{group}({', '.join(data.keys())})
            VALUES ({', '.join(['%s'] * len(data.values()))});
    '''
    if debug:
        print(query, data.values())
    cur.execute(query, tuple(data.values()))
    conn.commit()


async def send_to_websocket_server(group, data, debug):
    global ws_conn
    msg = {
        "group": group,
        "values": data
    }
    if debug:
        print("Sending msg to server:", json.dumps(msg))
    try:
        await ws_conn.send(json.dumps(msg))
    except websockets.exceptions.ConnectionClosedError:
        # Connection was closed, reopen it
        print("Reopening closed WS connection.")
        try:
            await connect_to_websocket_server()
            await send_to_websocket_server(group, data, debug)
        except (ConnectionRefusedError, OSError):
            print("WebSocket server is down. Not sending data. Trying again later.")
            ws_conn = None


async def sample(minute_of_last_slow_sampling, debug):
    global ws_conn
    if ws_conn == None:
        try:
            await connect_to_websocket_server()
        except (ConnectionRefusedError, OSError):
            print("WebSocket server is down. Not sending data. Trying again later.")
            ws_conn = None

    now = datetime.now()
    now_minute = now.minute + now.second / 60 + now.microsecond * 1e-6 / 60

    if (now_minute - minute_of_last_slow_sampling) > (interval["slow"][0] + interval["slow"][1] / 60):
        # Last slow sampling is too much in the past,
        # do it right now!
        print("Slow sampling was skipped, is now done before others.")
        next_sampling_group = "slow"
        next_sampling_delta_t = 0
    else:
        closest_sampling_point = {}
        for group in sampling_points:
            delta_ts = sampling_points[group] - now_minute
            # Remove sampling points of the past (negative time difference delta_t)
            delta_ts = delta_ts[delta_ts > 0]
            # Find next upcoming sampling point (closest in time in the future)
            delta_t = np.min(delta_ts)
            closest_sampling_point[group] = delta_t
        # Find which metric group has the smallest delta_t
        next_sampling_group = min(closest_sampling_point,
                                  key=closest_sampling_point.get)
        # Minutes until next sampling:
        next_sampling_delta_t = closest_sampling_point[next_sampling_group]

    # Wait until the next sampling point is due
    # time.sleep() takes seconds as parameter
    time.sleep(next_sampling_delta_t * 60)

    now = datetime.now()
    now_minute = now.minute + now.second / 60 + now.microsecond * 1e-6 / 60
    if next_sampling_group == "slow":
        minute_of_last_slow_sampling = now_minute

    data = data_for_psql(next_sampling_group)
    insert_into_psql(next_sampling_group, data, debug)
    if ws_conn != None:
        await send_to_websocket_server(next_sampling_group, data, debug)

    # Repeat the same process
    await sample(minute_of_last_slow_sampling, debug)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="insert_deye_data_into_db",
        description="""
        Insert Deye inverter data read with `read_deye_inverter.py`
        into an SQL DB and also send it to WebSocket server `inverter_websocket_server.py`
        """,
        epilog=""
    )

    parser.add_argument('-d', '--debug', action='store_true',
                        help="Turn debug output on")

    args = parser.parse_args()

    # Start the infinite sampling loop
    asyncio.run(sample(minute_of_last_slow_sampling, args.debug))