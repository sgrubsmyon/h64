#!/usr/bin/env python3

import argparse
import asyncio
import configparser
import os
import sys
import websockets
import json

# JS:
'''
var conn = new WebSocket('ws://localhost:8765');
conn.onopen = function(e) {
    console.log("Connection established!");
};
conn.onmessage = function(e) {
    console.log(e.data);
};
conn.send(JSON.stringify({a: 1, b: 2, c: 5}))
conn.send(JSON.stringify({group: "slow", values: {a: 1, b: 2, c: 5}}))
'''

# so that files like config.cfg are always found, no matter from where the script is being run
os.chdir(os.path.dirname(sys.argv[0]))

########################
### global variables ###
########################

CONNECTIONS = set()
CURR_VALUES = {}

CONFIG = configparser.ConfigParser()
CONFIG.read("../config.cfg")
CONFIG = CONFIG["WebSocket"]

###################
### end globals ###
###################


def on_connect_closure(debug):
    async def on_connect(conn):
        CONNECTIONS.add(conn)
        print(
            f"New connection ({conn.id})! Number of open connections: {len(CONNECTIONS)}")
        try:
            # Send the current values to the freshly connected client:
            await conn.send(json.dumps(CURR_VALUES))
            # Now wait for a message from the client.
            # There is only one client that is supposed to ever
            # send messages and this is the Python script
            # querying the inverter and putting the values
            # into the database. It sends messages with
            # the fresh values to this WebSocket server.
            # All other clients (in web browser) only passively
            # receive the messages with current values and do
            # not send any messages.
            async for message in conn:
                await on_message(conn, message, debug)
                # on_message(conn, message, debug)
        except websockets.exceptions.ConnectionClosedError:
            # do not complain
            pass
        finally:
            await on_close(conn)
    return on_connect


async def on_message(conn, message, debug):
    # def on_message(conn, message, debug):
    msg = json.loads(message)
    if debug:
        print("Message from", conn, ":", msg)
    if "group" in msg and "values" in msg:
        # Update the current values with new ones:
        group = msg["group"]
        CURR_VALUES[group] = msg["values"]
    # Broadcast the new current values to all connected clients
    websockets.broadcast(CONNECTIONS, json.dumps(CURR_VALUES))


async def on_close(conn):
    CONNECTIONS.remove(conn)
    print(
        f"Connection ({conn.id}) closed. Number of open connections: {len(CONNECTIONS)}")


async def main(debug):
    async with websockets.serve(on_connect_closure(debug), CONFIG["host"], CONFIG["port"]):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="inverter_websocket_server",
        description="""
        WebSocket server providing live data from invert, read via `read_deye_inverter.py`,
        sent to this WebSocket server by `insert_deye_data_into_db.py`
        """,
        epilog=""
    )

    parser.add_argument('-d', '--debug', action='store_true',
                        help="Turn debug output on")

    args = parser.parse_args()

    asyncio.run(main(args.debug))
