from websocket import create_connection
import uuid

opts = list()
opts.append('msrc: wk-heart-beat')
opts.append('sid: %s' % uuid.uuid4())

ws = create_connection("ws://localhost:8888/chatsocket",header=opts)

while True:
	print "Sending 'Hello, World'..."
	ws.send("Hello, World")
	print "Sent"
	print "Reeiving..."
	result =  ws.recv()
	print "Received '%s'" % result
ws.close()