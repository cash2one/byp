import tornado.httpserver
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        '''
        The below is only a testing which will be exected to kill time,
        and then we can find the asynchronous effect from the front page.
        '''
        for i in range(1, 100000):
            print "kill time"
        self.write("hello")


settings = {
    #"debug": True,
}

application = tornado.web.Application([
    (r"/async-sync-test/", MainHandler),
], **settings)

if __name__ == "__main__":

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8084)
    tornado.ioloop.IOLoop.instance().start()

