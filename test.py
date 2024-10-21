# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test.py  
   Description :  
   Author :       JHao
   date：          2017/3/7
-------------------------------------------------
   Change Activity:
                   2017/3/7: 
-------------------------------------------------
"""
__author__ = 'JHao'

from test import testProxyValidator
from test import testConfigHandler
from test import testLogHandler
from test import testDbClient
from test import testProxyClass
from fetcher.proxyFetcher import ProxyFetcher  # 添加这行导入

if __name__ == '__main__':
   #  print("ConfigHandler:")
   #  testConfigHandler.testConfig()

   #  print("LogHandler:")
   #  testLogHandler.testLogHandler()

   #  print("DbClient:")
   #  testDbClient.testDbClient()

   #  print("ProxyValidator:")
   #  testProxyValidator.testProxyValidator()

   testProxyClass.testProxyClass()

   #  print("ProxyFetcher:")
   #  fetcher = ProxyFetcher()
   #  for proxy in fetcher.freeProxy14():
   #      print(proxy)
