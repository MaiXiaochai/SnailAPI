# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : extensions.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 15:01
--------------------------------------
"""
from math import log

from flask_apscheduler import APScheduler
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .setting import EVENT_MSG

# SQLAlchemy 创建数据表，模型结构的修改，不会被映射到对应的数据表
# Migrate 作用是将models的结构修改映射到数据库中

db = SQLAlchemy()
# 生产环境时，不要使用迁移
migrate = Migrate()
scheduler = APScheduler()


def event_listener(event):
    """
    Job状态监听程序
    event.job_id: 任务名称
    event.code:   状态值
    """
    if event:
        name = event.job_id if hasattr(event, "job_id") else "SchedulerEvent"
        code = event.code
        log_v = int(log(code, 2))
        status = EVENT_MSG[log_v]
        print(f"Job_name: {name}\t| code: {code}\t| status: {status}")


def init_ext(app):
    db.init_app(app)
    scheduler.init_app(app)
    migrate.init_app(app, db)

    # 这里暂时不用担心scheduler start多次的问题
    # start多次会报错"已经在运行",但不会影响已存在实例的运行

    scheduler.add_listener(event_listener)  # 添加监听函数，用于处理对应的调度或者job状态
    scheduler.start()
