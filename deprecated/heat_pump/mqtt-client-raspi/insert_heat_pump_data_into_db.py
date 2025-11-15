#!/usr/bin/env python3

import os
import argparse
import configparser
import paho.mqtt.client as mqtt
import psycopg2
import json
import signal
from datetime import datetime

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


# close connection to database server when this script is terminated:
def close_connections(dry_run):
    global pg_conn

    def close(signalnum, stackframe):
        global pg_conn
        print(
            f"[{datetime.now()}] Received SIGTERM. Closing connection to database server."
        )
        if not dry_run:
            pg_conn.close()
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
    client.subscribe(cfg_heatpump["powermeter_mqtt_topic"], qos=2)

# The callback for when a PUBLISH message is received from the server.
def sample(debug, dry_run):
    
    def on_message(client, userdata, msg):
        if debug:
            print("Received MQTT message on topic:", msg.topic)
            print("Message payload:", msg.payload)
            print("Parsed message:", json.loads(msg.payload))
        
        try:
            data = json.loads(msg.payload)
            insert_into_psql(data, debug, dry_run)
        except json.decoder.JSONDecodeError:
            if debug:
                print(f"[{datetime.now()}] JSON decode error")

    return on_message


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="insert_bresser_data_into_db",
        description="""
        Insert heat pump power meter pulses read via MQTT into an SQL DB
        """,
        epilog=""
    )

    parser.add_argument('-d', '--debug', action='store_true',
                        help="Turn debug output on")
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help="Do a dry-run (i.e., don't write to DB)")

    args = parser.parse_args()

    if not args.dry_run:
        connect_to_psql()

    signal.signal(signal.SIGTERM, close_connections(args.dry_run))

    # Start the infinite sampling loop
    # i.e., connect to MQTT broker, register message handler and loop forever
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = sample(args.debug, args.dry_run)

    mqttc.connect(cfg_mqtt["host"], int(cfg_mqtt["port"]), 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    mqttc.loop_forever()