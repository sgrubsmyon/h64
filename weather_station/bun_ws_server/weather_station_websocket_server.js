// See ./README.md for instructions on how to run this benchmark.
// const CLIENTS_TO_WAIT_FOR = parseInt(process.env.CLIENTS_COUNT || "", 10) || 32;
// var remainingClients = CLIENTS_TO_WAIT_FOR;
// const COMPRESS = process.env.COMPRESS === "1";

import { parse } from "ini";

/********************
 * Global variables *
 ********************/

const configfile = Bun.file(`${import.meta.dir}/../../config.cfg`);
const configtext = await configfile.text();
const CONFIGFULL = parse(configtext);
const CONFIG = CONFIGFULL.WeatherStation_WebSocket;

var DEBUG = false;
process.argv.forEach(arg => {
  if (arg === "-d" || arg === "--debug") {
    DEBUG = true;
  }
});
if (DEBUG) {
  console.log("DEBUG:", DEBUG);
}

var CLIENT_AUTOINCREMENT = 0;
var N_CONN_CLIENTS = 0;
var CURR_VALUES = {};
var CURR_STATUS = {};

/***************
 * End globals *
 ***************/

const server = Bun.serve({
  hostname: CONFIG.host,
  port: CONFIG.port,

  // Protocol upgrade logic
  fetch(req, server) {
    const success = server.upgrade(req);
    if (success) {
      // Bun automatically returns a 101 Switching Protocols
      // if the upgrade succeeds
      return undefined;
    }
    // handle HTTP request normally
    return new Response(
      "Error switching protocols for connection to WebSocket server",
      { status: 500 });
  },

  // Websocket handlers:
  websocket: {
    open(ws) {
      CLIENT_AUTOINCREMENT++;
      N_CONN_CLIENTS++;
      if (DEBUG) {
        console.log(`[${new Date().toISOString()}] New connection (${CLIENT_AUTOINCREMENT}), now ${N_CONN_CLIENTS} open connection${N_CONN_CLIENTS == 1 ? "" : "s"}`);
      }
      ws.subscribe("weather_station");

      // Send the current values only back to the freshly connected client
      ws.send(JSON.stringify({
        values: CURR_VALUES,
        status: CURR_STATUS
      }));
    },

    // Now wait for a message from the client.
    // There is only one client that is supposed to ever
    // send messages and this is the Python script
    // receiving weather station data via RTL-SDR and putting
    // the values into the database. It sends messages with
    // the fresh values to this WebSocket server.
    // All other clients (in web browser) only passively
    // receive the messages with current values and do
    // not send any messages.
    message(ws, message) {
      const msg = JSON.parse(message);
      if (DEBUG) {
        console.log(`[${new Date().toISOString()}] Received message:`, msg);
      }
      const msg_keys = Object.keys(msg);
      if (!msg_keys.includes("token") && msg.token !== CONFIG.send_token) {
        // ignore message
        return;
      }
      if (msg_keys.includes("values") && msg.values !== null) {
        console.log("Message:", msg);
        console.log("Message values:", msg.values);
        // Update the current values with new ones:
        for (const [key, value] of msg.values) {
          console.log("Message key:", key);
          console.log("Message value:", value);
          // if the value is valid, adopt it as new value
          if (value !== null && value !== undefined) {
            CURR_VALUES[key] = value;
          }
        }
      }
      if (msg_keys.includes("status")) {
        CURR_STATUS = msg.status;
      }

      const broadcast_msg = JSON.stringify({
        values: CURR_VALUES,
        status: CURR_STATUS
      });
      if (DEBUG) {
        console.log(`[${new Date().toISOString()}] Broadcasting message to connected clients:`, broadcast_msg);
      }
      // Broadcast the new current values to all connected clients
      if (ws.publish("weather_station", broadcast_msg) !== broadcast_msg.length) {
        throw new Error("Failed to publish message");
      }
    },

    close(ws) {
      N_CONN_CLIENTS--;
      if (DEBUG) {
        console.log(`Disconnected, now ${N_CONN_CLIENTS} open connection${N_CONN_CLIENTS == 1 ? "" : "s"}`);
      }
    },

    perMessageDeflate: CONFIG.compress === "true" ? true : false,
    publishToSelf: true, // what does this mean?
  },

});

console.log(`Waiting for clients to connect...\n`, `  http://${server.hostname}:${server.port}/`);
