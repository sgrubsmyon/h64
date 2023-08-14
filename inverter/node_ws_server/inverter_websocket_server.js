const ws = require("ws");
const fs = require("fs");
const ini = require("ini");

console.log("Server started");

/********************
 * Global variables *
 ********************/

var CLIENTS = new Set();
var CURR_VALUES = {};
var CURR_STATUS = {};

const CONFIGFULL = ini.parse(
    fs.readFileSync('../../config.cfg', 'utf-8')
);
const CONFIG = CONFIGFULL.WebSocket;

var DEBUG = false;
process.argv.forEach(arg => {
    if (arg === "-d" || arg === "--debug") {
        DEBUG = true;
    }
});
// or:
// if (
//     process.argv.indexOf("-d") > -1 ||
//     process.argv.indexOf("--debug") > -1
// ) {
//     DEBUG = true;
// }

/***************
 * End globals *
 ***************/

var WebSocketServer = ws.Server;
var wss = new WebSocketServer({ host: CONFIG.host, port: CONFIG.port });
wss.on("connection", function (conn) {
    CLIENTS.add(conn);
    console.log(`[${new Date().toISOString()}] New connection (${conn})! Now ${CLIENTS.size} open connection${CLIENTS.size == 1 ? "" : "s"}:`, CLIENTS);

    // Send the current values to the freshly connected client:
    conn.send(JSON.stringify({
        values: CURR_VALUES,
        status: CURR_STATUS
    }));

    // Now wait for a message from the client.
    // There is only one client that is supposed to ever
    // send messages and this is the Python script
    // querying the inverter and putting the values
    // into the database. It sends messages with
    // the fresh values to this WebSocket server.
    // All other clients (in web browser) only passively
    // receive the messages with current values and do
    // not send any messages.
    conn.on("message", function (message) {
        msg = JSON.parse(message);
        if (DEBUG) {
            console.log(`[${new Date().toISOString()}] Message from (${conn}):`, msg);
        }
        const msg_keys = Object.keys(msg);
        if (msg_keys.includes("group") && msg_keys.includes("values")) {
            // Update the current values with new ones:
            const group = msg.group;
            if (msg.values != null) {
                CURR_VALUES[group] = msg.values;
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
        CLIENTS.forEach(function (client) {
            client.send(broadcast_msg);
        })
    });

    conn.on("close", function () {
        CLIENTS.delete(conn);
        console.log(`[${new Date().toISOString()}] Connection (${conn}) closed. Now ${CLIENTS.size} open connection${CLIENTS.size == 1 ? "" : "s"}:`, CLIENTS);
    });
});
