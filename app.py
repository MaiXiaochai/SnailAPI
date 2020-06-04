# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : App.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 15:25
--------------------------------------
"""
from App import create_app

app = create_app()

if __name__ == "__main__":
    app.run(use_reloader=False)
