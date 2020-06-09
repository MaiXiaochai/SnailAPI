# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : model_data.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/25 21:26
--------------------------------------
"""


def get_db_uri(db_info):
    """
    1)postgresql://username:password@hostname/database
        postgresql://pguser:Pg_1234.@192.168.158.14/SnailData

    2)oracle+cx_oracle://sched:sched123@192.168.158.219:1521/?service_name=bfcecdw

    :param db_info:     dict    连接信息
    :return:            str     ORM URI
    """
    uri = "{engine} not found."
    uri_tpl = "{engine}+{driver}://{user}:{password}@{host}:{port}/"

    db_engine = db_info.get("engine")

    if db_engine in ("mysql", "postgresql"):
        uri = uri_tpl + "{name}"

    elif db_engine == "oracle":
        _keys = db_info.keys()

        if "service_name" in _keys:
            uri = uri_tpl + "?service_name={service_name}"
        else:
            uri = uri_tpl + "{name}"

    result = uri.format(**db_info)

    return result
