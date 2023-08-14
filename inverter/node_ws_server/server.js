const ws = require("ws");

console.log("Server started");
var WebSocketServer = ws.Server
var wss = new WebSocketServer({ port: 8765 });
wss.on('connection', function (ws) {
    ws.on('message', function (message) {
        console.log('Received from client: %s', message);
        ws.send('Server received from client: ' + message);
    });
});