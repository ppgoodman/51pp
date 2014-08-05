#encoding: utf-8
#infohash组成磁力链接到迅雷种子库下载种子(thunder.py)
import socket
from time import time

import requests
from bencode import bdecode

from torrent import *
import sys

class thunder(object):
    def __init__(self, store=None):
        self.cache = {}
        self.store = store

    def download(self, infohash):
        info = {}
        try:
            self.cache[infohash] += 1
        except KeyError:
            self.cache[infohash] = 1
            tc = self._download(infohash)
            try:
                tc = bdecode(tc)
                info = torrentinfo(tc)
                hot = self.cache[infohash]
            except Exception, e:
                print '[bdecod error]' + repr(e)
            finally:
                del self.cache[infohash]
                return info

    def _download(self, infohash):
        infohash = infohash.upper()
        start = infohash[0:2]
        end = infohash[-2:]

        url = "http://bt.box.n0808.com/%s/%s/%s.torrent" % (start, end, infohash)
        headers = {
            "referer": "http://bt.box.n0808.com"
        }
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                return r.content

        except (socket.timeout, requests.exceptions.timeout), e:
            print '[requests error]' + repr(e)
        return ""


def main(argv):
    th = thunder()
    th.download(argv[1])


if __name__ == '__main__':
    main(sys.argv)
