# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : jobs.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 15:41
--------------------------------------
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from App.setting import STATUS_SLEEP
from . import BaseModel


class JobData(BaseModel):
    """任务数据"""
    job_name = Column(String, nullable=False, unique=True, comment="任务名称")
    job_type = Column(String, nullable=False, comment="任务类型")
    job_cmd = Column(String, comment="任务运行命令")
    time_style = Column(String, nullable=False, comment="时间风格")
    time_data = Column(String, nullable=False, comment="运行时间")
    created_by = Column(String, nullable=False, comment="创建人")
    category = Column(String, nullable=False, comment="所属业务")
    file_name = Column(String, comment="文件名称，job_type 为 script 时使用")
    desc = Column(String, nullable=False, comment="任务描述")
    status = relationship("JobStatus", backref="JobData", uselist=False)


class JobStatus(BaseModel):
    """任务状态"""
    job_name = Column(String, ForeignKey(JobData.job_name), nullable=False, comment="任务名称")
    start_on = Column(DateTime, comment="最近一次开始时间")
    end_on = Column(DateTime, comment="最近一次结束时间")
    run_status = Column(String(1), nullable=False, default=STATUS_SLEEP, comment="最近一次运行状态，默认S: sleep,等待运行")
    run_result = Column(String(1), comment="最近一次运行结果")
