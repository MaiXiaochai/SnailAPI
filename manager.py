# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : manager.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 15:26
--------------------------------------
"""

from flask_migrate import MigrateCommand
from flask_script import Manager

from App import create_app

app = create_app()
manager = Manager(app)
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
