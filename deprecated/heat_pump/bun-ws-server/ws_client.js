const socket = new WebSocket("ws://localhost:8767");

socket.addEventListener("message", event => {
  console.log(event.data);
})