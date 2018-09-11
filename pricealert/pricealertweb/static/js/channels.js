// Note that the path doesn't matter right now; any WebSocket
// connection gets bumped over to WebSocket consumers
socket = new WebSocket("ws://" + window.location.host);

socket.onmessage = function(e) {
  alert(e.data);
}

// Call onopen directly if socket is already open
if (socket.readyState == WebSocket.OPEN) socket.onopen();
