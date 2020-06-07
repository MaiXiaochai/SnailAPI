# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : __init__.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 13:50
--------------------------------------
"""
from App.extensions import db
from sqlalchemy import Column, Integer, DateTime, func


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_on = Column(DateTime, server_default=func.now(), comment='创建时间')
    # updated_on：设置自动更改
    updated_on = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='修改时间')

    def insert_save(self):
        """
        session.add & session.commit
        :return:        Boolean     True: 成功, False: 失败
        """
        result = True
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as err:
            result = False

        return result

    def delete(self, name, model):
        """
        按 job name 删除数据
        session.delete & session.commit
        :return:
        :param name:        str         job name
        :param model:       SubModel    子模型类
        :return:            Boolean     True: 成功, False: 失败
        """
        result = True
        try:
            db.session.query(model).filter(model.job_name == name).delete()
            db.session.commit()
        except Exception as err:
            result = False

        return result

    def commit(self):
        """
        just session.commit()
        :return:
        """
        result = True
        try:
            db.session.commit()
        except Exception as err:
            result = False

        return result

    def delete(self):
        result = False
        try:
            db.session.delete(self)
            db.session.commit()
            result = True
        except Exception as err:
            pass

        return result
