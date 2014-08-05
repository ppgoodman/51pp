#!/usr/bin/env python
#-*- coding: utf-8 -*-
########################################################################################################################
#开了这个后，gevent会把基础的socket啊这些东西弄成协程方式，和不开确实有点区别，不过感觉不大，暂时不开
#from gevent import monkey
#monkey.patch_all()
import WebPage
import os
import tornado.web
from tornado.options import define, options
import base64, uuid
from utils.xlog import GLog
import sys
import signal
import time

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=0, help="user pdb", type=int)
########################################################################################################################

########################################################################################################################

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            #page handle            
            (r"/", WebPage.IndexHandler),
            (r"/search", WebPage.SearchHandler),
            (r"/detail/(\w+)", WebPage.DetailHandler),

            (r"/login", WebPage.LoginHandler),
            (r"/register", WebPage.RegisterHandler),
            (r"/account", WebPage.AccountHandler),
            (r"/intro", WebPage.IntroHandler),
        ]

        _cookie_s = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret=_cookie_s,
            debug=False,
            login_url="/login",  # 默认的登陆页面，必须有
        )

        #         settings['pycket'] = {
        #              'engine': 'redis',
        #              'storage': {
        #                  'host': 'localhost',
        #                  'port': 6379,
        #                  'db_sessions': 10,
        #                  'db_notifications': 11,
        #                  'max_connections': 2 ** 31,
        #              },
        #              'cookies': {
        #                  'expires_days': 120,
        #              },
        #         }

        settings['pycket'] = {
            'engine': 'memcached',
            'storage': {
                'servers': ('localhost:11211',)
            },
            'cookies': {
                'expires_days': 120,
            },
        }
        self.trans = []
        GLog.Log('Server Running...')
        tornado.web.Application.__init__(self, handlers, **settings)



class App:
    def __init__(self):
        self.http_server = None
        self.mainApp = None
        self.io_loop = None
        self.deadline = None

    def __del__(self):
        pass


    def sig_handler(self, sig, frame):
        GLog.Log('Caught signal: %s'%sig)
        tornado.ioloop.IOLoop.instance().add_callback(self.shutdown)

    def shutdown(self):
        GLog.Log('Stopping http server')
        self.http_server.stop() # 不接收新的 HTTP 请求

        GLog.Log('Will shutdown in %s seconds ...'%1)
        self.io_loop = tornado.ioloop.IOLoop.instance()

        self.deadline = time.time() + 1
        self.stop_loop()

    def stop_loop(self):
        now = time.time()
        if now < self.deadline and (self.io_loop._callbacks or self.io_loop._timeouts):
            self.io_loop.add_timeout(now + 1, self.stop_loop)
        else:
            print 'Server Shutdown!'
            self.io_loop.stop() # 处理完现有的 callback 和 timeout 后，可以跳出 io_loop.start() 里的循环

    def Init(self):
        reload(sys)
        sys.setdefaultencoding('utf-8')

        # register signal.SIGTSTP's handler
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGQUIT, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        signal.signal(signal.SIGTSTP, self.sig_handler)
        #signal.signal(signal.SIGTERM, self.sig_handler)

        return True

    def MainLoop(self):
        tornado.options.parse_command_line()

        if options.debug == 1:
            import pdb

            pdb.set_trace()  #引入相关的pdb模块
        self.mainApp = Application()
        self.http_server = tornado.httpserver.HTTPServer(self.mainApp, xheaders=True)
        self.http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    app = App()
    if app.Init():
        app.MainLoop()

