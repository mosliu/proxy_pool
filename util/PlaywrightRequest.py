# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     PlaywrightRequest
   Description :   Playwright-based Network Requests Class
   Author :        Your Name
   date：          Current Date
-------------------------------------------------
"""
__author__ = 'Your Name'

from playwright.sync_api import sync_playwright, Page, Browser
from typing import Optional
import random
import time

from handler.logHandler import LogHandler

class PlaywrightRequest:
    name = "playwright_request"
    _instance = None
    _browser: Optional[Browser] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlaywrightRequest, cls).__new__(cls)
            cls._instance.log = LogHandler(cls.name, file=False)
            cls._instance.playwright = sync_playwright().start()
            cls._instance._browser = cls._instance.playwright.chromium.launch(headless=True)
        return cls._instance

    def __init__(self):
        self.page: Optional[Page] = None

    @property
    def user_agent(self):
        """
        返回随机的User-Agent
        """
        ua_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        ]
        return random.choice(ua_list)

    def get(self, url: str, retry_time: int = 3, retry_interval: int = 5, timeout: int = 30, *args, **kwargs):
        """
        使用Playwright执行GET请求
        """
        if(timeout < 500):
            # 如果timeout小于500 应该是指的秒，默认乘以1000
            timeout = timeout * 1000
        while retry_time > 0:
            try:
                if not self.page:
                    self.page = self._browser.new_page(user_agent=self.user_agent)
                
                self.page.set_default_timeout(timeout)
                response = self.page.goto(url, wait_until='networkidle', *args, **kwargs)
                return self
            except Exception as e:
                self.log.error(f"playwright请求: {url} 错误: {str(e)}")
                retry_time -= 1
                if retry_time <= 0:
                    self.log.error(f"请求 {url} 失败,已达到最大重试次数")
                    return self
                self.log.info(f"{retry_interval} 秒后重试")
                time.sleep(retry_interval)

    @property
    def content(self):
        return self.page.content() if self.page else ""

    @property
    def text(self):
        return self.page.inner_text('body') if self.page else ""

    def close(self):
        if self.page:
            self.page.close()
            self.page = None

    def __del__(self):
        if self._browser:
            self._browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()

# 使用示例
if __name__ == "__main__":
    pr = PlaywrightRequest()
    pr.get("https://www.example.com")
    print(pr.text)
    pr.close()
