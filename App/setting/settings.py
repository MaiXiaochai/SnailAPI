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

    # ================[ 上传文件设置 ]================
    BASE_DIR = dirname(dirname(dirname(abspath(__file__))))
    # 上传的文件所在的文件夹名称
    DIR_NAME = "scripts"
    UPLOAD_DIR = join(BASE_DIR, DIR_NAME)

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
    """
    coalesce:           是否允许job实例合并
    比如上个任务实例运行时间超过了运行间隔，到了再次运行新实例的时间，
    这个时候，是否将两个实例合并为一个实例运行
        True:合并，一个任务只会运行一个实例
        False:不合并，一个任务会同时运行多个实例

    [2020-07-27]
    replace_existing:
    如果在程序(这里指scheduler)初始化期间，在持久化作业存储中安排作业，
    必须给作业指定一个显示的ID，并且设置replace_existing=True，
    否则，每次程序重启的时候，会得到该job的一个新副本

    max_instances:      单个job最多可以运行几个实例
    misfire_grace_time: 任务因不可抗力在规定时间点没有执行时，允许自动补偿执行的宽限期
                            假设该值为1800s（0.5h）,任务将在9:00 运行，结果 8:55 ~ 9:10调度程序挂了，
                            那么只要在9:00 ~ 9:30内调度程序恢复正常（按1800s值计算），该任务会马上执行。
                            简称：虽迟但执
    """
    SCHEDULER_JOB_DEFAULTS = {
        "coalesce": False,
        "replace_existing": True,
        "max_instances": 3,
        "misfire_grace_time": 1800
    }

    #
    # 管理员用户设置
    ADMINS = ("snail",)

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
        "engine": "postgresql",
        "driver": "psycopg2",
        "user": "pguser",
        "password": "Pg_1234.",
        "host": "192.168.158.14",
        "port": 5432,
        "name": "SnailData"
    }
    # ORM 数据库连接串
    SQLALCHEMY_DATABASE_URI = get_db_uri(db_info)


class StagingBaseConfig(BaseConfig):
    """
    演示环境配置
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


if __name__ == "__main__":
    bc = BaseConfig()
    # E:\Code\github\SnailAPI\App\scripts
    res = bc.UPLOAD_DIR
    print(res)
