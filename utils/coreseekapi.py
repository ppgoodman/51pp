#!/usr/bin/python
#-*- encoding:utf-8 -*-
from sphinxapi import *

#参数limit为每次查询的最大数
def clQuery(s_keyword, currentpage=0, limit=10):

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
    cl = SphinxClient()
    #cl.SetMaxQueryTime(10);
    cl.SetServer ( '127.0.0.1', 9312);
    #cl.SetConnectTimeout ( 3 );
    #cl.SetArrayResult ( true );
    cl.SetMatchMode ( SPH_MATCH_EXTENDED);
    cl.SetLimits(currentpage * limit, limit); #每页条目数
    cl.SetSortMode ( SPH_SORT_ATTR_DESC, "hits" );
    cl.SetSortMode(SPH_SORT_RELEVANCE);
    res = cl.Query ( s_keyword, '*' );

    #更深度的找
    if res is not None and res['total_found'] == 0:
        cl.SetMatchMode (SPH_MATCH_ANY)
        cl.SetSortMode(SPH_SORT_RELEVANCE)
        cl.SetSortMode ( SPH_SORT_ATTR_DESC, "hits" )
        res = cl.Query ( s_keyword, "*" )

    #print res
    return res
    #self.write("<br>总数: %s 时间消耗: %s 秒<hr>"%(res['total_found'], res['time']))

