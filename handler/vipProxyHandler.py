# -*- coding: utf-8 -*-

import requests
import json
from handler.configHandler import ConfigHandler
from helper.proxy import Proxy
from db.dbClient import DbClient
from handler.logHandler import LogHandler
log = LogHandler("VIPProxyHandler")

class VIPProxyHandler:
    def __init__(self):
        self.conf = ConfigHandler()
        self.db = DbClient(self.conf.dbConn)
        self.vipTableName = self.conf.vipTableName
        self.db.changeTable(self.vipTableName)
        log.info(f"VIP代理数据库表: {self.db.getTable()}")

    def fetch(self, https=False):
        params = {
            "key": self.api_key,
            "num": 1,  # 增加获取的代理数量
            "distinct": True
        }
        try:
            resp = requests.get(self.api_url, params=params)
            log.info(f"获取VIP代理: {resp.text}")
            if resp.status_code == 200:
                data = json.loads(resp.text)
                if data["code"] == "SUCCESS" and data["data"]:
                    for proxy_info in data["data"]:
                        proxy = Proxy(proxy=proxy_info["server"], source="VIP", https=https,
                                      region=proxy_info["area"], isp=proxy_info["isp"],
                                      deadline=proxy_info["deadline"])
                        proxy.out_ip = proxy_info["proxy_ip"]
                        yield proxy
        except Exception as e:
            log.error(f"获取VIP代理时发生错误: {str(e)}")

    def get(self, https=False):
        self.db.changeTable(self.vipTableName)
        return self.db.get(https)

    def pop(self, https):
        self.db.changeTable(self.vipTableName)
        return self.db.pop(https)

    def put(self, proxy):
        self.db.changeTable(self.vipTableName)
        self.db.put(proxy)

    def delete(self, proxy):
        self.db.changeTable(self.vipTableName)
        return self.db.delete(proxy.proxy)

    def getAll(self, https=False):
        self.db.changeTable(self.vipTableName)
        return [Proxy.createFromJson(_) for _ in self.db.getAll(https)]

    def exists(self, proxy):
        self.db.changeTable(self.vipTableName)
        return self.db.exists(proxy.proxy)

    def getCount(self):
        self.db.changeTable(self.vipTableName)
        return self.db.getCount()
