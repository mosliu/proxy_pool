# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyHandler.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/03:
                   2020/05/26: 区分http和https
-------------------------------------------------
"""
__author__ = 'JHao'

from helper.proxy import Proxy
from db.dbClient import DbClient
from handler.configHandler import ConfigHandler
from handler.logHandler import LogHandler

log = LogHandler("ProxyHandler")

class ProxyHandler(object):
    """ Proxy CRUD operator"""

    def __init__(self):
        self.conf = ConfigHandler()
        self.db = DbClient(self.conf.dbConn)
        self.tableName = self.conf.tableName
        self.db.changeTable(self.tableName)
        log.info(f"代理数据库表: {self.db.getTable()}")

    def get(self, https=False):
        """
        return a proxy
        Args:
            https: True/False
        Returns:
        """
        self.db.changeTable(self.tableName)
        log.info(f"代理数据库表: {self.db.getTable()}")
        proxy = self.db.get(https)
        return Proxy.createFromJson(proxy) if proxy else None

    def pop(self, https):
        """
        return and delete a useful proxy
        :return:
        """
        self.db.changeTable(self.tableName)
        proxy = self.db.pop(https)
        if proxy:
            return Proxy.createFromJson(proxy)
        return None

    def put(self, proxy):
        """
        put proxy into use proxy
        :return:
        """
        self.db.changeTable(self.tableName)
        self.db.put(proxy)

    def delete(self, proxy):
        """
        delete useful proxy
        :param proxy:
        :return:
        """
        self.db.changeTable(self.tableName)
        return self.db.delete(proxy.proxy)

    def getAll(self, https=False):
        """
        get all proxy from pool as Proxy list
        :return:
        """
        self.db.changeTable(self.tableName)
        proxies = self.db.getAll(https)
        return [Proxy.createFromJson(_) for _ in proxies]

    def exists(self, proxy):
        """
        check proxy exists
        :param proxy:
        :return:
        """
        self.db.changeTable(self.tableName)
        return self.db.exists(proxy.proxy)

    def getCount(self):
        """
        return raw_proxy and use_proxy count
        :return:
        """
        self.db.changeTable(self.tableName)
        total_use_proxy = self.db.getCount()
        return {'count': total_use_proxy}
