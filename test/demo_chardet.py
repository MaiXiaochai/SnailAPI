# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : demo_chardet.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@CreatedOn  : 2020/7/2 16:53
--------------------------------------
"""
from chardet import detect

res = bytes.fromhex('01 02 03 ff 04 05')

print(detect(res))
