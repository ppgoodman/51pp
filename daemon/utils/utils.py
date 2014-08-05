#!/usr/bin/python
# -*- coding: utf8 -*-


import hashlib
import random
import string
import time


#convert string to hex
def toHex(s):
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)

    return reduce(lambda x,y:x+y, lst)

#convert hex repr to string
def toStr(s):
    return s and chr(string.atoi(s[:2], base=16)) + toStr(s[2:]) or ''



def PrintHEX(msg):
    for i in range(0,16):
        print "%3s" % hex(i) ,
    print
    for i in range(0,16):
        print "%3s" % "##" ,
    print
    index = 0
    for temp in msg:
        print "%3s" % temp.encode('hex'),
        index = index+1
        if index == 16:
            index = 0
            print

# This class provides the functionality we want. You only need to look at
# this if you want to know how this works. It only needs to be defined
# once, no need to muck around with its internals.
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:  # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


#获取当前时间，格式YYYY-MM-DD_HHMMSS,这个一般是作为文件名用，因为文件名不能用冒号
def GetCurrentTime():
    return time.strftime('%Y-%m-%d_%H%M%S',time.localtime(time.time()))

#数据库填写当前datetime字段用的格式：YYYY-MM-DD HH:MM:SS
def GetDateTime(timestamp=None):
    if timestamp is None:
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    else:
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(timestamp))

#就是time.time()得到的时间，这个是从'%Y-%m-%d %H:%M:%S'格式转换为18289423.23这种格式，用于计算时间间隔
def GetTimpStamp(timestr):
    if timestr is None:
        return 0
    return time.mktime(time.strptime(str(timestr), '%Y-%m-%d %H:%M:%S'))

#获取一个占位用的时间，1970-01-01 08:00:00, 转换为时间戳为0.0
def GetNullDateTime():
    return '1970-01-01 08:00:00'

def isFloatEqual(f1, f2):
     if abs(abs(f1) - abs(f2)) < 0.000001:
         return True
     return False


#根据单位得到这个单位的时间长度（秒单位）
def GetSecondByUnit(unit):
    second = 0
    for case in switch(unit):
        if case('hour'):
            second = 3600
            break

        if case('day'):
            second = 86400
            break

        if case('month'):
            second = 2592000
            break

        if case('year'):
            second = 31104000
            break

        if case():
            break

    return second


def GetFileMD5(fdfile):
    md5obj = hashlib.md5()
    md5obj.update(fdfile.read())
    hash = md5obj.hexdigest().upper()
    fdfile.seek(0)
    return hash

def GetMD5(str):
    m0=hashlib.md5()
    m0.update(str)
    return m0.hexdigest().upper()

def EncrypPassword(orgStr):
    magic = '@godbless$'
    orgStr = magic + orgStr
    orgStr += str(len(orgStr)*23)
    return GetMD5(orgStr)


def GenerateRandomIntNum(min, max):
    return int(random.randint(min, max))

def CreateGUID(prefix):
    gen = GenerateRandomString(30, False)
    return '%s_%s'%(prefix, gen.lower())


#withpunctuation是否带标点符号
def GenerateRandomString(length, withpunctuation = True):
    '''
    Linux正则命名参考：http://vbird.dic.ksu.edu.tw/linux_basic/0330regularex.php#lang
    [:alnum:]	代表英文大小写字节及数字，亦即 0-9, A-Z, a-z
    [:alpha:]	代表任何英文大小写字节，亦即 A-Z, a-z
    [:blank:]	代表空白键与 [Tab] 按键两者
    [:cntrl:]	代表键盘上面的控制按键，亦即包括 CR, LF, Tab, Del.. 等等
    [:digit:]	代表数字而已，亦即 0-9
    [:graph:]	除了空白字节 (空白键与 [Tab] 按键) 外的其他所有按键
    [:lower:]	代表小写字节，亦即 a-z
    [:print:]	代表任何可以被列印出来的字节
    [:punct:]	代表标点符号 (punctuation symbol)，亦即：" ' ? ! ; : # $...
    [:upper:]	代表大写字节，亦即 A-Z
    [:space:]	任何会产生空白的字节，包括空白键, [Tab], CR 等等
    [:xdigit:]	代表 16 进位的数字类型，因此包括： 0-9, A-F, a-f 的数字与字节

    Python自带常量(本例中改用这个，不用手工定义了)
    string.digits		  #十进制数字：0123456789
    string.octdigits	   #八进制数字：01234567
    string.hexdigits	   #十六进制数字：0123456789abcdefABCDEF
    string.ascii_lowercase #小写字母(ASCII)：abcdefghijklmnopqrstuvwxyz
    string.ascii_uppercase #大写字母(ASCII)：ABCDEFGHIJKLMNOPQRSTUVWXYZ
    string.ascii_letters   #字母：(ASCII)abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
    string.punctuation	 #标点符号：!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~

    以下的不用，有locale问题
    string.lowercase	   #abcdefghijklmnopqrstuvwxyz
    string.uppercase	   #ABCDEFGHIJKLMNOPQRSTUVWXYZ
    string.letters		 #ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz

    以下的不能用
    string.whitespace	  #On most systems this includes the characters space, tab, linefeed, return, formfeed, and vertical tab.
    string.printable	   #digits, letters, punctuation, and whitespace
    '''
    punctuation = '!$%^&*'

    passwd_seed = string.digits + string.ascii_letters

    if withpunctuation:
        passwd_seed = passwd_seed + punctuation

    passwd = []
    while (len(passwd) < length):
        passwd.append(random.choice(passwd_seed))
    return ''.join(passwd)

# --exeTime
#测试函数执行时间，使用方法，在函数的上一行写@TestExeTime即可
def TestExeTime(func):
    def newFunc(*args, **args2):
        t0 = time.time()
        #print "@%s, {%s} start" % (time.strftime("%X", time.localtime()), func.__name__)
        back = func(*args, **args2)
        #print "@%s, {%s} end" % (time.strftime("%X", time.localtime()), func.__name__)
        print "@%.3fms taken for {%s}" % ((time.time() - t0) * 1000, func.__name__)
        return back
    return newFunc
# --end of exeTime












