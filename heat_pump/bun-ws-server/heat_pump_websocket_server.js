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
const CONFIG_HEATPUMP = CONFIGFULL.HeatPump;

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
var POOL = {}; // pool of active WebSocket client connections
var CURR_STATUS = "Waiting for 1st pulse";
var CURR_VALUES_1 = null;
var CURR_VALUES_2 = null;
var CURR_POWER = NaN;

/***************
 * End globals *
 ***************/

/**
 * Converts a date string with microseconds into a number of seconds since epoch with microseconds precision.
 *
 * @param {string} datestring - The date string in the format "YYYY-MM-DDTHH:MM:SS.ssssss" 
 *                              where "ssssss" represents microseconds.
 * @returns {number} - The timestamp in microseconds precision.
 */
function getMicroTime(datestring) {
  const date = new Date(datestring + "Z"); // Z for UTC
  const epoch = date.getTime(); // is in milliseconds
  const micros = datestring.substring(23); // get the microseconds
  const micro_timestring = epoch.toString() + "." + micros;
  return parseFloat(micro_timestring) / 1000; // now in seconds
}

function updatePower() {
  if (CURR_VALUES_1 === null || CURR_VALUES_2 === null) {
    CURR_POWER = NaN;
  } else {
    const time1 = getMicroTime(CURR_VALUES_1.time);
    const time2 = getMicroTime(CURR_VALUES_2.time);
    const timediff = time2 - time1;
    // one pulse every 0.001 kWh or 1000 pulses per kWh
    // => from one pulse to another, the energy difference is 0.001 kWh or 1 Wh or 1 W * 3600 seconds
    // => we have: power * timediff = 3600 Ws => power = 3600 Ws / timediff
    CURR_POWER = 3600 / timediff;
  }
}

// Connect to MQTT broker (https://www.emqx.com/en/blog/how-to-use-mqtt-in-nodejs, https://www.npmjs.com/package/mqtt#example)
const mqtt_connect_url = `mqtt://${CONFIG_MQTT.host}:${CONFIG_MQTT.port}`;
const client_id = `mqtt_${Math.random().toString(16).slice(3)}`;

const MQTT_CLIENT = mqtt.connect(mqtt_connect_url, {
  client_id,
  clean: true,
  connectTimeout: 4000,
  // username: 'emqx',
  // password: 'public',
  reconnectPeriod: 1000,
});

MQTT_CLIENT.on("connect", () => {
  console.log("Connected to MQTT broker");
  console.log("Will now subscribe to topic:", CONFIG_HEATPUMP.powermeter_mqtt_topic);
  MQTT_CLIENT.subscribe(CONFIG_HEATPUMP.powermeter_mqtt_topic, (err) => {
    if (!err) {
      console.log(`Subscribed to topic '${CONFIG_HEATPUMP.powermeter_mqtt_topic}'`);
    }
  });
});

const server = Bun.serve({
  hostname: CONFIG_WS.host,
  port: CONFIG_WS.port,

  // Protocol upgrade logic
  fetch(req, server) {
    const success = server.upgrade(req, {
      data: {
        socket_id: Math.random(),
      },
    });
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
      console.log(ws);
      POOL[ws.data.socket_id] = ws;
      console.log("POOL:", POOL);
      if (DEBUG) {
        console.log(`[${new Date().toISOString()}] New connection (${CLIENT_AUTOINCREMENT}), now ${N_CONN_CLIENTS} open connection${N_CONN_CLIENTS == 1 ? "" : "s"}`);
      }
      ws.subscribe("heat_pump");

      // Send the current values only back to the freshly connected client
      ws.send(JSON.stringify({
        status: CURR_STATUS,
        values: {
          values1: CURR_VALUES_1,
          values2: CURR_VALUES_2,
          power: CURR_POWER
        }
      }));

      // Now wait for an MQTT message from the MQTT_CLIENT
      MQTT_CLIENT.on("message", (topic, payload) => {
        const msg = JSON.parse(payload.toString());
        if (DEBUG) {
          console.log(`[${new Date().toISOString()}] Received message on topic '${topic}':`, msg);
        }
        // const msg_keys = Object.keys(msg);
        // if (!msg_keys.includes("token") && msg.token !== CONFIG.send_token) {
        //   // ignore message
        //   return;
        // }
        // if (msg_keys.includes("values") && msg.values !== null) {
        //   // Update the current values with new ones:
        //   for (const [key, value] of Object.entries(msg.values)) {
        //     // if the value is valid, adopt it as new value
        //     if (value !== null && value !== undefined) {
        //       CURR_VALUES[key] = value;
        //     }
        //   }
        // }
        if (CURR_VALUES_1 === null) {
          CURR_VALUES_1 = msg;
          CURR_STATUS = "Waiting for 2nd pulse";
        } else if (CURR_VALUES_2 === null) {
          CURR_VALUES_2 = msg;
          CURR_STATUS = "OK";
          updatePower();
        } else {
          CURR_VALUES_1 = CURR_VALUES_2;
          CURR_VALUES_2 = msg;
          CURR_STATUS = "OK";
          updatePower();
        }

        const broadcast_msg = JSON.stringify({
          status: CURR_STATUS,
          values: {
            values1: CURR_VALUES_1,
            values2: CURR_VALUES_2,
            power: CURR_POWER
          }
        });
        if (DEBUG) {
          console.log(`[${new Date().toISOString()}] Broadcasting message to connected clients:`, broadcast_msg);
        }
        // Broadcast the new current values to all connected clients
        if (server.publish("heat_pump", broadcast_msg) !== broadcast_msg.length) {
          throw new Error("Failed to publish message");
        }
      });
    },

    close(ws) {
      N_CONN_CLIENTS--;
      POOL[ws.data.socket_id] = null;
      if (DEBUG) {
        console.log(`Disconnected, now ${N_CONN_CLIENTS} open connection${N_CONN_CLIENTS == 1 ? "" : "s"}`);
      }
    },

    perMessageDeflate: CONFIG_WS.compress === "true" ? true : false,
    publishToSelf: true, // what does this mean?
  },

});

console.log(`Waiting for clients to connect...\n`, `  http://${server.hostname}:${server.port}/`);