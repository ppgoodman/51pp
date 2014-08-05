#!/usr/bin/env python
#-*- coding: utf-8 -*-
########################################################################################################################
import time
import BaseAPI
from utils import utils
import json
from utils.xDB import GxDB
from utils.xlog import GLog
from utils import coreseekapi
from math import ceil

########################################################################################################################
#http://192.168.22.129:8888/test?type=logtest|login
class TestHandler(BaseAPI.BaseHandler):
    def get(self):
        testtype = self.get_argument('type')

        if testtype == 'login':
            username = self.get_current_user()
            if username is None:
                self.redirect("/")
            else:
                self.write(username + '<br>')
                
        elif testtype == 'logtest':
            #log test
            GLog.Log('所噶！！！说的是呢！')
            self.write('log test done!')

        elif testtype == 'db':
            for i in xrange(10):
                key = i + 20
                if i == 9:
                    key = 1

                sqlstr = """INSERT INTO "test" ("id","username")
                            VALUES ('%s','9090@qq.com')"""%key
                GxDB.TransExec(sqlstr)

            rv = GxDB.TransCommit()
            self.write(repr(rv))

        elif testtype == 'json':
            self.set_header("Content-Type", "application/json")
            jsondict =  {
                            'testkey1':1,
                            'testkey2':'2',
                            'testkey3':300.0128,
                            'testkey6':'kadieolskfj'
                        }
            self.write(json.dumps(jsondict))
        
        else:
            self.write('unsupport test type %s <br>'% testtype)
        

    def post(self):
        pass

class IntroHandler(BaseAPI.BaseHandler):
    def get(self):
        self.render('intro.html', title='介绍与申明')

class AccountHandler(BaseAPI.BaseHandler):
    def get(self):
        self.render('account.html', title='VIP账户')

class RegisterHandler(BaseAPI.BaseHandler):
    def get(self):
        self.render('register.html', title='注册51PP VIP')

class LoginHandler(BaseAPI.BaseHandler):
    def get(self):
        self.render('login.html', title='欢迎登录51PP')
    #登录请求发来后，这里在数据库检查是否合法，建立session
    def post(self):        
        #数据库校验
        username = self.get_argument("un")
        password = self.get_argument("pw")
        code = self.get_argument("cd")

        print username, password, code

        sqlstr = """SELECT username FROM "user" WHERE username='%s' and password='%s';""" % (username, utils.EncrypPassword(password))
        rv = GxDB.Query(sqlstr)
        if rv['error'] != 0:
            self.write(BaseAPI.ReturnCode(rv['error'], rv['result']));
            return

        if code.lower() != self.session.get('validatecode'):
            self.write(BaseAPI.ReturnCode(900, '验证码错误'));
            return

        #更新登录时间
        sqlstr = """UPDATE "user" SET lastloginip='%s' WHERE username = '%s'"""\
                    %(self.request.remote_ip, username)
        rv = GxDB.Exec(sqlstr)
        if rv is False:
            #self.write(BaseAPI.ReturnCode(900, '更新数据库错误'));
            return
        
        #成功了才写入session        
        self.session.set('user', username)
        self.session.set('logintime', time.strftime('%Y-%m-%d(%H.%M.%S)',time.localtime(time.time())))
        self.write(BaseAPI.ReturnCode(100));


class DetailHandler(BaseAPI.BaseHandler):
    @staticmethod
    def GetDetail(infohash):
        sqlstr = """SELECT * FROM "bttorrent" WHERE infohash='%s';"""%infohash
        rv = GxDB.Query(sqlstr)
        if rv['error'] != 0:
            return None

        fetchlist = rv['result']
        return fetchlist[0]

    #获取文件列表
    @staticmethod
    def GetFileArray(filetext):
        if filetext is None or len(filetext) == 0:
            return ''
        _id = filetext.find('\r\n')
        if _id == -1:
            arr = filetext.split('\r\n')
        else:
            arr = filetext.split('\n')

        return arr

    def get(self, infohash):
        rv = self.GetDetail(infohash)
        if rv is None:
            self.render('error.html', title='错误提示',errmsg='数据库错误，请重试。', errcode=500)

        filearr = self.GetFileArray(rv['files'])
        self.render('details.html',title='详细结果', infohash=infohash, name=rv['name'], getsize=utils.GetFileSizeString,
                    size=rv['length'],filenum=len(filearr), filelist=filearr, buildtime=rv['buildtime'])



