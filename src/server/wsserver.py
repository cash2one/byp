# coding=UTF-8
"""
@author tomas
@date    2013-03-31
@desc
    server
    
@brief
    main build websocket server 
"""


import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
import time

from tornado.options import define, options

import project

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/buildserver", BuildServerHandler),
            (r"/heartbeat", HeartbeatHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            autoescape=None,
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

#处理默认连接相应
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages=ChatSocketHandler.cache)

#处理build主页相应
class BuildServerHandler(tornado.websocket.WebSocketHandler):
    clients = []
    workers = []
    def open(self):
        print self.request.headers
        self.id = ''
        self.nickname = ''
        self.status = ''#'idle','running','error'
        self.type = ''#'client','worker'

    def on_close(self):
        
        #通知所有clients，worker少了一个
        if self.type == 'worker':
            BuildServerHandler.workers.remove(self)
            for client in BuildServerHandler.clients:
                content = '{"msrc":"ws-worker-select","content":"remove,%s"}' % (self.id)
                client.write_message(content)
                content = '{"msrc":"ws-worker-%s","content":"-"}' % self.status
                client.write_message(content)
        #通知所有worker，不再notify
        elif self.type == 'client':
            BuildServerHandler.clients.remove(self)
            pass
 
    def on_message(self, message):
        logging.info("got message %r", message)
        content = ''
        msg = eval(message)
        if msg['msrc'] == 'ws-client-connect':
            self.type = 'client'
            BuildServerHandler.clients.append(self)
            
        elif msg['msrc'] == 'wk-worker-connect':
            ctx = msg['content'].split('|');
            self.id = ctx[0]
            self.nickname = ctx[1]
            self.status = 'idle'
            self.type = 'worker'
            BuildServerHandler.workers.append(self)
            
            #通知所有clients，worker增加了一个
            for client in BuildServerHandler.clients:
                content = '{"msrc":"ws-worker-select","content":"add,%s,%s,%s"}' % (self.id,self.nickname,self.status)
                client.write_message(content)
                content = '{"msrc":"ws-worker-idle","content":"+"}'
                client.write_message(content)
        
        elif msg['msrc'] == 'ws-project-select':
            content = '{"msrc":"ws-project-select","content":"'
            for key,val in project.projects.items():
                content += '%s,' % key
            content = content[:-1]
            content += '"}'
            self.write_message(content)
            
        elif msg['msrc'] == 'ws-sln-select':
            projName = msg['content']
            try:
                slns = project.projects[projName]
                for item in slns:
                    content = '{"msrc":"ws-sln-select","content":"%s,%s,%s,%s"}' % (item[0],item[1],item[2],item[3])
                    self.write_message(content)
            except KeyError,e:
                logging.info('message error %s' % message)
        
        elif msg['msrc'] == 'ws-build-options':
            projName = msg['content']
            try:
                options = project.build_options[projName]
                for key,val in options.items():
                    if val[0] == 'check':
                        content = '{"msrc":"ws-build-options","content":"%s|%s|%s|%s,%s"}' % (key,val[0],val[1],val[2],val[3])
                    elif val[0] == 'radio':
                        ctx = ''
                        for item in val[2]:
                            ctx += '%s,%s,%s' % (item[0],item[1],item[2])
                            if len(item) == 4:
                                ctx += ',%s;' % item[3]
                            else:
                                ctx += ';'
                        ctx = ctx[:-1]
                        content = '{"msrc":"ws-build-options","content":"%s|%s|%s|%s"}' % (key,val[0],val[1],ctx)
                    self.write_message(content)
            except KeyError,e:
                logging.info('message error %s' % message)
                
        elif msg['msrc'] == 'ws-worker-select':
            if len(BuildServerHandler.workers) == 0:
                return
            if msg['content'] == '':
                for worker in BuildServerHandler.workers:
                    content = '{"msrc":"ws-worker-select","content":"add,%s,%s,%s"}' % (worker.id,worker.nickname,worker.status)
                    self.write_message(content)
                    content = '{"msrc":"ws-worker-%s","content":"+"}' % worker.status
                    self.write_message(content)
            else:
                pass
            
#处理心跳连接相应
class HeartbeatHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        print self.request.headers
        self.workerId = ''

    def on_close(self):
        self.workerId = ''

    def on_message(self, message):
        logging.info("got message %r", message)
        self.write_message(message)

#代表一个client
class buildClient(object):
    def __init__(self):
        self.clientId = uuid.uuid4()
        self.nickname = ''
        object.__init__(self)
        
    #update client ui
    #classmethod
    def update(cls):
        pass

    def __str__(self):
        return '[%s]' % nickname

#表征一个worker
class buildWorker(object):
    def __init__(self, id, nickname):
        self.workerId = id
        self.nickname = nickname
        self.watchers = set()
        object.__init__(self)
    
    def addWatcher(self,client):
        self.watchers.add(client)
        
    def removeWatcher(self,client):
        self.watchers.remove(client)
        
    def notifyWatchers(self):
        for client in self.watchers:
            logging.info('notify client %s' % client)
            client.update()
    
def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
