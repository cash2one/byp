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

    def open(self):
        print self.request.headers
        self.workerId = ''

    def on_close(self):
        self.workerId = ''

    def on_message(self, message):
        logging.info("got message %r", message)
        content = ''
        msg = eval(message)
        if msg['msrc'] == 'ws-project-select':
            content = '{"msrc":"ws-project-select","content":"'
            for key,val in project.projects.items():
                content += '%s,' % key
            content =content[:-1]
            content += '"}'
        elif msg['msrc'] == 'ws-sln-select':
            pass
        self.write_message(content)

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
    def __init__(self):
        self.workerId = uuid.uuid4()
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
