# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : api.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 15:47
--------------------------------------
"""
from sqlalchemy import func

from App.setting import (ACTION_CREATED, ACTION_UPDATED, ACTION_DELETED, STATUS_PAUSED, STATUS_SLEEP, STATUS_RUNNING,
                         STATUS_DICT
                         )


def save_mod_log(action, args, model_mod, model_data):
    """
    TODO: [2020-06-05]
    保存job数据和人为状态修改记录,每次人为的CRUD、pause、resume、run操作都会记录。
    :param action:          str         job信息修改的操作名称
    :param args:            dict        job 信息
    :param model_mod:       Model       job数据修改日志模型
    :param model_data:      Model       job数据模型
    """
    action = action if len(action) == 1 else getattr(STATUS_DICT, action)
    t_mod = model_mod()
    name = getattr(args, "job_name")
    executable = False

    if action == ACTION_CREATED:
        set_model_value(t_mod, args)
        executable = True

    elif action == ACTION_UPDATED:
        """
        Q: 为什么用getattr而不是get？
        A: args虽然规定为字典，在使用时难免遇到不是字典的情况，为了在后者出现时同样兼容。
        """
        job_data = model_data.query.filter(model_data.job_name == name).first()
        if job_data:
            set_model_value(t_mod, job_data)
            set_model_value(t_mod, args)
            executable = True

    elif action in (ACTION_DELETED, STATUS_PAUSED, STATUS_SLEEP, STATUS_RUNNING):
        job_data = model_data.query.filter(model_data.job_name == name).first()
        if job_data:
            set_model_value(t_mod, job_data)
            executable = True

    if hasattr(t_mod, "status"):
        delattr(t_mod, "status")

    if executable:
        setattr(t_mod, "action", action)
        t_mod.insert_save()

    return executable


def save_job_data(args, model_data):
    """
    保存job数据到数据库
    :param args:        Parse.args  job数据对象
    :param model_data:  Model       job数据库模型
    :return:            Boolean     True:成功，False:失败
    """

    t_data = model_data()

    # 给model job_data对象的字段赋值
    set_model_value(t_data, args)

    return t_data.insert_save()


def up_job_data(args, model_data):
    """
    保存job数据到数据库
    :param args:        Parse.args  job数据对象
    :param model_data:  Model       job数据库模型
    :return:            Boolean     True:成功，False:失败
    """
    name = getattr(args, "job_name")
    t_data = model_data.query.filter(model_data.job_name == name).first()

    # 给model job_data对象的字段赋值
    set_model_value(t_data, args)

    return t_data.commit()


def save_job_status(name, model):
    """
    保存或者修改job 状态
    :param name:        str         job name
    :param name:        str         job status
    :param model:       Model       job status 数据模型
    :return:            Boolean     True:成功，False:失败
    """
    t_status = model()
    t_status.job_name = name

    return t_status.insert_save()


def up_job_status(name, model, status, result=None):
    """
    更新job 状态
    :param name:        str     job name
    :param model:       Model   job status 模型
    :param status:      str     job 状态
    :param result:      str     job 运行结果
    :return:            Boolean True：更新成功，False：更新失败
    """
    t_status = model.query.filter(model.job_name == name).first()
    t_status.run_status = status

    if status == "run":
        t_status.start_on = func.now()

    if result:
        t_status.end_on = func.now()
        t_status.run_result = result

    return t_status.commit()


def del_job(name, model_status, model_data):
    """
    删除job数据
    因为JobData和JobStatus有一对一关系，后者使用了前者的job_name作为外键，所以，先删除JobStatus再删除JobData
    :param name:                str         job name
    :param model_status:        JobStatus   job status模型
    :param model_data:          JobData     job data模型
    """
    t_status, t_data = model_status, model_data

    t_status.delete(name)
    t_data.delete(name)


def set_model_value(model, args):
    """
    给 model_data 实例赋值,
    前提是args中解析的keys都包含在model的cols中
    :param model:       model_data 实例
    :param args:        flask_restful.RequestParser解析出来的对象
    """
    for item in args.items():
        k, v = item
        setattr(model, k, v)


def get_next_time(job_list):
    """
    获取 scheduler.get_job(s)结果中的下次运行时间
    :param job_list:        list        job查询结果
    :return:                list        格式化好的结果
    """
    result = []

    for item in job_list:
        _tmp = {
            "job_name": item.id,
            "next_run_time": item.next_run_time,

        }
        result.append(_tmp)
        _tmp = {}

    return result
