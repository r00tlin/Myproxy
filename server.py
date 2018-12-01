from flask import Flask, g
from conredis import RedisClient

__all__ = ["app"]
app = Flask(__name__)

def get_conn():
    if not hasattr(g, "redis"):
        g.redis = RedisClient()
    return g.redis

@app.route("/")
def index():
    return "<h2>WELCOME TO PROXY POOL SYSTEM!</h2>"

@app.route("/random")
def get_proxy():
    """
    获取一个随机可用代理
    :return: 随机可用代理
    """
    conn = get_conn()
    return conn.random()

@app.route("/count")
def get_counts():
    """
    获取代理池总量
    :return: 代理池总量
    """
    conn = get_conn()
    return str(conn.count())