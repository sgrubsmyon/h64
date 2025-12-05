#!/usr/bin/env python3

# This script receives data from Home Assistant (the central hub for all IoT data)
# via MQTT and inserts it into a PostgreSQL database for long term storage.

import os
import argparse
import configparser
import paho.mqtt.client as mqtt
import psycopg
import json
import signal
from datetime import datetime
import pandas as pd

########################
### global variables ###
########################

# Load config file
config = configparser.ConfigParser()
basepath = os.path.dirname(os.path.abspath(__file__))
config.read(basepath + "/config.cfg")
# Convert config to pandas DataFrame
nested_list_config = [
    [ [section.name] + list(i) for i in section.items() ]
        for section in [ v for v in config.values() ]
            if len(section) > 0
]
# Flatten nested list
flat_list_config = [ item for sublist in nested_list_config for item in sublist ]
config_df = pd.DataFrame(flat_list_config, columns=["section", "key", "value"])
# Find all topics from config file (keys starting with 'mqtt_topic' in pandas DataFrame config_df)
mqtt_topics = config_df[config_df.key.str.startswith("mqtt_topic")]

cfg_mqtt = config["MQTT"]
cfg_psql = config["PostgreSQL"]

# Connection to DB that shall be persisted throughout
pg_conn = None

def connect_to_psql():
    global pg_conn
    pg_conn = psycopg.connect(
        # "host={} port={} user={} password={} dbname={}".format()
        host=cfg_psql["host"],
        port=cfg_psql["port"],
        user=cfg_psql["user"],
        dbname=cfg_psql["db"],
        password=cfg_psql["password"]
    )

# Close connection to database server when this script is terminated:
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


def insert_into_psql(table_name, data, debug, dry_run, columns=None):
    if columns is not None:
        # Filter data to only include specified columns
        data = { key: data[key] for key in columns if key in data }
    query = f'''
        INSERT INTO {table_name} ({', '.join(data.keys())})
            VALUES ({', '.join(['%s'] * len(data.values()))});
    '''
    if debug:
        print(query, data.values())
    if not dry_run:
        cur = pg_conn.cursor()
        cur.execute(query, tuple(data.values()))
        pg_conn.commit()
        cur.close()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(debug):
    def on_connect2(client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect, then subscriptions will be renewed.
        
        # Subscribe to all topics
        for _, row in mqtt_topics.iterrows():
            if debug:
                print(f"[{datetime.now()}] Subscribing to topic: {row['value']}")
            client.subscribe(row["value"], qos=2)
    return on_connect2

# The callback for when a PUBLISH message is received from the server.
def sample(debug, dry_run):
    def on_message(client, userdata, msg):
        if debug:
            print("Received MQTT message on topic:", msg.topic)
            print("Parsed message:", json.loads(msg.payload))
        try:
            # Find out table name from config file based on topic.
            # The table name is the value with the same section and the same key as
            # the topic key, only replacing 'mqtt_topic' with 'table_name'.
            cfg_row = mqtt_topics[mqtt_topics.value == msg.topic]
            section = cfg_row.section.values[0]
            key_table = cfg_row.key.values[0].replace("mqtt_topic", "table_name")
            table_name = config_df[
                (config_df.section == section) &
                (config_df.key == key_table)
            ].value.values[0]
            # The columns to insert (optional)
            key_columns = key_table.replace("table_name", "columns")
            if key_columns in config_df[config_df.section == section].key.values:
                columns_str = config_df[
                    (config_df.section == section) &
                    (config_df.key == key_columns)
                ].value.values[0]
                columns = json.loads(columns_str.replace("'", '"'))
            else:
                columns = None
            data = json.loads(msg.payload)
            insert_into_psql(table_name, data, debug, dry_run, columns)
        except json.decoder.JSONDecodeError:
            if debug:
                print(f"[{datetime.now()}] JSON decode error")
    return on_message


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="insert_data_into_db",
        description="""
        Insert IoT smart home data received via MQTT into a Postgres DB
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
    mqttc.on_connect = on_connect(args.debug)
    mqttc.on_message = sample(args.debug, args.dry_run)
    mqttc.username_pw_set(cfg_mqtt["user"], cfg_mqtt["pass"])

    # Connect to MQTT broker
    if args.debug:
        print(f"[{datetime.now()}] Connecting to MQTT broker at {cfg_mqtt['host']}:{cfg_mqtt['port']}...")
    mqttc.connect(cfg_mqtt["host"], int(cfg_mqtt["port"]), 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    mqttc.loop_forever()