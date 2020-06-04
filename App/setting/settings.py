# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : setting.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 16:10
--------------------------------------
"""
from os.path import dirname, abspath, join

from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from App.extensions import db
from App.utils import get_db_uri

BASE_DIR = dirname(dirname(abspath(__file__)))


class BaseConfig:
    """
    基础配置
    """
    db_info = {
        "engine": "postgresql",
        "driver": "psycopg2",
        "user": "pguser",
        "password": "Pg_1234.",
        "host": "192.168.158.14",
        "port": 5432,
        "name": "SnailData"
    }
    DEBUG = False
    TESTING = False
    # ================[ 接口版本设置 ]================
    API_INTERFACE = "/api"

    # ================[ APScheduler设置 ]================
    # 时区
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'

    # 是否使用flask-apscheduler自带的API
    SCHEDULER_API_ENABLED = False

    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url=get_db_uri(db_info))
    }
    SCHEDULER_EXECUTORS = {
        'default': ThreadPoolExecutor(50),
        'processpool': ProcessPoolExecutor(max_workers=8),
    }
    SCHEDULER_JOB_DEFAULTS = {
        "coalesce": True,
        "max_instances": 1,                 # 单个作业可以运行几个实例
        "misfire_grace_time": 1800,         # 假设任务将在9:00 运行，结果 8:55 ~ 9:10调度程序挂了，
                                            # 那么只要在9:00 ~ 9:30内重新启动（按1800s值计算），该任务会继续运行

    }

    # ===================[ session设置 ]===================
    #
    SECRET_KEY = "4)rzG[giX:{>)2>_Np'`X-Q&YZFzj@5-"
    SESSION_USE_SIGNER = True  # 对发送到浏览器上的cookie进行加密
    SESSION_TYPE = "sqlalchemy"
    SESSION_SQLALCHEMY = db

    # Sqlalchemy 使用的数据库
    SQLALCHEMY_DATABASE_URI = get_db_uri(db_info)  # "sqlite:///sqlite.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # ===================[ 缓存设置 ]===================
    # 缓存类型
    CACHE_TYPE = "filesystem"
    # 缓存类型为"filesystem"时，该值要指定。
    # 注意：指定的是目录，不是文件
    CACHE_DIR = "cache"
    # 缓存数据超时时间(seconds)
    CACHE_DEFAULT_TIMEOUT = 60 * 60 * 24 * 30

    # ===================[ 邮箱设置 ]===================
    MAIL_SERVER = "smtp.163.com"
    # 163 SSL协议端口 465/994, 非SSL协议端口25
    # 注意这里启用的是TLS协议(transport layer security)，而不是SSL协议所用的是25号端口
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = "chargestarmap@163.com"
    # 163这里用的是授权码
    MAIL_PASSWORD = """RYLVFPIMSJSDKVTD"""
    MAIL_DEFAULT_SENDER = MAIL_USERNAME


class DevelopBaseConfig(BaseConfig):
    """
    开发环境配置
    """
    pass


class TestingBaseConfig(BaseConfig):
    """
    测试环境配置
    """
    TESTING = True
    db_info = {
        "engine": "mysql",
        "driver": "pymysql",
        "user": "sched",
        "password": "sched123",
        "host": "127.0.0.1",
        "port": 1521,
        "name": "Snail"
    }
    # ORM 数据库连接串
    SQLALCHEMY_DATABASE_URI = get_db_uri(db_info)


class StagingBaseConfig(BaseConfig):
    """
    演示环境配置
    """
    db_info = {
        "engine": "mysql",
        "driver": "pymysql",
        "user": "sched",
        "password": "sched123",
        "host": "127.0.0.1",
        "port": 1521,
        "name": "Snail"
    }
    # ORM 数据库连接串
    SQLALCHEMY_DATABASE_URI = get_db_uri(db_info)


class ProductBaseConfig(BaseConfig):
    """
    生产环境配置
    """
    db_info = {
        "engine": "postgresql",
        "driver": "psycopg2",
        "user": "pguser",
        "password": "Pg_1234.",
        "host": "192.168.158.14",
        "port": 5432,
        "name": "SnailData"
    }
    # ORM 数据库URI
    SQLALCHEMY_DATABASE_URI = get_db_uri(db_info)


envs = {
    "development": DevelopBaseConfig,
    "testing": TestingBaseConfig,
    "staging": StagingBaseConfig,
    "production": ProductBaseConfig,
    "default": DevelopBaseConfig,
}

# 管理员用户设置
ADMINS = (
    "snail",
)

# 静态文件路径
UPLOAD_DIR = join(BASE_DIR, "App/static/upload/icons")

# 相对文件路径
FILE_PATH = "/static/upload/icons"


if __name__ == "__main__":
    res = DevelopBaseConfig().CACHE_DIR
    print(res)
