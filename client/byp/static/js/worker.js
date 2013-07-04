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
    postMessage(message);
}

//main websocket service object
var updater = {
    socket: null,

    start: function() {
        //1. connect to server
        //console.log('connect to server');
        var url = "ws://172.17.180.61:13412/buildserver";
        updater.socket = new WebSocket(url);
        
        //2 register callbacks
	    updater.socket.onmessage = function(event) {
	        updateUI(event.data);
	    }
        updater.socket.onopen = function (event) {
            // handshaked, init ui
            //console.log('websocket server connected');
            updater.send("{\"msrc\":\"ws-client-connect\",\"content\":\"18\"}");
            updater.send("{\"msrc\":\"ws-project-select\",\"content\":\"\"}");
            updater.send("{\"msrc\":\"ws-worker-select\",\"content\":\"\"}");
            updater.send("{\"msrc\":\"ws-query-buildlog\",\"content\":\"\"}");
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
