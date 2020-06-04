# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : api.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 15:47
--------------------------------------
"""


def save_mod_log(action, kwargs, model):
    """
    TODO: [2020-06-05]
    保存job修改记录,每次CRUD操作都会记录。
    :param action:          str         job信息修改的操作名称
    :param kwargs:          dict        job 信息
    :param model:           Model       mod log 数据模型
    """
    t_mod = model()


def save_job_data(name, args, model):
    """
    保存job数据到数据库
    :param name:        str         job name
    :param args:        Parse.args  job数据对象
    :param model:       Model       job数据库模型
    :return:            Boolean     True:成功，False:失败
    """

    t_data = model()

    # 给model job_data对象的字段赋值
    set_model_value(t_data, args)

    # 上一行赋值时，args没有 job_name属性,所以job中没有赋值该属性，这里单独赋值
    setattr(t_data, "job_name", name)

    return t_data.insert_save()


def save_job_status(name, model):
    """
    保存job name 到 status表
    :param name:        str         job name
    :param model:       `Model`     job status 数据模型
    :return:            Boolean     True:成功，False:失败
    """
    t_status = model()
    t_status.job_name = name

    return t_status.insert_save()


def set_model_value(model, args):
    """
    给 model 实例赋值,
    前提是args中解析的keys都包含在model的cols中
    :param model:       model 实例
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
