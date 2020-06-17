# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : logs.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 15:41
--------------------------------------
"""
from . import BaseModel
from sqlalchemy import Column, SmallInteger, DateTime, String, Text


class RunningLog(BaseModel):
    """任务运行日志"""
    job_name = Column(String, index=True, nullable=False, comment="任务名称")
    start_date = Column(DateTime, nullable=False, comment="执行开始时间")
    end_date = Column(DateTime, comment="执行结束时间")
    job_cmd = Column(String, comment="执行的命令")
    category = Column(String, nullable=False, comment="所属业务")
    file_name = Column(String, comment="文件名称，job_type 为 script 时使用")
    return_code = Column(SmallInteger, comment="执行返回值, 0为成功，其它值为失败")
    stdout = Column(Text, comment="命令执行时的输出内容")
    stderr = Column(Text, comment="命令执行出错是的输出内容")
    status = Column(String(1), index=True, comment="任务运行状态")


class ModLog(BaseModel):
    """任务数据修改日志"""
    job_name = Column(String, nullable=False, index=True, comment="任务名称")
    job_type = Column(String, nullable=False, comment="任务类型")
    job_cmd = Column(String, nullable=False, comment="任务运行命令")
    time_style = Column(String, nullable=False, comment="时间风格")
    time_data = Column(String, nullable=False, comment="运行时间")
    created_by = Column(String, nullable=False, comment="创建人")
    category = Column(String, nullable=False, comment="所属业务")
    file_name = Column(String, comment="文件名称，job_type 为 script 时使用")
    desc = Column(String, nullable=False, comment="任务描述")
    action = Column(String(1), nullable=False, index=True, comment="修改动作,C:create, U:update, D:delete")
