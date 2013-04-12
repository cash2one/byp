//
//
//
//
//
//
//
//
//
//
//
//
//
//
//


String.format = function ()
{
    var param = [];
    for (var i = 0, l = arguments.length; i < l; i++)
    {
        param.push(arguments[i]);
    }
    var statment = param[0]; // get the first element(the original statement)
    param.shift(); // remove the first element from array
    return statment.replace(/\{(\d+)\}/g, function(m, n)
    {
        return param[n];
    });
}

onmessage = function (evt){
    updater.send(evt.data);
}

function updateUI (message) {
    //console.log('notify ui to update view');
    var msg = String.format("{\"msrc\":\"{0}\",\"content\":\"{1}\"}", message['msrc'], message['content']);
    postMessage(msg);
}

//main websocket service object
var updater = {
    socket: null,

    start: function() {
        //1. connect to server
        //console.log('connect to server');
        var url = "ws://192.168.5.21:13412/buildserver";
        updater.socket = new WebSocket(url);
        
        //2 register callbacks
	    updater.socket.onmessage = function(event) {
	        updateUI(JSON.parse(event.data));
	    }
        updater.socket.onopen = function (event) {
            // handshaked, init ui
            //console.log('websocket server connected');
            updater.send("{\"msrc\":\"ws-client-connect\",\"content\":\"\"}");
            updater.send("{\"msrc\":\"ws-project-select\",\"content\":\"\"}");
            updater.send("{\"msrc\":\"ws-worker-select\",\"content\":\"\"}");
        }
        updater.socket.onerror = function (event) {
            //console.log('websocket error occer');
        }

    },

    // send message to server
    send: function(msg) {
        updater.socket.send(msg);

    }
};

updater.start();
