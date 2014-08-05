#!/usr/bin/python
# -*- coding: utf8 -*-
import logging
import os
import utils
import uuid

class BLog():
	def __init__(self, logname, withuuid=True):
		print 'Init Log System...'
		if not os.path.exists('log') :
			os.mkdir('log')
		# 创建一个self.logger
		if withuuid :
			logname = logname + '_' + str(uuid.uuid1())
		self.logger = logging.getLogger(logname)
		self.logger.setLevel(logging.INFO)

		# 创建一个handler，用于写入日志文件
		filename = 'log/%s_%s.log'%(logname, utils.GetCurrentTime())
		fh = logging.FileHandler(filename)
		fh.setLevel(logging.INFO)

		# 再创建一个handler，用于输出到控制台
		ch = logging.StreamHandler()
		ch.setLevel(logging.INFO)

		# 定义handler的输出格式
		#'%(asctime)s-%(name)s-%(levelname)s-%(message)s'
		formatter = logging.Formatter('[%(asctime)s]%(message)s')
		fh.setFormatter(formatter)
		ch.setFormatter(formatter)

		# 给self.logger添加handler
		self.logger.addHandler(fh)
		self.logger.addHandler(ch)

	def __del__(self):
		print 'Shutdown Log System...'	
		#logging.shutdown() #tornado给释放了，这里不需要释放了

	def Log(self, message, msgbox = None, withreturn = True):
		self.logger.info(message)
		if msgbox != None:
			if withreturn == True:
				_outmsg = message + '\n'
			else:
				_outmsg = message

			msgbox.insert('end', _outmsg)



#全局定义
GLog = BLog('App')