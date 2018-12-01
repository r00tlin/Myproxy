import re
import redis
import utils
from random import sample
from error import PoolEmptyError



class RedisClient():
    _obj = None
    _ini = True
    def __new__(cls, *args, **kwargs):
        """
        使用单例模式创建
        :return: 新创建的对象
        """
        if not cls._obj:
            cls._obj = object.__new__(cls)
        return cls._obj

    def __init__(self):
        conf = utils.config()
        host = conf["REDIS_HOST"]
        port = conf["REDIS_PORT"]
        passwd = conf["REDIS_PASS"]
        self.key = conf["REDIS_KEY"]
        self.max_score = conf["MAX_SCORE"]
        self.min_score = conf["MIN_SCORE"]
        self.initial_score = conf["INITIAL"]
        self.ip_count = conf["IP_COUNT"]
        self.db = redis.StrictRedis(host=host, port=port, password=passwd, decode_responses=True)

    def add(self, proxy):
        """
        添加代理，设置分数为最高
        :param proxy: 代理
        :return: 添加结果
        """
        if not re.match(r"\d+.\d+.\d+.\d+:\d+", proxy):
            return
        if not self.db.zscore(self.key, proxy):
            return self.db.zadd(self.key, self.initial_score, proxy)

    def random(self):
        """
        随机获取有效的代理，首先尝试获取分数最高的代理，如果分数最高的不存在，则按照排名获取。否则异常
        :return: 随机代理
        """
        result = self.db.zrangebyscore(self.key, self.max_score, self.max_score)
        rlen = len(result)
        if rlen:
            if rlen >= self.ip_count:
                res = "|".join(sample(result, self.ip_count))
            else:
                res = "|".join(sample(result, rlen))
        else:
            result = self.db.zrevrange(self.key, 0, 100)
            rlen = len(result)
            if rlen:
                if rlen >= self.ip_count:
                    res = "|".join(sample(result, self.ip_count))
                else:
                    res = "|".join(sample(result, rlen))
            else:
                raise PoolEmptyError
        return res

    def decrease(self, proxy):
        """
        代理分数减少操作，每次失败以后减去一分，当小于某个阀值以后，删除代理
        :param proxy: 代理
        :return: 修改以后的代理分数
        """
        score = self.db.zscore(self.key, proxy)
        if score and score > self.min_score:
            return self.db.zincrby(self.key, proxy, -1)
        else:
            return self.db.zrem(self.key, proxy)

    def exists(self, proxy):
        """
        判断是否存在
        :param proxy:代理
        :return: 是否存在
        """
        return not self.db.zscore(self.key, proxy)

    def max(self, proxy):
        """
        将代理设置为MAX_SCORE
        :param proxy: 代理
        :return: 设置结果
        """
        return self.db.zadd(self.key, self.max_score, proxy)

    def count(self):
        """
        获取数量
        :return:数量
        """
        return self.db.zcard(self.key)

    def all(self):
        """
        获取全部代理
        :return: 全部代理列表,降序
        """
        return self.db.zrangebyscore(self.key, self.max_score, self.min_score)

    def batch(self, start, stop):
        """
        批量获取
        :param start:开始索引
        :param stop:结束索引
        :return:代理列表
        """
        return self.db.zrevrange(self.key, start, stop-1)

    def info(self):
        """
        测试时使用，获取redis服务器info信息
        :return:
        """
        return self.db.info()