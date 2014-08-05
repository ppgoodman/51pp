#!/usr/bin/env python
#-*- coding: utf-8 -*-
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool


#using example
class xDB(object):
    def __init__(self):
        self.pgpool = SimpleConnectionPool(minconn=1, maxconn=10, host='localhost', database='p2pworld',
                                                           user='postgres',
                                                           password='123kkk', port=5432)
        self._db = None
        self.trans = {}

    def __del__(self):
        self.pgpool.closeall()


    #执行查询，返回结果list
    def Query(self, sqlstr):
        rv = {}
        try:
            db = self.pgpool.getconn()
            db.autocommit = True
            cur = db.cursor(cursor_factory=RealDictCursor)
            cur.execute(sqlstr)
            _fetch = cur.fetchall()
            if len(_fetch) == 0:
                rv['error'] = 800
                rv['result'] = 'result NULL'
                return rv

            rv['error'] = 0
            rv['result'] = _fetch

        except Exception, e:
            rv['error'] = 800
            rv['result'] = 'ERR: %s' % (repr(e))

        finally:
            self.pgpool.putconn(db)

        return rv

    #执行插入或者更新，返回true或者false
    def Exec(self, sqlstr):
        try:
            db = self.pgpool.getconn()
            db.autocommit = True
            cur = db.cursor()
            #self.write(sqlstr + '<br>')
            #cur.execute(‘INSERT INTO test (a, b) VALUES (%s, %s) RETURNING id;’, (‘a’, ‘b’))
            cur.execute(sqlstr)
            #self.db.commit()  #放到这里要快的多，等于上面的全部执行了
        except Exception, e:
            print '[sqlerrror]' + repr(e)
            return False
        finally:
            self.pgpool.putconn(db)
        return True

    def TransExec(self, sqlstr):
        self.application.trans.append(sqlstr)

    def TransCommit(self):
        try:
            db = self.pgpool.getconn()
            db.autocommit = False
            cur = db.cursor()

            for sqlstr in self.trans:
                cur.execute(sqlstr)

            db.commit()  #放到这里要快的多，等于上面的全部执行了
            self.trans = []
        except Exception, e:
            db.rollback()
            self.trans = []
            print '[sqlerror]' + repr(e)
            return False
        finally:
            self.pgpool.putconn(db)

        return True


GxDB = xDB()