class SearchHandler(BaseAPI.BaseHandler):
    #test only
    # def get(self):
    #     self.render('results.html',title='搜索结果')

    #通过res获取matches的id列表字串
    @staticmethod
    def _GetResIdxStr(res):
        idxstr = ''
        for mi in res['matches']:
            idxstr += '%s,'%mi['id']

        idxstr = idxstr[:-1]
        return idxstr

    #获取数据库中的具体细节数据
    def GetAllSqlData(self, res):
        idxstr = self._GetResIdxStr(res)
        if len(idxstr) == 0:
            return None

        sqlstr = """SELECT * FROM "bttorrent" WHERE idx IN (%s);"""%idxstr
        rv = GxDB.Query(sqlstr)
        if rv['error'] != 0:
            return None

        fetchlist = rv['result']
        return fetchlist


    @staticmethod
    def UpdateKeywordStatistics(key):
        #直接update，如果失败就insert
        sqlstr = """SELECT mergedb('%s', 1)"""%key
        GxDB.Query(sqlstr)


    def ShowResultPage(self, skey, current=0, limit=10):
        """
           res =
           {
               'status': 0,
               'matches':
               [
                   {
                       'id': 1,
                       'weight': 1356,
                       'attrs': {'buildtime': 2014}
                   },
                   {
                       'id': 3,
                       'weight': 1356,
                       'attrs': {'buildtime': 2014}
                   }
               ],
               'fields':['name', 'files'],
               'time': '0.168',
               'total_found': 2,
               'warning': '',
               'attrs': [['buildtime', 2]],
               'words': [{'docs': 2, 'hits': 2, 'word': '\xe8\x9b\x8b\xe8\x9b\x8b'}],
               'error': '',
               'total': 2
           }
        """
        skey = skey.strip()

        #关键字统计记录
        self.UpdateKeywordStatistics(skey)

        res = coreseekapi.clQuery(skey, current, limit)

        # 无结果
        if res is None:
            self.render('results.html', title='搜索结果-%s' % skey, skey=skey,
                        totalfind=0, usetime=0, curpage=1, pagecount=1,
                        res=None, getsize=None)
            return


        #查询结果
        allrv = self.GetAllSqlData(res)
        if allrv is None:
            self.render('results.html', title='搜索结果-%s' % skey, skey=skey,
                        totalfind=0, usetime=0, curpage=1, pagecount=1,
                        res=None, getsize=None)
            return

        #底部页码
        totalnum = float(res['total_found'])
        #还是限制最多出来1000个结果，避免过多出错
        if totalnum > 1000:
            totalnum = 1000
        echopage = float(limit)
        pagecount = ceil(totalnum / echopage)
        self.render('results.html', title='搜索结果-%s' % skey, skey=skey,
                    totalfind=res['total_found'], usetime=res['time'], curpage=current+1, pagecount=pagecount,
                    res=allrv, getsize=utils.GetFileSizeString)

    def get(self):
        skey = self.get_argument('q')
        page = int(self.get_argument('p'))
        keylen = len(skey)
        if keylen == 0:
            self.render('error.html', title='错误提示',errmsg='请输入要查找的内容。', errcode=600)
        elif keylen > 50:
            self.render('error.html', title='错误提示',errmsg='查找的内容过长，请缩短一点再试.', errcode=600)
        else:
            self.ShowResultPage(skey, page)


