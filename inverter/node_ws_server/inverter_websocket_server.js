const path = require("path");
const ws = require("ws");
const fs = require("fs");
const ini = require("ini");

console.log("Server started");

// so that files like config.cfg are always found, no matter from where the script is being run
process.chdir(path.dirname(process.argv[1]));

/********************
 * Global variables *
 ********************/

var CLIENT_AUTOINCREMENT = 0;
var CURR_VALUES = {};
var CURR_STATUS = {};

const CONFIGFULL = ini.parse(
    fs.readFileSync('../../config.cfg', 'utf-8')
);
const CONFIG = CONFIGFULL.DeyeInverter_WebSocket;

var DEBUG = false;
process.argv.forEach(arg => {
    if (arg === "-d" || arg === "--debug") {
        DEBUG = true;
    }
});

/***************
 * End globals *
 ***************/

function client_ids(clients) {
    return [...clients].map(client => client.id);
}

var WebSocketServer = ws.Server;
var wss = new WebSocketServer({ host: CONFIG.host, port: CONFIG.port });
wss.on("connection", function (conn) {
    conn.id = CLIENT_AUTOINCREMENT++;
    console.log(`[${new Date().toISOString()}] New connection (${conn.id})! Now ${wss.clients.size} open connection${wss.clients.size == 1 ? "" : "s"}:`, client_ids(wss.clients));

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
            console.log(`[${new Date().toISOString()}] Message from (${conn.id}):`, msg);
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
        wss.clients.forEach(function (client) {
            client.send(broadcast_msg);
        });
    });

    conn.on("close", function () {
        // CLIENTS.delete(conn);
        console.log(`[${new Date().toISOString()}] Connection (${conn.id}) closed. Now ${wss.clients.size} open connection${wss.clients.size == 1 ? "" : "s"}:`, client_ids(wss.clients));
    });
});
