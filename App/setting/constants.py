# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : constants.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 16:11
--------------------------------------
*）这里定义了一些通用的常量。
!）若非对使用逻辑和使用场景完全了解，请勿修改，否则会造成整个调度系统出现问题。
# TODO: [2020-07-01]
        将常量写在 Enum 子类中，防止使用中修改
"""

# ============================[ 请求返回状态码，status ]============================
HTTP_OK = 200
HTTP_CREATED_OK = 201
HTTP_CREATED_FAILED = 500
HTTP_EXECUTE_FAILED = 500
HTTP_CONFLICT = 409         # 发生冲突
HTTP_QUERY_ERROR = 400

# =============================[ 任务请求返回信息 msg ]=============================
MSG_JOB_EXISTED = "任务已存在"
MSG_FILE_EMPTY = "脚本是空的或者没有上传"
MSG_CMD_VALID = "不支持的命令模式"

MSG_JOB_QUERY_SUCCESS = "查询成功"
MSG_JOB_QUERY_FAILED = "查询错误"

MSG_JOB_CREATED_SUCCESS = "任务添加成功"
MSG_JOB_CREATED_FAILED = "任务添加失败"

MSG_JOB_PAUSED_SUCCESS = "任务暂停成功"
MSG_JOB_PAUSED_FAILED = "任务暂停失败"

MSG_JOB_RESUMED_SUCCESS = "任务恢复成功"
MSG_JOB_RESUMED_FAILED = "任务恢复失败"

MSG_JOB_RUNNING_START = "任务开始运行"
MSG_JOB_RUNNING_SUCCESS = "任务运行成功"
MSG_JOB_RUNNING_FAILED = "任务运行失败"

MSG_JOB_MODIFIED_SUCCESS = "任务修改成功"
MSG_JOB_MODIFIED_FAILED = "任务修改失败"

MSG_JOB_EXECUTE_SUCCESS = "任务执行成功"
MSG_JOB_EXECUTE_FAILED = "任务执行失败"

MSG_JOB_DELETED_SUCCESS = "任务删除成功"
MSG_JOB_DELETED_FAILED = "任务删除失败"
MSG_JOB_DELETED_AGAIN = "任务已经删除，多次删除也只是删除一次，干点别的吧，亲"

# =============================[ 任务运行状态 ]=============================
STATUS_SLEEP = "S"      # SLEEP     任务已添加等待运行
STATUS_RUNNING = "R"    # RUNNING   任务正在运行
STATUS_PAUSED = "P"     # PAUSED    任务暂停(这里的暂停指的是没有下次运行时间)
STATUS_OVER = "O"       # OVER      用于只执行一次的任务

STATUS_DICT = {
    "pause": STATUS_PAUSED,
    "resume": STATUS_SLEEP,
    "run": STATUS_RUNNING
}

# =============================[ 任务运行结果 ]=============================
RESULT_SUCCESS = "Y"    # YES       运行成功
RESULT_FAILED = "N"     # NO        运行失败

# =============================[ 任务修改操作 ]=============================
ACTION_CREATED = "C"    # CREATE    创建
ACTION_UPDATED = "U"    # UPDATE    修改
ACTION_DELETED = "D"    # DELETE    删除

# ======================[ APScheduler listener设置 ]=======================
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

# =============================[ 自定义错误处理 ]=============================
# TODO: ，API使用, 暂时还没有用到
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

# ============================[ 调度的时间关键词 ]==============================
CRON_KEYS = ["minute", "hour", "day", "month", "day_of_week"]

# ===========================[ 调度执行命令的类型 ]=============================
JOB_TYPE_CLI = "cli"
JOB_TYPE_SCRIPT = "script"
JOB_TYPE_DIR = "dir"
# =============================[ job 的时间类型 ]==============================
TRIGGER_TYPE_CRON = "cron"
TRIGGER_TYPE_DATE = "date"
TRIGGER_TYPE_INTERVAL = "interval"

# ==========================[ 根据后缀判断命令的设置 ]===========================
SUFFIX_CMD = {
    "py": "python ",
    "bat": "",
    "cmd": "",
    "sh": "./"
}

# =========================[ 传入的参数中需要小写的 key ]==========================
LOWER_KEYS = ["category", "time_style", "job_type"]
