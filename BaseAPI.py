#!/usr/bin/env python
#-*- coding: utf-8 -*-
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.gen
import json

from pycket.session import SessionMixin
#from pycket.session import SessionManager

def ReturnCode(error_code, msg=None):
    ejson = {'code': error_code}
    if None != msg:
        ejson['msg'] = msg
    jsonstr = json.dumps(ejson)
    return jsonstr

class BaseHandler(tornado.web.RequestHandler, SessionMixin):
    def get_current_user(self):
        username = self.session.get('user')
        return username

    def write_error(self, status_code, **kwargs):
        self.render('error.html', title='错误提示',errmsg='内部错误', errcode=status_code)
        #self.write(ReturnCode(900, status_code))
        #self.write("{code:900, msg:%d}" % (status_code))







