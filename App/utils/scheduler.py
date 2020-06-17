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
from App.models.jobs import JobStatus, JobData
from App.models.logs import RunningLog
from App.setting import CRON_KEYS, STATUS_RUNNING, RESULT_SUCCESS, RESULT_FAILED, STATUS_SLEEP


def log_start(job_name, cmd):
    """
    保存任务开始信息到日志
    :param job_name:        str         job名称
    :param cmd:             str         运行的命令
    :return:                int         返回log id，成功 > 0, 失败 -1
    """
    status = STATUS_RUNNING

    job_data = JobData.query.filter(JobData.job_name == job_name).first()

    log_run = RunningLog()

    log_run.job_name = job_name
    log_run.job_cmd = cmd
    log_run.category = job_data.category
    log_run.start_date = func.now()
    log_run.status = status

    job_status = JobStatus.query.filter(JobStatus.job_name == job_name).first()
    job_status.start_on = func.now()
    job_status.run_status = status

    if job_status.commit() and log_run.insert_save():
        return job_status.id, log_run.id


def log_end(status_id, log_id, return_code, stdout, stderr):
    """
    保存任务开始信息到日志
    :param status_id:       int         任务状态的id
    :param log_id:          int         开始之前插入的运行日志的id
    :param return_code:     int         结果返回值，0正常结束，非0非正常
    :param stdout:          str         正常结束时的输出
    :param stderr:          str         运行出错时的输出
    :return:                Boolean     True：成功，False：失败
    """
    # [2020-06-17]
    # RunningLog 中要保存的额外的值，这些值来自 JobData
    running_log_keys = ["category", "job_cmd"]

    result = RESULT_SUCCESS if return_code == 0 else RESULT_FAILED
    job_status = JobStatus.query.filter(JobStatus.id == status_id).first()

    if job_status:
        """
        [2020-06-11]
        用于处理以下情形:
        程序在运行中，执行了 DELETE /api/{job_name} 命令，
        此时，job_status 中对应的 状态被删除，这时 job_status 为 None，None 没有属性，不能赋值，数据也不能更新
        """
        job_status.run_status = STATUS_SLEEP
        job_status.run_result = result
        job_status.end_on = func.now()
        job_status.commit()

    log_run = RunningLog.query.filter(RunningLog.id == log_id).first()
    # 作用同`if job_status`说明
    if log_run:
        job_name = log_run.job_name
        job_data = JobData.query.filter(JobData.job_name == job_name).first()

        log_run.status = result
        log_run.end_date = func.now()
        log_run.return_code = return_code
        log_run.stdout = stdout
        log_run.stderr = stderr

        # [2020-06-17] RunningLog 中保存额外的值
        for k in running_log_keys:
            if hasattr(job_data, k):
                setattr(log_run, k, getattr(job_data, k))

        log_run.commit()


def exec_cmd(command, cwd=None):
    """
    执行shell命令
    :param command:    str     命令内容
    :param cwd:        str     工作目录
    """
    sub = run(command, cwd=cwd, capture_output=True, shell=True, text=True)
    return sub.args, sub.returncode, sub.stdout, sub.stderr


def executor(cmd, job_name, cwd=None):
    """
    该程序作为scheduler.add_job的func
    :param cmd:             str     命令内容
    :param job_name:        str     job的身份标识
    :param cwd:             str     工作目录
    """
    with scheduler.app.app_context():
        status_id, log_id = log_start(job_name, cmd)
        _, return_code, stdout, stderr = exec_cmd(cmd, cwd)
        log_end(status_id, log_id, return_code, stdout, stderr)


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
    cwd = kwargs["cwd"]

    trigger_time = cron_to_dict(CRON_KEYS, time_data)

    job_args = {
        "cmd": job_cmd,
        "job_name": job_name,
        "cwd": cwd
    }
    # TODO: 各种执行器， cli, script, proc
    if time_style == "cron":
        main_scheduler.add_job(
            func=executor,
            id=job_name,
            kwargs=job_args,
            trigger="cron",
            **trigger_time,
            replace_existing=True  # 在添加任务时，如果任务已经存在则替换
        )

    # TODO: 对 date和 interval时间风格的支持
    elif time_style == "date":
        raise Exception("date时间风格暂不支持")

    elif time_style == "interval":
        raise Exception("interval时间风格暂不支持")

    else:
        raise Exception("非法的时间风格")
