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
        db.session.add(self)
        db.session.commit()

        return True

    def commit(self):
        """ Just session.commit() """
        db.session.commit()

        return True

    def delete(self):
        db.session.delete(self)
        db.session.commit()

        return True
