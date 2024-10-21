# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyScheduler
   Description :
   Author :        JHao
   date：          2019/8/5
-------------------------------------------------
   Change Activity:
                   2019/08/05: proxyScheduler
                   2021/02/23: runProxyCheck时,剩余代理少于POOL_SIZE_MIN时执行抓取
-------------------------------------------------
"""
__author__ = 'JHao'

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

from util.six import Queue
from helper.fetch import Fetcher
from helper.check import Checker
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler
from handler.vipProxyHandler import VIPProxyHandler

scheduler_log = LogHandler("scheduler")

def __runProxyFetch():
    proxy_queue = Queue()
    proxy_fetcher = Fetcher()

    for proxy in proxy_fetcher.run():
        proxy_queue.put(proxy)

    Checker("raw", proxy_queue)


def __runProxyCheck():
    proxy_handler = ProxyHandler()
    proxy_queue = Queue()
    if proxy_handler.db.getCount().get("total", 0) < proxy_handler.conf.poolSizeMin:
        __runProxyFetch()
    for proxy in proxy_handler.getAll():
        proxy_queue.put(proxy)
    Checker("use", proxy_queue)


def __runVIPProxyFetch():
    vip_proxy_queue = Queue()  # 使用相同的 Queue 类
    vip_proxy_handler = VIPProxyHandler()
    
    for proxy in vip_proxy_handler.fetch():
        vip_proxy_queue.put(proxy)
    
    Checker("vip", vip_proxy_queue)
    
    # 将 VIP 代理存储到 Redis
    for _ in range(vip_proxy_queue.qsize()):
        proxy = vip_proxy_queue.get()
        vip_proxy_handler.put(proxy)


def __runVIPProxyCheck():
    scheduler_log.info("Start check VIP proxy")
    vip_proxy_handler = VIPProxyHandler()
    vip_proxy_queue = Queue()
    # if vip_proxy_handler.getCount().get("total", 0) < vip_proxy_handler.conf.vipPoolSizeMin:
    #     for proxy in vip_proxy_handler.fetch():
    #         vip_proxy_handler.put(proxy)
    for proxy in vip_proxy_handler.getAll():
        vip_proxy_queue.put(proxy)
    Checker("vip", vip_proxy_queue)


def runScheduler():
    
    scheduler_log.info("Scheduler start!")
    config_handler = ConfigHandler()


    timezone = ConfigHandler().timezone
    
    scheduler = BlockingScheduler(logger=scheduler_log, timezone=timezone)

    
    if config_handler.enableFreeProxy:
        scheduler_log.info("Enable free proxy, start fetch free proxy")
        __runProxyFetch()
        scheduler.add_job(__runProxyFetch, 'interval', minutes=4, id="proxy_fetch", name="proxy采集")
        scheduler.add_job(__runProxyCheck, 'interval', minutes=2, id="proxy_check", name="proxy检查")
    else:
        scheduler_log.info("Disable free proxy, skip fetch free proxy")
    
    # VIP代理相关的任务保持不变
    # scheduler.add_job(__runVIPProxyFetch, 'interval', minutes=30, id="vip_proxy_fetch", name="VIP代理采集")
    scheduler_log.info("Enable VIP proxy, start check VIP proxy")
    scheduler.add_job(__runVIPProxyCheck, 'interval', minutes=1, id="vip_proxy_check", name="VIP代理检查")
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 20},
        'processpool': ProcessPoolExecutor(max_workers=5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 10
    }

    scheduler.configure(executors=executors, job_defaults=job_defaults, timezone=timezone)

    scheduler.start()


if __name__ == '__main__':
    runScheduler()
