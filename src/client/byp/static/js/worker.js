onmessage = function (evt){
  	var d = evt.data;
  	postMessage(d);
}

//main websocket service object
var updater = {
    socket: null,

    start: function() {
        //1. handshake
        var url = "ws://localhost:8888/chatsocket";
        updater.socket = new WebSocket(url);
        
        //2 register callbacks
	    updater.socket.onmessage = function(event) {
	        updater.showMessage(JSON.parse(event.data));
	    }

        //3 
    },

    showMessage: function(message) {
    	postMessage(message.html);
    }
};

updater.start();