#!/usr/bin/env python3

import os
import argparse
import asyncio
import configparser
import paho.mqtt.client as mqtt
import psycopg2
import websockets
import json
import signal
import datetime

# Code for reading data from heat pump power meter via MQTT

########################
### global variables ###
########################

# load config file

config = configparser.ConfigParser()
basepath = os.path.dirname(os.path.abspath(__file__))
config.read(basepath + "/../../config.cfg")
cfg_mqtt = config["MQTT"]
cfg_heatpump = config["HeatPump"]
cfg_psql = config["PostgreSQL"]
cfg_ws = config["HeatPump_WebSocket"]

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
            f"[{datetime.now()}] Received SIGTERM. Closing connection to database and WebSocket server."
        )
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
        INSERT INTO heat_pump_metrics_electric_power_pulse
            VALUES ('{data["time"]}');
    '''
    if debug:
        print("Query: ", query, ", Values: ", data.values())
    if not dry_run:
        cur = pg_conn.cursor()
        cur.execute(query, tuple(data.values()))
        pg_conn.commit()
        cur.close()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/home/heat_pump/electric_power_pulse")

# The callback for when a PUBLISH message is received from the server.
def sample(debug, dry_run):
    
    async def on_message(client, userdata, msg):
        global ws_conn

        if debug:
            print("Received MQTT message:", msg.topic+" "+str(msg.payload))
        
        if ws_conn == None:
            try: # to reconnect
                await connect_to_websocket_server()
            except (ConnectionRefusedError, OSError):
                print(
                    f"[{datetime.now()}] WebSocket server is down. Not sending data. Trying again later."
                )
                ws_conn = None

        status = {"type": "NORMAL", "msg": ""}

        try:
            data = json.loads(msg.payload)
            insert_into_psql(data, debug, dry_run)
        except json.decoder.JSONDecodeError:
            status = {"type": "ERROR", "msg": f"[{datetime.now()}] JSON decode error"}
        if ws_conn != None:
            await send_to_websocket_server(data, status, debug)

    return on_message


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
                f"[{datetime.now()}] WebSocket server is down. Not sending data. Trying again later."
            )
            ws_conn = None


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
    # i.e., connect to MQTT broker, register message handler and loop forever
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = sample(args.debug, args.dry_run)

    mqttc.connect("192.168.178.100", 1883, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    mqttc.loop_forever()