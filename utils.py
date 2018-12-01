import os
import sys
import signal
import requests
from configparser import ConfigParser
from requests.exceptions import ConnectionError

base_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
}

def get_page(url, options={}):
    """
    抓取代理
    :param url:
    :param options:
    :return:
    """
    headers = dict(base_headers, **options)
    print("正在抓取：{}".format(url))
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.text
        else:
            return "ERROR STATUS_CODE"
    except (ConnectionError, Exception):
        return None


def config():
    try:
        configs = {}
        conf = ConfigParser()
        conf.read("config", encoding="utf-8")
        configs["REDIS_HOST"] = conf.get("REDIS", "REDIS_HOST")
        configs["REDIS_PORT"] = int(conf.get("REDIS", "REDIS_PORT"))
        configs["REDIS_PASS"] = None if conf.get("REDIS", "REDIS_PASS") == "" or "None" else conf.get("REDIS", "REDIS_PASS")
        configs["REDIS_KEY"] = conf.get("REDIS", "REDIS_KEY")
        configs["MAX_SCORE"] = int(conf.get("SCORE", "MAX_SCORE"))
        configs["MIN_SCORE"] = int(conf.get("SCORE", "MIN_SCORE"))
        configs["INITIAL"] = conf.get("SCORE", "INITIAL")
        configs["POOL_UPPER_THRESHOLD"] = int(conf.get("POOL","POOL_UPPER_THRESHOLD"))
        configs["VALID_STATUS_CODES"] = [int(code) for code in conf.get("POOL", "VALID_STATUS_CODES").split()]
        configs["TEST_URL"] = conf.get("POOL", "TEST_URL")
        configs["BATCH_TEST_SIZE"] = int(conf.get("POOL", "BATCH_TEST_SIZE"))
        configs["TESTER_CYCLE"] = int(conf.get("SCHEDULER", "TESTER_CYCLE"))
        configs["GETTER_CYCLE"] = int(conf.get("SCHEDULER" ,"GETTER_CYCLE"))
        configs["TESTER_ENABLED"] = False if  conf.get("SCHEDULER", "TESTER_ENABLED") == "False" else True
        configs["GETTER_ENABLED"] = False if  conf.get("SCHEDULER", "GETTER_ENABLED") == "False" else True
        configs["API_ENABLED"] = False if  conf.get("SCHEDULER", "API_ENABLED") == "False" else True
        configs["API_HOST"] = conf.get("SERVER", "API_HOST")
        configs["API_PORT"] = int(conf.get("SERVER", "API_PORT"))
        configs["IP_COUNT"] = int(conf.get("SERVER", "IP_COUNT"))
        return configs
    except Exception as e:
        print("配置文件读取出错，请按照配置文件标准进行修改:{}".format(e))
        raise e



def kill(pid):
    if not plat():
        os.popen("taskkill /PID:{} /F".format(pid))
    else:
        os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)

def info(msg):
    return "\033[1;31;40m{}\033[0m".format(msg) if plat() else msg

def plat():
    #win<-->False   other<-->True
    return False if "win32" in sys.platform else True