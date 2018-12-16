import sys
import time
import utils
from crawler import Crawler
from conredis import RedisClient

class Getter():
    def __init__(self, pid):
        self.redis = RedisClient()
        self.crawler = Crawler()
        self.POOL_UPPER_THRESHOLD = utils.config()["POOL_UPPER_THRESHOLD"]
        self.pid = pid

    def is_over_threshold(self):
        """
        判断代理池是否已经达到上限
        :return:
        """
        if self.redis.count() >= self.POOL_UPPER_THRESHOLD:
            return True
        elif self.POOL_UPPER_THRESHOLD == 0:
            return False
        else:
            return False

    def run(self):
        try:
            print("代理获取模块/getter开始运行，本次运行开始时间为：{}".format(time.ctime()).upper())
            sys.stdout.flush()
            if not self.is_over_threshold():
                for callback_label in range(self.crawler.__CrawlFuncCount__):
                    callback = self.crawler.__CrawlFunc__[callback_label]
                    proxies = self.crawler.get_proxies(callback)
                    if not proxies:
                        for proxy in proxies:
                            self.redis.add(proxy)
            print("代理获取模块/getter运行完成，本次运行结束时间为：{}".format(time.ctime()).upper())
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.flush()
            print(utils.info("(程序主动退出！)代理获取模块/getter发生错误，请尽快修复：{}".format(e)))
            utils.kill(self.pid)
