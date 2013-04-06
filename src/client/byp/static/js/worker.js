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
  	var d = evt.data;
    if (d == "ws-project-select") {
        updater.initui();
    }
}

function updateUI (message) {
    //console.log('notify ui to update view');
    var msg = String.format("msrc = {0}, content = {1}", message['msrc'], message['content']);
    postMessage(msg);
}

//main websocket service object
var updater = {
    socket: null,

    start: function() {
        //1. connect to server
        //console.log('connect to server');
        var url = "ws://localhost:8888/buildserver";
        updater.socket = new WebSocket(url);
        
        //2 register callbacks
	    updater.socket.onmessage = function(event) {
	        updateUI(JSON.parse(event.data));
	    }
        updater.socket.onopen = function (event) {
            // handshaked, init ui
            //console.log('websocket server connected');
            updater.initui();
        }
        updater.socket.onerror = function (event) {
            //console.log('websocket error occer');
        }

    },

    initui: function() {
        //3 init ui
        //console.log('initialize user interface');
        var projSelMsg = "{\"msrc\":\"ws-project-select\"}";
        updater.socket.send(projSelMsg);

    }
};

updater.start();