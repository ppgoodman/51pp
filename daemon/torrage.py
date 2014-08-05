#encoding: utf-8
#用infohash组成磁力链接到torrage.com下载种子文件(torrage.py)
import re
from utils.xDB import GxDB
from utils import utils

import requests
import gevent
from gevent import monkey
monkey.patch_all()
from bencode import bdecode

from torrent import *

jobs = 50
timeout = 10

def start():
    downloadhashfile()

def downloadpage():
    try:
        r = requests.get("http://torrage.com/sync", timeout=timeout*60)
        return r.content
    except Exception:
        return ""

def downloadhashfile():
    c = downloadpage()
    files = extractinfohashfiles(c)
    for file in files:
        temp = []
        #if infohashfilestore.exists(file): continue
        r = requests.get("http://torrage.com/sync/%s" % (file,))
        for infohash in r.iter_lines():
            if len(temp) == jobs:
                downtorrentingevent(temp)
                temp = []
            else:
                temp.append(infohash)
                #downtorrent(infohash, resourcestore)
        downtorrentingevent(temp)
        #infohashfilestore.save(file)

def downtorrentingevent(infohashes):
      jobs = [ gevent.spawn(downtorrent, infohash) for infohash in infohashes]
      gevent.joinall(jobs)


def downtorrent(infohash):
    try:
        r = requests.get("http://torrage.com/torrent/%s.torrent" % (infohash, ), timeout=timeout)
        if r.status_code==200:
            tc = bdecode(r.content)
            info = torrentinfo(tc)
            print '---> wang wang! <---%s'%info['name']

            name = info['name'].replace('\'','\'\'')
            files = info["files"].replace('\'','\'\'')

            sqlstr = """INSERT INTO "bttorrent" (infohash, name, length, buildtime, files, hits, downloads)
                        VALUES ('%s', '%s', '%s', '%s', '%s','0','0') """%\
                     (infohash, name, info["length"], utils.GetDateTime(info["timestamp"]), files)
            #print sqlstr
            GxDB.Exec(sqlstr)

            # resourcestore.save(infohash=infohash, name=info["name"],
            #     length=info["length"], timestamp=info["timestamp"],
            #     files=info["files"], hot=1)
    except Exception, e:
        print 'downtorrent err:' + repr(e)

def extractinfohashfiles(content):
    c = re.compile(r'<a href="(\d{8}\.txt)">')
    return c.findall(content)


import sys

def main(argv):
    start()

        
if __name__ == '__main__':
    main(sys.argv)