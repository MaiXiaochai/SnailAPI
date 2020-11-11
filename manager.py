# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : manager.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 15:26
--------------------------------------
初始化时的命令：
1) python manager.py db init        # 初始化一个迁移脚本的环境，只需要执行一次
2) python manager.py db migrate     # 将模型生成迁移文件，只要模型更改了，数据库结构有变动时，需要执行一次这个命令
3) python manager.py db upgrade     # 将迁移文件真正地映射到数据库中，数据库结构有变动时先执行2)，再执行一次这个命令
"""

from flask_migrate import MigrateCommand
from flask_script import Manager

from App import create_app

app = create_app()
manager = Manager(app)
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
