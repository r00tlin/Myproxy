import os
import sys
import time
import utils
from server import app
from getter import Getter
from tester import Tester
from concurrent import futures

class Scheduler():
    def __init__(self):
        conf = utils.config()
        self.TESTER_CYCLE = conf["TESTER_CYCLE"]
        self.GETTER_CYCLE = conf["GETTER_CYCLE"]
        self.TESTER_ENABLED = conf["TESTER_ENABLED"]
        self.GETTER_ENABLED = conf["GETTER_ENABLED"]
        self.API_ENABLED = conf["API_ENABLED"]
        self.API_HOST = conf["API_HOST"]
        self.API_PORT = conf["API_PORT"]

    def schedule_tester(self, pid):
        """
        定时测试代理
        """
        tester = Tester(pid)
        while True:
            tester.run()
            time.sleep(self.TESTER_CYCLE)

    def schedule_getter(self, pid):
        """
        定时获取代理
        """
        getter = Getter(pid)
        while True:
            getter.run()
            time.sleep(self.GETTER_CYCLE)

    def schedule_api(self, pid):
        """
        开启api
        """
        try:
            print("API模块/server开始运行，以下为服务启动信息：")
            app.run(self.API_HOST, self.API_PORT)
        except Exception as e:
            sys.stdout.flush()
            print(utils.info("(程序主动退出！)API模块/server发生错误，请尽快修复：{}".format(e)))
            utils.kill(pid)

    def run(self):
        """
        运行调度程序，分别启用三个进程控制三个模块
        :return:
        """
        info = """
        PROXYPOOL 调度程序开始运行
        
您将持续获得以下服务：
1.自动获取网络上免费的代理服务地址。
2.自动更新获得的代理信息。
3.本地API服务以方便读取地址。

在获得上述服务之前您需要保证：
1.配置文件完整且有效。
2.安装必要的第三方库。
3.redis正确安装且有效配置。
        """
        print(info)
        with futures.ProcessPoolExecutor(max_workers=3) as executor:
            pid = os.getpid()
            if self.API_ENABLED:
                executor.submit(self.schedule_api, pid)
            if self.GETTER_ENABLED:
                executor.submit(self.schedule_getter, pid)
            if self.TESTER_ENABLED:
                executor.submit(self.schedule_tester, pid)

if __name__ == "__main__":
    #启动三个进程别处理三个相关模块
    Scheduler().run()