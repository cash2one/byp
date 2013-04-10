# coding=UTF-8
"""
@author tomas
@date    2013-03-31
@desc
	代表一个worker websocket
    
@brief
     
"""

import sys,os,time
import logging
import socket
import websocket
import subprocess
import uuid
import worker

#worker thread
class Worker(subprocess.Popen):
	def __init__(self, wsConnection):
		self.socket = wsConnection
		threading.Thread.__init__(self)

	def run(self):
		pass

def postStatus(socket,msg):
	logging.info('send %s' % msg)
	socket.send(msg)

def mainLoop(socket, workerId, nickname):
	logging.info('start mainlooping')
	worker = None
	socket.send('{"msrc":"wk-worker-connect","content":"%s|%s"}' % (workerId,nickname))
	try:
		while True:
			msg = socket.recv()
			ctx = eval(msg)
			logging.info('command received %s' % ctx)
			if ctx['msrc'] == 'wk-start-build':
				postStatus(socket,'{"msrc":"wk-status-change","content":"running"}')
			#build !!!
			time.sleep(5)
			postStatus(socket,'{"msrc":"wk-status-change","content":"idle"}')
			
	except Exception, e:
		logging.error(e)
		logging.error('exception in mainLoop, server may lost')
	
	logging.info('end mainlooping')

		
def main(argc, argv):
	#init logging system, it's told logging is threadsafe, so do NOT need to sync
	logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG, stream = sys.stdout)
	
	#init constants
	timeout_buildserver = 0
	workerId = '%s' % uuid.uuid4()
	nickname = 'Daenerys'
	
	while True:
		ws_service = None
		try:
			#make connection to wsserver
			logging.info('try connectting to server')
			opts = list()
			opts.append('sid: %s' % workerId)
			ws_service = websocket.create_connection("ws://192.168.5.21:8888/buildserver",
								timeout = timeout_buildserver,
								sockopt = ((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),),
								header = opts)
			logging.info('server connected')
		
			#main logic
			mainLoop(ws_service, workerId, nickname)
		
		except Exception,e:
			logging.error(e)
			logging.error('failed to connect to server')
			logging.info('sleep 5 seconds and try again ...')
			time.sleep(5)
	
	logging.info('main quit')

if __name__ == "__main__":
	sys.exit(main(len(sys.argv),sys.argv))
