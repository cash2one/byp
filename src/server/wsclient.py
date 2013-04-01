from websocket import create_connection
ws = create_connection("ws://localhost:8888/chatsocket")
i = 0
while True:
	print "Sending 'Hello, World'..."
	msg = '{"body":"hello from wsclient to wschatserver %d","_xsrf":"1dd6c86a4f9a461aaafd01c014ae387f"}' % i
	i = i + 1
	ws.send(msg)
	print "Sent"
	print "Reeiving..."
	result =  ws.recv()
	print "Received '%s'" % result
ws.close()