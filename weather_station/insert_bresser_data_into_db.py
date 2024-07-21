#!/usr/bin/env python3

import os
import argparse
import asyncio
import configparser
from datetime import datetime
import subprocess
import json
import signal
import psycopg2
import websockets

# Code for reading data from Bresser 5-in-1 weather station via RTL-SDR antenna
# See https://www.vromans.org/johan/articles/hass_bresser51/index.html for inspiration

########################
### global variables ###
########################

# load config file

config = configparser.ConfigParser()
basepath = os.path.dirname(os.path.abspath(__file__))
config.read(basepath + "/../config.cfg")
cfg_weather = config["WeatherStation"]
cfg_psql = config["PostgreSQL"]
cfg_ws = config["WeatherStation_WebSocket"]

# connection to DB that shall be persisted throughout
pg_conn = None

# connection to WebSocket server that shall be persisted throughout
ws_conn = None

# open connection to DB
def connect_to_psql():
    global pg_conn
    pg_conn = psycopg2.connect(
        host=cfg_psql["host"],
        port=cfg_psql["port"],
        user=cfg_psql["user"],
        database=cfg_psql["db"],
        password=cfg_psql["password"]
    )


# open connection to WebSocket server
async def connect_to_websocket_server():
    global ws_conn
    uri = f"ws://{cfg_ws['host']}:{cfg_ws['port']}"
    ws_conn = await websockets.connect(uri)


# close connection to database and WebSocket server when this script is terminated:
def close_connections(dry_run):
    global pg_conn, ws_conn

    def close(signalnum, stackframe):
        global pg_conn, ws_conn
        print(
            f"[{datetime.now()}] Received SIGTERM. Closing connection to database and WebSocket server.")
        if not dry_run:
            pg_conn.close()
            # Not working:
            # await ws_conn.close()
    return close


###################
### end globals ###
###################


def insert_into_psql(data, debug, dry_run):
    query = f'''
        INSERT INTO weather_station_metrics
            VALUES ({', '.join(['%s'] * len(data.values()))});
    '''
    if debug:
        print(query, data.values())
    if not dry_run:
        cur = pg_conn.cursor()
        cur.execute(query, tuple(data.values()))
        pg_conn.commit()
        cur.close()


async def send_to_websocket_server(data, status, debug):
    global ws_conn
    msg = {
        "token": cfg_ws["send_token"],
        "values": data,
        "status": status
    }
    if debug:
        print("Sending msg to server:", json.dumps(msg))
    try:
        await ws_conn.send(json.dumps(msg))
    except websockets.exceptions.ConnectionClosedError:
        # Connection was closed, reopen it
        print(f"[{datetime.now()}] Reopening closed WS connection.")
        status = {"type": "WARN",
                  "msg": "Had to reopen closed WebSocket connection"}
        try:
            await connect_to_websocket_server()
            await send_to_websocket_server(data, status, debug)
        except (ConnectionRefusedError, OSError):
            print(
                f"[{datetime.now()}] WebSocket server is down. Not sending data. Trying again later.")
            ws_conn = None


def isoformat(dt):
    # convert from format '2024-07-20 14:44:52' to isoformat '2024-07-21T11:53:18'
    return dt[0:10] + "T" + dt[11:]

async def sample(debug, dry_run):
    command_array = [
        cfg_weather["command"],
        cfg_weather["frequency_opt"], cfg_weather["frequency"],
        cfg_weather["format_opt"], cfg_weather["format"]
    ]
    
    if (cfg_weather["other_options"]):
        command_array += cfg_weather["other_options"].split(" ")
    
    if debug:
        print("Running command array:", command_array)

    proc = subprocess.Popen(
        command_array,
        stdout=subprocess.PIPE)

    while True: # infinite sampling loop
        line = proc.stdout.readline().decode("utf-8")
        if not line:
            break
        try:
            ljson = json.loads(line)
            if debug:
                print("    => JSON:", ljson)
            if not dry_run:
                data = json.loads(line)

                # check if this message comes from the weather station with the correct ID (configured in config.cfg)
                # otherwise ignore it
                if data["id"] != cfg_weather["id"]:
                    if debug:
                        print(("    => Ignoring message from unknown weather station with ID {data_id}, " +
                              "differing from the configured ID {conf_id}.").format(data_id = data["id"], conf_id = cfg_weather["id"]))
                    continue

                # Prepare the data for the DB
                psql_data = {
                    "time": isoformat(data["time"]),
                    "location": cfg_weather["location"],
                    "id": data["id"],
                    "battery_ok": data["battery_ok"],
                    "temperature_C": data["temperature_C"],
                    "humidity": data["humidity"],
                    "wind_max_m_s": data["wind_max_m_s"],
                    "wind_avg_m_s": data["wind_avg_m_s"],
                    "wind_dir_deg": data["wind_dir_deg"],
                    "rain_mm": data["rain_mm"],
                }

                insert_into_psql(psql_data, debug, dry_run)
                status = {"type": "OK", "msg": "OK"}
                await send_to_websocket_server(data, status, debug)
        except json.decoder.JSONDecodeError:
            if debug:
                print(line)
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="insert_bresser_data_into_db",
        description="""
        Insert Bresser 5-in-1 weather station data read with shell command `rtl_433`
        into an SQL DB and also send it to WebSocket server `inverter_websocket_server.js`
        """,
        epilog=""
    )

    parser.add_argument('-d', '--debug', action='store_true',
                        help="Turn debug output on")
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help="Turn debug output on")

    args = parser.parse_args()

    if not args.dry_run:
        connect_to_psql()

    signal.signal(signal.SIGTERM, close_connections(args.dry_run))

    # Start the infinite sampling loop
    asyncio.run(sample(args.debug, args.dry_run))