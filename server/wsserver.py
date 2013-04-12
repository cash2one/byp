# coding=UTF-8
"""
@author tomas
@date    2013-03-31
@desc
    a websocket server that support client and worker
    
@brief
    main build websocket server 
"""


import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import logging
import sys,os.path
import uuid
import time
import project

from tornado.options import define, options

define("port", default=13412, help="run on the given port", type=int)

#main web app
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),#for v8 and webkit portable web client (must support websocket)
            (r"/buildserver", BuildServerHandler),#for google chrome extension client
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

#处理默认连接响应
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

#处理build主页响应
class BuildServerHandler(tornado.websocket.WebSocketHandler):
    clients = []
    workers = []
    
    #发送消息
    def notify(self, content):
        logging.info('send message %s' % content)
        self.write_message(content)
    
    def allow_draft76(self):
        # for iOS 5.1.1 Safari and Chrome
        return True
    
    def open(self):
        pass

    def on_close(self):
        #worker断开，通知所有clients，worker少了一个
        if self.type == 'worker':
            BuildServerHandler.workers.remove(self)
            for client in BuildServerHandler.clients:
                content = '{"msrc":"ws-worker-select","content":"remove,%s"}' % (self.id)
                client.notify(content)
                content = '{"msrc":"ws-worker-%s","content":"-"}' % self.status
                client.notify(content)
        #client断开，移除该client
        elif self.type == 'client':
            BuildServerHandler.clients.remove(self)
            for worker in BuildServerHandler.workers:
                if self in worker.listeners:
                    worker.listeners.remove(self)
 
    def on_message(self, message):
        logging.info("recv message %r", message)
        content = ''
        msg = eval(message)
        
        #client连接时发送；增加client
        if msg['msrc'] == 'ws-client-connect':
            self.type = 'client'
            BuildServerHandler.clients.append(self)
            if len(BuildServerHandler.workers) > 0:
                BuildServerHandler.workers[0].listeners.append(self)
            
        #worker连接时发送；增加idle worker
        elif msg['msrc'] == 'wk-worker-connect':
            ctx = msg['content'].split('|');
            self.id = ctx[0]
            self.nickname = ctx[1]
            self.status = 'idle'
            self.type = 'worker'
            self.listeners = []
            BuildServerHandler.workers.append(self)
            
            #通知所有clients，worker增加了一个
            for client in BuildServerHandler.clients:
                content = '{"msrc":"ws-worker-select","content":"add,%s,%s,%s,%s"}' % (self.id,self.nickname,self.status,self.request.remote_ip)
                client.notify(content)
                content = '{"msrc":"ws-worker-idle","content":"+"}'
                client.notify(content)
                
        #client连接后发送；提供projects
        elif msg['msrc'] == 'ws-project-select':
            content = '{"msrc":"ws-project-select","content":"'
            for key,val in project.projects.items():
                content += '%s,' % key
            content = content[:-1]
            content += '"}'
            self.notify(content)
            
        #手动切换项目combobox时发送；提供当前project的slns
        elif msg['msrc'] == 'ws-sln-select':
            projName = msg['content']
            try:
                slns = project.projects[projName]
                for item in slns:
                    content = '{"msrc":"ws-sln-select","content":"%s,%s,%s,%s"}' % (item[0],item[1],item[2],item[3])
                    self.notify(content)
            except KeyError,e:
                logging.info('message error %s' % message)
                
        #手动切换项目combobox时发送；提供当前project的buildoptions
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
                    self.notify(content)
            except KeyError,e:
                logging.info('message error %s' % message)
                
        #手动切换项目combobox时发送；提供当前project支持的codebase
        elif msg['msrc'] == 'ws-code-base':
            projName = msg['content']
            try:
                codebase = project.build_depends[projName]
                for item in codebase:
                    if len(item) == 3:
                        content = '{"msrc":"ws-code-base","content":"%s,%s,%s"}' % (item[0],item[1],item[2])
                    elif len(item) == 4:
                        content = '{"msrc":"ws-code-base","content":"%s,%s,%s,%s"}' % (item[0],item[1],item[2],item[3])
                    self.notify(content)
            except KeyError,e:
                logging.info('message error %s' % message)
                    
        #手动切换worker时发送，提供worker状态
        elif msg['msrc'] == 'ws-worker-select':
            if len(BuildServerHandler.workers) != 0:
                if msg['content'] == '':
                    for worker in BuildServerHandler.workers:
                        content = '{"msrc":"ws-worker-select","content":"add,%s,%s,%s,%s"}' % (worker.id,worker.nickname,worker.status,self.request.remote_ip)
                        self.notify(content)
                        content = '{"msrc":"ws-worker-%s","content":"+"}' % worker.status
                        self.notify(content)
                else:
                    workerId = msg['content']
                    for worker in BuildServerHandler.workers:
                        if workerId == worker.id:
                            if self not in worker.listeners:
                                worker.listeners.append(self)
                                content = '{"msrc":"ws-worker-%s","content":"+"}' % worker.status
                                self.notify(content)
                        else:
                            if self in worker.listeners:
                                worker.listeners.remove(self)
            else:
                content = '{"msrc":"ws-worker-select","content":""}'
                self.notify(content)
            
        #收到worker状态切换，通知所有clients
        elif msg['msrc'] == 'wk-status-change':
            oldStatus = self.status
            self.status = msg['content']
            content0 = '{"msrc":"ws-worker-select","content":"update,%s,%s"}' % (self.id,self.status)
            content1 = '{"msrc":"ws-worker-%s","content":"-"}' % (oldStatus)
            content2 = '{"msrc":"ws-worker-%s","content":"+"}' % (msg['content'])
            for client in self.listeners:
                client.notify(content0)
                client.notify(content1)
                client.notify(content2)
        
        #收到worker日志，发送到这个worker的所有listener
        elif msg['msrc'] == 'wk-build-log':
            content = '{"msrc":"ws-build-log","content":"%s"}' % msg['content']
            for client in self.listeners:
                client.notify(content)
                
        #收到打包消息，开始干活
        elif msg['msrc'] == 'ws-btn-build':
            content = '{"msrc":"wk-start-build","content":"%s"}' % msg['content']
            for worker in BuildServerHandler.workers:
                if worker.status == 'idle':
                    worker.notify(content)
                    break
                
        #收到进度更新消息，通知所有listener更新进度
        elif msg['msrc'] == 'wk-build-progress':
            content = '{"msrc":"ws-build-progress","content":"%s"}' % msg['content']
            for client in self.listeners:
                client.notify(content)
        #收到不知道是什么
        else:
            pass
            
        #如果对象是client，且是某些需要更新ui的消息类型，通知其重置ui
        if self.type == 'client' and (msg['msrc'] == 'ws-sln-select' or msg['msrc'] == 'ws-build-options' or msg['msrc'] == 'ws-code-base'):
            content = '{"msrc":"ws-client-update","content":""}';
            self.notify(content)
            
def main():
    #init logging system, it's told logging is threadsafe, so do NOT need to sync
    logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG, stream = sys.stdout)
    
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
