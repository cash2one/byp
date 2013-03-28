import os
import tornado.web
import tornado.httpclient


class MainHandlerOriginal(tornado.web.RequestHandler):
    def initialize(self):
        print "in initialize"
        self.write("<p>in initialize<p>")
    
    def prepare(self):
        print "in prepare"
        self.write("<p>in prepare<p>")
    
    def get_error_html(self):
        print "in get_error_html"
        self.write("<p>in get_error_html<p>")
        
    def get_current_user(self):
        print "in get_current_user"
        self.write("<p>in get_current_user<p>")
        
    def get_user_locale(self):
        print "in get_user_locale"
        self.write("<p>in get_user_locale<p>")
        
    def get_login_url(self):
        print "in get_login_url"
        self.write("<p>in get_login_url<p>")
        
    def get_template_path(self):
        print "in get_template_path"
        self.write("<p>in get_template_path<p>")
    
    def get(self):
        self.write("You requested the main page")
        self.redirect("/story/1",permanent=False)

class StoryHandler(tornado.web.RequestHandler):
    def get(self, story_id):
        self.write("You requested the story " + story_id)

class TemplateHandler(tornado.web.RequestHandler):
    def get(self):
        items = ["Item 1", "Item 2", "Item 3"]
        self.render("template.html", title="My title", items=items)

class CookieHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie("mycookie"):
            self.set_secure_cookie("mycookie", "myvalue")
            self.write("Your cookie was not set yet!")
        else:
            self.write("Your cookie was set!")

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        self.write("Hello, " + name)

class LoginHandler(BaseHandler):
    def get(self):
        self.write('<html><body><form action="/login" method="post">'
                   'Name: <input type="text" name="name">'
                   '<input type="submit" value="Sign in">'
                   '</form></body></html>')

    def post(self):
        self.set_secure_cookie("user", self.get_argument("name"))
        self.redirect("/")

class AsyncHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        http = tornado.httpclient.AsyncHTTPClient()
        http.fetch("http://localhost:8084/async-sync-test/",callback=self.on_response)
        #http.fetch("http://localhost:8084/async-sync-test/", callback=self.fake_func)

    def fake_func(self, response):
        #Cannot write() after finish().  
        #May be caused by using async operations without the @asynchronous decorator.
        self.write(response.body)
    
    def on_response(self, response):
        if response.error:
            raise tornado.web.HTTPError(500)
        self.write(response.body)
        self.finish()


if __name__ == "__main__":
    
        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            "login_url": "/login",
            "xsrf_cookies": True,
            "debug":True,
        }

        application = tornado.web.Application([
            (r"/original", MainHandlerOriginal),
            (r"/", MainHandler),
            (r"/login", LoginHandler),
            (r"/template", TemplateHandler),
            (r"/cookie", CookieHandler),
            (r"/story/([0-9]+)", StoryHandler),
            (r"/async", AsyncHandler),
        ], **settings)
        
        application.listen(8888)
        
        tornado.ioloop.IOLoop.instance().start()
        