class IndexHandler(BaseAPI.BaseHandler):
    #@tornado.web.authenticated # 如果没有登陆，就自动跳转到登陆页面
    def get(self):
        # name = tornado.escape.xhtml_escape(self.current_user)
        # self.write("Hello, " + name + '<br>')
        # self.write("login Time : %s, login IP : %s<br>"
        #            %(self.session.get('logintime'),
        #              self.request.remote_ip))

        #self.RecordUV(self.request.remote_ip)

        totalbt = self.GetTotalNumStr()
        todaybt = self.GetTodayNumStr()
        stimes = self.GetTotalSearchTimesStr()
        top10 = self.GetSearchTop10Info()
        #UVtimes = self.GetUVStr()
        self.render('index.html', title='WWW.51PP.PW[我要片片]',keys=top10, newbt=todaybt, totalbt=totalbt, searchtimes=stimes)

    def post(self):
        pass    


    #记录用户访问统计信息
    # def RecordUV(self, userip):
    #     sqlstr = """SELECT idx, totalvisitor FROM traffic WHERE userip='%s'"""%userip
    #     rv = GxDB.Query(sqlstr)
    #
    #     if rv['error'] != 0:
    #         #没有就插入
    #         _sqlstr = """INSERT INTO "traffic" ("userip", "totalvisitor", "lastvisitortime")
    #                      VALUES ('%s', '1', now()) """%userip
    #         GxDB.Exec(_sqlstr)
    #
    #     else:
    #         #有就update
    #         fetchlist = rv['result']
    #         lastv = fetchlist[0]['totalvisitor']
    #         idx = fetchlist[0]['idx']
    #         _sqlstr = """UPDATE "traffic" SET "totalvisitor"='%d', "lastvisitortime"=now()
    #                      WHERE "idx" = %d"""%(lastv + 1, idx)
    #         GxDB.Exec(_sqlstr)


    @staticmethod
    def GetSearchTop10Info():
        sqlstr = """SELECT keywords FROM keywordstatistics ORDER BY times DESC LIMIT 10;"""
        rv = GxDB.Query(sqlstr)
        if rv['error'] != 0:
            return ''

        fetchlist = rv['result']
        if len(fetchlist) == 0:
            return ''

        rvlist = []
        num = 0
        for v in fetchlist:
            if num == 0:    labelstr = 'label label-danger'
            elif num == 1:  labelstr = 'label label-warning'
            elif num == 2:  labelstr = 'label label-primary'
            elif num == 3:  labelstr = 'label label-success'
            elif num == 4:  labelstr = 'label label-info'
            else:           labelstr = 'label label-default'

            vd = {'key': (v['keywords']), 'label': labelstr, 'url': '/search?q=%s&p=0'%v['keywords']}
            rvlist.append(vd)
            num += 1

        return rvlist

    @staticmethod
    def GetTotalNumStr():

        sqlstr = """SELECT count(idx) as totalnum FROM bttorrent;"""
        rv = GxDB.Query(sqlstr)
        if rv['error'] != 0:
            return ''

        fetchlist = rv['result']
        if len(fetchlist) == 0:
            return ''

        tonum = fetchlist[0]['totalnum']
        return str(tonum)

    # def GetUVStr(self):
    #         sqlstr = """SELECT SUM(totalvisitor) as uv FROM "traffic";"""
    #         rv = GxDB.Query(sqlstr)
    #         if rv['error'] != 0:
    #             return ''
    #
    #         fetchlist = rv['result']
    #         if len(fetchlist) == 0:
    #             return ''
    #
    #         tonum = fetchlist[0]['uv']
    #         return str(tonum)

    @staticmethod
    def GetTodayNumStr():
        sqlstr = """SELECT count(idx) as todaynum
                    FROM bttorrent WHERE buildtime >= current_date;"""
        rv = GxDB.Query(sqlstr)
        if rv['error'] != 0:
            return ''

        fetchlist = rv['result']
        if len(fetchlist) == 0:
            return ''

        tonum = fetchlist[0]['todaynum']
        return str(tonum)

    @staticmethod
    def GetTotalSearchTimesStr():
        sqlstr = """SELECT SUM(times) as stimes FROM keywordstatistics;"""
        rv = GxDB.Query(sqlstr)
        if rv['error'] != 0:
            return ''

        fetchlist = rv['result']
        if len(fetchlist) == 0:
            return ''

        tonum = fetchlist[0]['stimes']
        return str(tonum)









