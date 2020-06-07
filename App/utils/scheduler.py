# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : scheduler.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/28 20:18
--------------------------------------
"""

from subprocess import run

from sqlalchemy import func

from App.extensions import scheduler
from App.models.jobs import JobStatus
from App.models.logs import RunningLog
from App.setting import CRON_KEYS, STATUS_RUNNING, RESULT_SUCCESS, RESULT_FAILED, STATUS_SLEEP


def log_start(job_name, cmd, model_status, model_log):
    """
    保存任务开始信息到日志
    :param job_name:        str         job名称
    :param cmd:             str         运行的命令
    :param model_status：   class       任务状态的model类
    :param model_log：      class       运行日志的model类
    :return:                int         返回log id，成功 > 0, 失败 -1

    [2020-05-29]
    为什么用 model_data class 而不是 model_data instance？
    考虑到有的任务运行时间很长，model_data instance可能会占用会话资源。
    如果有很多运行时间很长的任务（如，刷新涉及多数据的物化视图），会给数据库带来负担，甚至会话失败。
    """
    status = STATUS_RUNNING

    job_status = model_status.query.filter(model_status.job_name == job_name).first()
    log_run = model_log()

    log_run.job_name = job_name
    log_run.job_cmd = cmd

    job_status.start_on = log_run.start_date = func.now()
    job_status.run_status = log_run.status = status

    if job_status.insert_save() and log_run.insert_save():
        return job_status.id, log_run.id

    else:
        return False


def log_end(status_id, log_id, return_code, stdout, stderr, model_status, model_log):
    """
    保存任务开始信息到日志
    :param status_id:       int         任务状态的id
    :param log_id:          int         开始之前插入的运行日志的id
    :param return_code:     int         结果返回值，0正常结束，非0非正常
    :param stdout:          str         正常结束时的输出
    :param stderr:          str         运行出错时的输出
    :param model_status：   class       任务状态的model类
    :param model_log：      class       运行日志的model类
    :return:                Boolean     True：成功，False：失败

    [2020-05-29]
    为什么用 model_data class 而不是 model_data instance？
    考虑到有的任务运行时间很长，model_data instance可能会占用会话资源。
    如果有很多运行时间很长的任务（如，刷新涉及多数据的物化视图），会给数据库带来负担，甚至新建会话失败。
    """
    job_status = model_status.query.filter(model_status.id == status_id).first()
    log_run = model_log.query.filter(model_log.id == log_id).first()

    result = RESULT_SUCCESS if return_code == 0 else RESULT_FAILED

    job_status.run_status = STATUS_SLEEP
    job_status.run_result = log_run.status = result
    job_status.end_on = log_run.end_date = func.now()

    log_run.return_code = return_code
    log_run.stdout = stdout
    log_run.stderr = stderr

    return job_status.commit(), log_run.commit()


def exec_cmd(command):
    """
    执行shell命令
    :param command:    str     命令内容
    :return:
    """
    sub = run(command, capture_output=True, shell=True, text=True)
    return sub.args, sub.returncode, sub.stdout, sub.stderr


def executor(cmd, job_name):
    """
    该程序作为scheduler.add_job的func
    :param cmd:             str     命令内容
    :param job_name:        str     job的身份标识
    TODO
    """
    with scheduler.app.app_context():
        status_id, log_id = log_start(job_name, cmd, JobStatus, RunningLog)
        _, return_code, stdout, stderr = exec_cmd(cmd)
        _ = log_end(status_id, log_id, return_code, stdout, stderr, JobStatus, RunningLog)


def cron_to_dict(cron_keys, time_data):
    """
    将crontab风格的时间, 组成dict
    :param time_data:       str     cron风格的时间
    :param cron_keys:       str     cron 使用的时间关键词
    :return:                dict    cron按照给定的时间key组成dict
    """

    cron_dict = dict(zip(cron_keys, time_data.split()))
    return cron_dict


def job_handler(main_scheduler, kwargs):
    """
    处理job，增、删、改、查
    :param main_scheduler:
    :param kwargs:           dict        job信息
    """

    job_name = kwargs["job_name"]
    job_cmd = kwargs["job_cmd"]
    time_style = kwargs["time_style"]
    time_data = kwargs["time_data"]

    trigger_time = cron_to_dict(CRON_KEYS, time_data)

    job_args = {
        "cmd": job_cmd,
        "job_name": job_name
    }
    # TODO: 各种执行器， cli, script, proc
    if time_style == "cron":
        main_scheduler.add_job(
            func=executor,
            id=job_name,
            kwargs=job_args,
            trigger="cron",
            **trigger_time,
            replace_existing=True  # 如果任务已经存在则替换
        )

    elif time_style == "date":
        raise Exception("date时间风格暂不支持")

    elif time_style == "interval":
        raise Exception("interval时间风格暂不支持")

    else:
        raise Exception("非法的时间风格")
