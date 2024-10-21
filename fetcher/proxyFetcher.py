# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyFetcher
   Description :
   Author :        JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: proxyFetcher
-------------------------------------------------
"""
__author__ = 'JHao'

import re
import json
from time import sleep

from util.webRequest import WebRequest
from util.PlaywrightRequest import PlaywrightRequest

# 新增导入
import requests
from bs4 import BeautifulSoup
import random
from fake_useragent import UserAgent
import datetime


class ProxyFetcher(object):
    """
    proxy getter
    """

    @staticmethod
    def freeProxy01():
        """
        站大爷 https://www.zdaye.com/dayProxy.html
        """
        start_url = "https://www.zdaye.com/dayProxy.html"
        html_tree = WebRequest().get(start_url, verify=False).tree
        latest_page_time = html_tree.xpath("//span[@class='thread_time_info']/text()")[0].strip()
        from datetime import datetime
        interval = datetime.now() - datetime.strptime(latest_page_time, "%Y/%m/%d %H:%M:%S")
        if interval.seconds < 300:  # 只采集5分钟内的更新
            target_url = "https://www.zdaye.com/" + html_tree.xpath("//h3[@class='thread_title']/a/@href")[0].strip()
            while target_url:
                _tree = WebRequest().get(target_url, verify=False).tree
                for tr in _tree.xpath("//table//tr"):
                    ip = "".join(tr.xpath("./td[1]/text()")).strip()
                    port = "".join(tr.xpath("./td[2]/text()")).strip()
                    yield "%s:%s" % (ip, port)
                next_page = _tree.xpath("//div[@class='page']/a[@title='下一页']/@href")
                target_url = "https://www.zdaye.com/" + next_page[0].strip() if next_page else False
                sleep(5)

    @staticmethod
    def freeProxy02():
        """
        代理66 http://www.66ip.cn/
        """
        url = "http://www.66ip.cn/"
        resp = WebRequest().get(url, timeout=10).tree
        for i, tr in enumerate(resp.xpath("(//table)[3]//tr")):
            if i > 0:
                ip = "".join(tr.xpath("./td[1]/text()")).strip()
                port = "".join(tr.xpath("./td[2]/text()")).strip()
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy03():
        """ 开心代理 """
        target_urls = ["http://www.kxdaili.com/dailiip.html", "http://www.kxdaili.com/dailiip/2/1.html"]
        for url in target_urls:
            tree = WebRequest().get(url).tree
            for tr in tree.xpath("//table[@class='active']//tr")[1:]:
                ip = "".join(tr.xpath('./td[1]/text()')).strip()
                port = "".join(tr.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy04():
        """ FreeProxyList https://www.freeproxylists.net/zh/ """
        url = "https://www.freeproxylists.net/zh/?c=CN&pt=&pr=&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=50"
        tree = WebRequest().get(url, verify=False).tree
        from urllib import parse

        def parse_ip(input_str):
            html_str = parse.unquote(input_str)
            ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', html_str)
            return ips[0] if ips else None

        for tr in tree.xpath("//tr[@class='Odd']") + tree.xpath("//tr[@class='Even']"):
            ip = parse_ip("".join(tr.xpath('./td[1]/script/text()')).strip())
            port = "".join(tr.xpath('./td[2]/text()')).strip()
            if ip:
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy05(page_count=1):
        """ 快代理 https://www.kuaidaili.com """
        url_pattern = [
            'https://www.kuaidaili.com/free/inha/{}/',
            'https://www.kuaidaili.com/free/intr/{}/'
        ]
        url_list = []
        for page_index in range(1, page_count + 1):
            for pattern in url_pattern:
                url_list.append(pattern.format(page_index))

        for url in url_list:
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            sleep(1)  # 必须sleep 不然第二条请求不到数据
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])

    @staticmethod
    def freeProxy06():
        """ 冰凌代理 https://www.binglx.cn """
        url = "https://www.binglx.cn/?page=1"
        try:
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])
        except Exception as e:
            print(e)

    @staticmethod
    def freeProxy07():
        """ 云代理 """
        urls = ['http://www.ip3366.net/free/?stype=1', "http://www.ip3366.net/free/?stype=2"]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy08():
        """ 小幻代理 """
        urls = ['https://ip.ihuan.me/address/5Lit5Zu9.html']
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</a></td><td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy09(page_count=1):
        """ 免费代理库 """
        for i in range(1, page_count + 1):
            url = 'http://ip.jiangxianli.com/?country=中国&page={}'.format(i)
            html_tree = WebRequest().get(url, verify=False).tree
            for index, tr in enumerate(html_tree.xpath("//table//tr")):
                if index == 0:
                    continue
                yield ":".join(tr.xpath("./td/text()")[0:2]).strip()

    @staticmethod
    def freeProxy10():
        """ 89免费代理 """
        r = WebRequest().get("https://www.89ip.cn/index_1.html", timeout=10)
        proxies = re.findall(
            r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
            r.text)
        for proxy in proxies:
            yield ':'.join(proxy)

    @staticmethod
    def freeProxy11():
        """ 稻壳代理 https://www.docip.net/ """
        r = WebRequest().get("https://www.docip.net/data/free.json", timeout=10)
        try:
            for each in r.json['data']:
                yield each['ip']
        except Exception as e:
            print(e)

    @staticmethod
    def freeProxy12():
        """ 获取free-proxy-list.net上的代理 """
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        proxies = []
        for row in soup.find('table', class_='table table-striped table-bordered').tbody.find_all('tr'):
            columns = row.find_all('td')
            ip_address = columns[0].text
            port = columns[1].text
            https = columns[6].text
            anonymity = columns[4].text
            if https == 'yes' and anonymity == 'elite proxy':
                yield f"{ip_address}:{port}"

    @staticmethod
    def freeProxy13():
        """ proxy-list.download 一整页代理 随机20个 """
        url ='https://www.proxy-list.download/api/v2/get?l=en&t=https'
        response = requests.get(url, headers={'User-Agent': UserAgent().random})
        if response.status_code == 200:
            data = json.loads(response.text)
            ip_port_list = [f"{item['IP']}:{item['PORT']}" for item in data['LISTA']]
            if len(ip_port_list) >= 20:
                return random.sample(ip_port_list, 20)
            else:
                return ip_port_list
        else:
            print('Failed to retrieve the webpage')
            print(response.status_code)
            return []

    @staticmethod
    def freeProxy14():
        """ 66ip.cn 获取20个 """
        url ='http://www.66ip.cn/nmtq.php?getnum=20&isp=0&anonymoustype=4&start=&ports=&export=&ipaddress=&area=0&proxytype=1&api=66ip'
        response = requests.get(url, headers={'User-Agent': UserAgent().random})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            ip_port_list = soup.text.split('\r\n')[2:]
            return [item.strip() for item in ip_port_list if item.strip()]
        else:
            print('Failed to retrieve the webpage')
            print(response.status_code)
            return []

    @staticmethod
    def freeProxy15():
        """ 开心代理 随机三页代理 """
        def get_page_proxies(page_url):
            response = requests.get(page_url, headers={'User-Agent': UserAgent().random})
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                ip_table = soup.find('table', class_='active')
                ip_rows = ip_table.find_all('tr')[1:]
                for row in ip_rows:
                    tds = row.find_all('td')
                    if tds[3].text == 'HTTP,HTTPS' and tds[4].text[0] in ['1','2','0']:
                        yield f"{tds[0].text}:{tds[1].text}"
            else:
                print('Failed to retrieve the webpage')
                print(response.status_code)

        base_url = 'http://www.kxdaili.com/dailiip/1/{}.html'
        page_count = 10  # 假设有10页
        random_pages = random.sample(range(1, page_count + 1), 3)
        
        for page in random_pages:
            yield from get_page_proxies(base_url.format(page))

    @staticmethod
    def freeProxy16():
        """ 小幻代理 20个 """
        current_time = datetime.datetime.now().strftime('%Y/%m/%d/%H')
        url = f'https://ip.ihuan.me/today/{current_time}.html'
        # res = WebRequest().get(url, timeout=10)
        # res1 = PlaywrightRequest().get('https://lowjs.com', timeout=30)
        response = requests.get(url, headers={'User-Agent': UserAgent().random})

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            ip_port_list = []
            for item in soup.find('p', class_='text-left'):
                if '#支持HTTPS#支持POST' in str(item) and '#[高匿]' in str(item) and ':' in str(item):
                    ip_port_list.append(str(item).split('@')[0])
            return ip_port_list
        else:
            print('Failed to retrieve the webpage')
            print(response.status_code)
            return []


if __name__ == '__main__':
    p = ProxyFetcher()
    for _ in p.freeProxy01():
        print(_)

# http://nntime.com/proxy-list-01.htm
