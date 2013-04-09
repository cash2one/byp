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
import threading
import socket
import websocket
import subprocess
import uuid
import worker

#heartbeat thread
class HeartBeatThread(threading.Thread):
	def __init__(self, id, wsConnection, t):
		self.workerId = id
		self.socket = wsConnection
		self.interval = t
		threading.Thread.__init__(self)

	def setInterval(self, t):
		self.interval = t
		
	def setSocket(self, wsConnection):
		self.socket = wsConnection

	def run(self):
		try:
			logging.info('heartbeat thread started')
			while True:
				self.sendHeartbeat()
				self.receiveHeartbeat()
				time.sleep(self.interval)
		except Exception,e:
			logging.error(e)
			logging.error('heartbeat thead exception, thread quit')
	
	def sendHeartbeat(self):
		msg = '{"msrc":"wk-heart-beat","sid":"%s",}' % self.workerId
		self.socket.send(msg)
		logging.info('heartbeat sended %s' % msg)

	def receiveHeartbeat(self):
		result = self.socket.recv()
		logging.info('heartbeat received %s' % result)
		
#worker thread
class Worker(subprocess.Popen):
	def __init__(self, wsConnection):
		self.socket = wsConnection
		threading.Thread.__init__(self)

	def run(self):
		pass

def mainLoop(socket, workerId, nickName):
	logging.info('start mainlooping')
	worker = None
	socket.send('{"msrc":"wk-worker-connect","content":"%s|%s"}' % (workerId,nickName))
	try:
		while True:
			msg = socket.recv()
			parsed = eval(msg)
			logging.info('command received %s' % parsed)
	except Exception, e:
		logging.error(e)
		logging.error('exception in mainLoop, server may lost')
	
	logging.info('end mainlooping')

		
def main(argc, argv):
	#init logging system, it's told logging is threadsafe, so do NOT need to sync
	logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG, stream = sys.stdout)
	
	#constants
	hbThread = None
	interval_to_send_beartbeat = 1
	timeout_heartbeat = 10
	timeout_buildserver = 0
	workerId = '%s' % uuid.uuid4()
	nickName = 'Daenerys'
	
	while True:
		ws_heartbeat = None
		ws_service = None
		try:
			#make connection to wsserver
			logging.info('try connectting to server')
			opts = list()
			opts.append('sid: %s' % workerId)
			ws_heartbeat = websocket.create_connection("ws://localhost:8888/heartbeat",
								timeout = timeout_heartbeat,
								sockopt = ((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),),
								header = opts)
			ws_service = websocket.create_connection("ws://localhost:8888/buildserver",
								timeout = timeout_buildserver,
								sockopt = ((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),),
								header = opts)
			logging.info('server connected')
			
			#init heartbeating system
			#logging.info('start heartbeating')
			#hbThread = HeartBeatThread(workerId, ws_heartbeat, interval_to_send_beartbeat)
			#hbThread.start()
		
			#main logic
			#time.sleep(10)
			mainLoop(ws_service, workerId, nickName)
		
		except Exception,e:
			logging.error(e)
			logging.error('failed to connect to server')
			logging.info('sleep 5 seconds and try again ...')
			time.sleep(5)
	
	logging.info('main quit')

if __name__ == "__main__":
	sys.exit(main(len(sys.argv),sys.argv))
