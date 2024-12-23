// See ./README.md for instructions on how to run this benchmark.
// const CLIENTS_TO_WAIT_FOR = parseInt(process.env.CLIENTS_COUNT || "", 10) || 32;
// var remainingClients = CLIENTS_TO_WAIT_FOR;
// const COMPRESS = process.env.COMPRESS === "1";

import { parse } from "ini";
import mqtt from "mqtt";

/********************
 * Global variables *
 ********************/

const configfile = Bun.file(`${import.meta.dir}/../../config.cfg`);
const configtext = await configfile.text();
const CONFIGFULL = parse(configtext);
const CONFIG_WS = CONFIGFULL.HeatPump_WebSocket;
const CONFIG_MQTT = CONFIGFULL.MQTT;

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
var CURR_STATUS = "Waiting for 1st pulse";
var CURR_TIMESTAMP_1 = null;
var CURR_TIMESTAMP_2 = null;
var CURR_POWER = NaN;

/***************
 * End globals *
 ***************/

const server = Bun.serve({
  hostname: CONFIG_WS.host,
  port: CONFIG_WS.port,

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
      ws.subscribe("heat_pump");

      // Send the current values only back to the freshly connected client
      ws.send(JSON.stringify({
        status: CURR_STATUS,
        timestamp1: CURR_TIMESTAMP_1,
        timestamp2: CURR_TIMESTAMP_2,
        power: CURR_POWER
      }));
    },

    // // Now wait for an MQTT message with a power meter pulse
    // message(ws, message) {
    //   const msg = JSON.parse(message);
    //   if (DEBUG) {
    //     console.log(`[${new Date().toISOString()}] Received message:`, msg);
    //   }
    //   const msg_keys = Object.keys(msg);
    //   if (!msg_keys.includes("token") && msg.token !== CONFIG.send_token) {
    //     // ignore message
    //     return;
    //   }
    //   if (msg_keys.includes("values") && msg.values !== null) {
    //     // Update the current values with new ones:
    //     for (const [key, value] of Object.entries(msg.values)) {
    //       // if the value is valid, adopt it as new value
    //       if (value !== null && value !== undefined) {
    //         CURR_VALUES[key] = value;
    //       }
    //     }
    //   }
    //   if (msg_keys.includes("status")) {
    //     CURR_STATUS = msg.status;
    //   }

    //   const broadcast_msg = JSON.stringify({
    //     values: CURR_VALUES,
    //     status: CURR_STATUS
    //   });
    //   if (DEBUG) {
    //     console.log(`[${new Date().toISOString()}] Broadcasting message to connected clients:`, broadcast_msg);
    //   }
    //   // Broadcast the new current values to all connected clients
    //   if (ws.publish("heat_pump", broadcast_msg) !== broadcast_msg.length) {
    //     throw new Error("Failed to publish message");
    //   }
    // },

    close(ws) {
      N_CONN_CLIENTS--;
      if (DEBUG) {
        console.log(`Disconnected, now ${N_CONN_CLIENTS} open connection${N_CONN_CLIENTS == 1 ? "" : "s"}`);
      }
    },

    perMessageDeflate: CONFIG_WS.compress === "true" ? true : false,
    publishToSelf: true, // what does this mean?
  },

});

console.log(`Waiting for clients to connect...\n`, `  http://${server.hostname}:${server.port}/`);

// Connect to MQTT broker (https://www.emqx.com/en/blog/how-to-use-mqtt-in-nodejs)
const mqtt_connect_url = `mqtt://${CONFIG_MQTT.host}:${CONFIG_MQTT.port}`;
const client_id = `mqtt_${Math.random().toString(16).slice(3)}`;

const client = mqtt.connect(mqtt_connect_url, {
  client_id,
  clean: true,
  connectTimeout: 4000,
  // username: 'emqx',
  // password: 'public',
  reconnectPeriod: 1000,
});

client.on('connect', () => {
  console.log('Connected to MQTT broker');
  client.subscribe([CONFIG_MQTT.powermeter_mqtt_topic], () => {
    console.log(`Subscribed to topic '${CONFIG_MQTT.powermeter_mqtt_topic}'`);
  });
});

// Now wait for an MQTT message from the client
client.on('message', (topic, payload) => {
  console.log('Received Message:', topic, payload.toString());
});