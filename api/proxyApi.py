# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyApi.py
   Description :   WebApi
   Author :       JHao
   date：          2016/12/4
-------------------------------------------------
   Change Activity:
                   2016/12/04: WebApi
                   2019/08/14: 集成Gunicorn启动方式
                   2020/06/23: 新增pop接口
                   2022/07/21: 更新count接口
-------------------------------------------------
"""
__author__ = 'JHao'

import json
import platform
from datetime import datetime, timedelta
from werkzeug.wrappers import Response
from flask import Flask, jsonify, request

from util.six import iteritems
from helper.proxy import Proxy
from handler.configHandler import ConfigHandler
from handler.proxyHandler import ProxyHandler
from handler.vipProxyHandler import VIPProxyHandler

from handler.logHandler import LogHandler
log = LogHandler("ProxyApi")

app = Flask(__name__)
conf = ConfigHandler()
proxy_handler = ProxyHandler()
vip_proxy_handler = VIPProxyHandler()

# # ... 确保 VIPProxyHandler 使用正确的表名 ...
# vip_proxy_handler.db.changeTable(conf.vipTableName)
# log.info(f"VIP代理数据库表: {vip_proxy_handler.db.getTable()}")

class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)

        return super(JsonResponse, cls).force_type(response, environ)


app.response_class = JsonResponse

api_list = [
    {"url": "/get", "params": "type: ''https'|''", "desc": "get a proxy"},
    {"url": "/pop", "params": "", "desc": "get and delete a proxy"},
    {"url": "/delete", "params": "proxy: 'e.g. 127.0.0.1:8080'", "desc": "delete an unable proxy"},
    {"url": "/all", "params": "type: ''https'|''", "desc": "get all proxy from proxy pool"},
    {"url": "/count", "params": "", "desc": "return proxy count"},
    {"url": "/getvip", "params": "", "desc": "get a VIP proxy"},
    # 'refresh': 'refresh proxy pool',
]


@app.route('/')
def index():
    return {'url': api_list}


@app.route('/get/')
def get():
    log.info("获取代理")
    https = request.args.get("type", "").lower() == 'https'
    proxy = proxy_handler.get(https)
    return proxy.to_dict if proxy else {"code": 0, "src": "no proxy"}


@app.route('/pop/')
def pop():
    https = request.args.get("type", "").lower() == 'https'
    proxy = proxy_handler.pop(https)
    return proxy.to_dict if proxy else {"code": 0, "src": "no proxy"}


@app.route('/refresh/')
def refresh():
    # TODO refresh会有守护程序定时执行，由api直接调用性能较差，暂不使用
    return 'success'


@app.route('/all/')
def getAll():
    https = request.args.get("type", "").lower() == 'https'
    proxies = proxy_handler.getAll(https)
    return jsonify([_.to_dict for _ in proxies])


@app.route('/delete/', methods=['GET'])
def delete():
    proxy = request.args.get('proxy')
    status = proxy_handler.delete(Proxy(proxy))
    return {"code": 0, "src": status}


@app.route('/count/')
def getCount():
    proxies = proxy_handler.getAll()
    http_type_dict = {}
    source_dict = {}
    for proxy in proxies:
        http_type = 'https' if proxy.https else 'http'
        http_type_dict[http_type] = http_type_dict.get(http_type, 0) + 1
        for source in proxy.source.split('/'):
            source_dict[source] = source_dict.get(source, 0) + 1
    return {"http_type": http_type_dict, "source": source_dict, "count": len(proxies)}


@app.route('/getvip/')
def getVIP():
    log.info("获取VIP代理")
    https = request.args.get("type", "").lower() == 'https'
    
    while True:
        proxy = vip_proxy_handler.get(https)
        if not proxy:
            break
        proxy_dict = json.loads(proxy)
        # proxy_dict = eval(proxy)
        deadline = datetime.strptime(proxy_dict['deadline'], "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()
        
        if deadline > current_time + timedelta(seconds=15):
            log.info(f"REDIS获取到有效的VIP代理: {proxy}")
            return proxy
        else:
            log.info(f"删除过期的VIP代理: {proxy}")
            vip_proxy_handler.delete(Proxy(proxy_dict['proxy']))
    
    log.info("VIP队列为空或无有效代理, 从后台调用接口获取新的VIP代理")
    new_proxies = vip_proxy_handler.fetch(https)
    
    for new_proxy in new_proxies:
        if new_proxy:
            vip_proxy_handler.put(new_proxy)
            log.info(f"添加新的VIP代理: {new_proxy.to_dict}")
            return new_proxy.to_dict
    
    return {"code": 0, "src": "无可用的VIP代理"}

@app.route('/vip/count/')
def getVIPCount():
    vip_proxies = vip_proxy_handler.getAll()
    http_type_dict = {}
    for proxy in vip_proxies:
        http_type = 'https' if proxy.https else 'http'
        http_type_dict[http_type] = http_type_dict.get(http_type, 0) + 1
    return {"http_type": http_type_dict, "count": len(vip_proxies)}

@app.route('/vip/delete/')
def deleteVIP():
    proxy = request.args.get('proxy')
    status = vip_proxy_handler.delete(Proxy(proxy))
    return {"code": 0, "src": status}

@app.route('/vip/exists/')
def existsVIP():
    proxy = request.args.get('proxy')
    status = vip_proxy_handler.exists(Proxy(proxy))
    return {"code": 0, "exists": status}

@app.route('/vip/all/')
def getAllVIP():
    https = request.args.get("type", "").lower() == 'https'
    proxies = vip_proxy_handler.getAll(https)
    return {"code": 0, "proxies": [proxy.to_dict for proxy in proxies]}



def runFlask():
    if platform.system() == "Windows":
        app.run(host=conf.serverHost, port=conf.serverPort,debug=True)
    else:
        import gunicorn.app.base

        class StandaloneApplication(gunicorn.app.base.BaseApplication):

            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super(StandaloneApplication, self).__init__()

            def load_config(self):
                _config = dict([(key, value) for key, value in iteritems(self.options)
                                if key in self.cfg.settings and value is not None])
                for key, value in iteritems(_config):
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        _options = {
            'bind': '%s:%s' % (conf.serverHost, conf.serverPort),
            'workers': 4,
            'accesslog': '-',  # log to stdout
            'access_log_format': '%(h)s %(l)s %(t)s "%(r)s" %(s)s "%(a)s"'
        }
        StandaloneApplication(app, _options).run()


if __name__ == '__main__':
    runFlask()
