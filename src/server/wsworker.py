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

#heartbeat thread
class HeartBeatThread(threading.Thread):
	def __init__(self, eventQuit, wsConnection, t):
		self.evtQuit = eventQuit
		self.socket = wsConnection
		self.interval = t
		threading.Thread.__init__(self)

	def setInterval(self, t):
		self.interval = t

	def run(self):
		while True:
			self.sendHeartbeat()
			self.receiveHeartbeat()
			
			if self.evtQuit.isSet():
				self.socket.close()
				break
			else:
				time.sleep(self.interval)
	
	def sendHeartbeat(self):
		msg = '{"body":"heartbeat","_xsrf":"1dd6c86a4f9a461aaafd01c014ae387f"}'
		self.socket.send(msg)
		logging.info('heartbeat sended %s' % msg)

	def receiveHeartbeat(self):
		result =  self.socket.recv()
		logging.info('heartbeat received %s' % result)
		
#worker thread
class Worker(subprocess.Popen):
	def __init__(self, wsConnection):
		self.socket = wsConnection
		threading.Thread.__init__(self)

	def run(self):
		pass

def main(argc, argv):
	#init logging system, it's told logging is threadsafe, so do NOT need to sync
	logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG, stream = sys.stdout)
	
	#make connection to wsserver
	ws_heartbeat = None
	ws_service = None
	try:
		ws_heartbeat = websocket.create_connection("ws://localhost:8888/heartbeat",
							timeout = 10,
							sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),))
	
		ws_service = websocket.create_connection("ws://localhost:8888/buildserver",
							timeout = 0,
							sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),))
	except websocket.WebSocketException,e:
		logging.error('failed to connect to server')
		logging.error(e)
		return
	
	#init syncObj
	evtQuit = threading.Event()
	
	#init heartbeating system
	interval = 1
	hbThread = HeartBeatThread(evtQuit, ws_heartbeat, interval)
	hbThread.start()
	
	#main logic
	worker = None
	while True:
		msg = ws_service.recv()
		parsed = eval(msg)
		if parsed['type'] != '2':
			continue
		elif parsed['ws-btn-build'] == 'cancel':
			if worker == None:
				continue
			else:
				logging.info('worker terminated')
				#worker.terminate()
				worker = None
				logging.info('worker notify server to turn on build')
				ws_service.send('ws-btn-build=build')
		elif parsed['ws-btn-build'] == 'build':
			if worker == None:
				command = 'python build.py '
				for key,val in parsed:
					cmdline += '%s=%s' % (key,val)
					cmdline += ' '
				logging.info(command)
				worker = 'building in progress'
				#worker = subprocess.call(command)
				logging.info('worker notify server to turn off build')
				ws_service.send('ws-btn-build=cancel')
			else:
				logging.info('building in progress, please wait')
		else:
			continue
	
	#tell hbthread to quit
	time.sleep(10)
	evtQuit.set()
	hbThread.join()
	logging.info('main quit')

if __name__ == "__main__":
	sys.exit(main(len(sys.argv),sys.argv))
