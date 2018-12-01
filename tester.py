import sys
import time
import utils
import asyncio
import aiohttp
from hashlib import md5
from conredis import RedisClient
from aiohttp.client_exceptions import ClientError, ClientConnectionError

class Tester():
    def __init__(self, pid):
        conf = utils.config()
        self.redis = RedisClient()
        self.VALID_STATUS_CODES = conf["VALID_STATUS_CODES"]
        self.TEST_URL = conf["TEST_URL"]
        self.BATCH_TEST_SIZE = conf["BATCH_TEST_SIZE"]
        self.pid = pid

    async def test_single_proxy(self, proxy):
        """
        测试单个代理
        :param proxy:代理
        :return: None
        """
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode("utf-8")
                real_proxy = "http://"+proxy
                async with session.get(self.TEST_URL, proxy=real_proxy, timeout=15) as resp:
                    if resp.status in self.VALID_STATUS_CODES:
                        self.redis.max(proxy)
                    else:
                        self.redis.decrease(proxy)
            except (ClientError, ClientConnectionError, asyncio.TimeoutError, AttributeError):
                self.redis.decrease(proxy)

    def run(self):
        """
        测试主函数
        :return: None
        """
        sessionid = md5()
        sessionid.update(str(time.time()).encode("utf-8"))
        sessionid = sessionid.hexdigest()
        print("(id:{})代理测试模块/tester开始运行，本次运行开始时间为：{}".format(sessionid, time.ctime()).upper())
        sys.stdout.flush()
        try:
            count = self.redis.count()
            #批量测试
            for i in range(0, count, self.BATCH_TEST_SIZE):
                stop = min(i+self.BATCH_TEST_SIZE, count)
                test_proxies = self.redis.batch(i, stop)
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                if tasks:
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(asyncio.wait(tasks))
                else:
                    pass
            print("(id:{})代理测试模块/tester运行完成，本次运行结束时间为：{}".format(sessionid, time.ctime()).upper())
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.flush()
            print(utils.info("(程序主动退出！)代理测试模块/tester发生错误，请尽快修复：{}".format(e)))
            utils.kill(self.pid)