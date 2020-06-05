# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : constants.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 16:11
--------------------------------------
"""
# # API return
# 请求返回状态码，status
HTTP_OK = 200
HTTP_CREATED_OK = 201
HTTP_CREATED_FAILED = 500
HTTP_EXECUATE_FAILED = 500
HTTP_CONFLICT = 409             # 发生冲突
HTTP_QUERY_ERROR = 400

# 任务请求返回信息 msg
MSG_JOB_CREATED_SUCCESS = "任务添加成功"
MSG_JOB_CREATED_FAILED = "添加任务失败"
MSG_JOB_EXISTED = "任务已存在"
MSG_JOB_PAUSED = "任务已暂停"
MSG_JOB_RESUMED = "任务已恢复"
MSG_JOB_RUNNING = "任务正在运行"
MSG_JOB_EXECUATE_FAIELD = "任务执行失败"
MSG_JOB_QUERY_FAILED = "查询错误"
MSG_JOB_QUERY_SUCCESS = "查询成功"

# 任务运行状态
STATUS_SLEEP = "S"      # SLEEP     任务已添加等待运行
STATUS_RUNNING = "R"    # RUNNING   任务正在运行
STATUS_PAUSED = "P"     # PAUSED    任务暂停(这里的暂停指的是没有下次运行时间)
STATUS_OVER = "O"       # OVER      用于只执行一次的任务

# 任务运行结果
RESULT_SUCCESS = "Y"    # YES       运行成功
RESULT_FAILED = "N"     # NO        运行失败

# TODO: 任务修改操作,用于任务修改的记录
ACTION_CREATED = "C"    # CREATE    创建
ACTION_UPDATED = "U"    # UPDATE    修改
ACTION_DELETED = "D"    # DELETE    删除


# TODO: 自定义错误字典，API使用, 暂时还没有自定义错误
ERRORS = {
    'UserAlreadyExistsError': {
        'message': "A user with that username already exists.",
        'status': 409,
    },
    'ResourceDoesNotExist': {
        'message': "所访问的资源不存在",
        'status': 404,
        'extra': "建议使用规范的地址重新尝试"
    }
}

# crontab 调度的时间关键词
CRON_KEYS = ["minute", "hour", "day", "month", "day_of_week"]


# ============================[ APScheduler EVENT MSG ] ============================
EVENT_MSG = (
    "EVENT_SCHEDULER_STARTED",
    "EVENT_SCHEDULER_SHUTDOWN",
    "EVENT_SCHEDULER_PAUSED",
    "EVENT_SCHEDULER_RESUMED",
    "EVENT_EXECUTOR_ADDED",
    "EVENT_EXECUTOR_REMOVED",
    "EVENT_JOBSTORE_ADDED",
    "EVENT_JOBSTORE_REMOVED",
    "EVENT_ALL_JOBS_REMOVED",
    "EVENT_JOB_ADDED",
    "EVENT_JOB_REMOVED",
    "EVENT_JOB_MODIFIED",
    "EVENT_JOB_EXECUTED",
    "EVENT_JOB_ERROR",
    "EVENT_JOB_MISSED",
    "EVENT_JOB_SUBMITTED",
    "EVENT_JOB_MAX_INSTANCES"
)
