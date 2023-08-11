#!/usr/bin/env python3

import asyncio
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

### global variables ###

CONNECTIONS = set()
CURR_VALUES = {}

### end global variables ###


async def on_connect(conn):
    CONNECTIONS.add(conn)
    print(f"New connection ({conn.id})! Number of open connections: {len(CONNECTIONS)}")
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
            # await on_message(conn, message)
            on_message(conn, message)
    finally:
        on_close(conn)


# async def on_message(conn, message):
def on_message(conn, message):
    msg = json.loads(message)
    print("Message from", conn, ":", msg)
    if "group" in msg and "values" in msg:
        # Update the current values with new ones:
        group = msg["group"]
        CURR_VALUES[group] = msg["values"]
    # Broadcast the new current values to all connected clients
    websockets.broadcast(CONNECTIONS, json.dumps(CURR_VALUES))


def on_close(conn):
    CONNECTIONS.remove(conn)
    print(f"Connection ({conn.id}) closed. Number of open connections: {len(CONNECTIONS)}")


async def main():
    async with websockets.serve(on_connect, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())


# curr_values[next_sampling_group] = data
# print(curr_values)
