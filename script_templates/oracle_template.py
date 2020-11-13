# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : oracle_template.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@CreatedOn  : 2020/11/13 10:28
--------------------------------------
"""

from cx_Oracle import makedsn, connect


class OracleUtils:
    def __init__(self,
                 username: str,
                 password: str,
                 host: str,
                 port: str,
                 service_name: str = None,
                 sid: str = None):

        dns = ''
        if service_name:
            dns = makedsn(host, port, service_name=service_name)

        elif sid:
            dns = makedsn(host, port, sid=sid)

        self.conn = connect(username, password, dns)
        self.cur = self.conn.cursor()

    def execute(self, sql, args=None):
        if args:
            self.cur.execute(sql, args)
        else:
            self.cur.execute(sql)

    def executemany(self, sql, args):
        self.cur.executemany(sql, args)
        self.commit()

    def fetchall(self, sql, args=None):
        self.execute(sql, args)
        result = self.cur.fetchall()

        return result

    def fetchone(self, sql, args=None):
        self.execute(sql, args)
        result = self.cur.fetchone()

        return result

    def call_proc(self, proc: str):
        """执行不带参数的存储过程，"""
        proc = proc.strip()
        self.cur.callproc(proc)
        self.commit()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        try:
            self.cur.close()
            self.conn.close()
        except Exception as err:
            print(str(err))

    def __del__(self):
        self.close()


def worker(config: dict, args: dict):
    """执行SQL、调用存储过程"""
    oracle = OracleUtils(**config)

    # 允许执行sql、调用存储过程(proc)，以及对应的方法
    allow_args = {
        'sql': oracle.execute,
        'proc': oracle.call_proc
    }

    # 执行第几次
    counter = 1

    for key in allow_args:
        content = args.get(key)
        func = allow_args.get(key)

        if content:
            # 执行每一个SQL 或调用每一个proc
            for i in content:
                # 每个i中可能包含';'，执行时会报错,
                # 所以，遇到';'则拆成多个子句，执行每一个
                split_list = i.split(';')

                try:
                    for a_slice in split_list:
                        # 打印执行内容
                        info = f"[NO.{counter} | {key}: {a_slice}]"
                        print(info)

                        if a_slice:
                            func(a_slice)
                            oracle.commit()
                            counter += 1

                except Exception as err:
                    # 这里用print是为了给调度程序捕获输出内容
                    print(str(err))

                    # 每个i是一个完整的SQL逻辑，所以，主要i中的一个小SQL出错，整个i就停止执行
                    oracle.rollback()
                    continue


def main():
    """
    =============================[ 说明 ]================================
    oracle_cfg:
        连接Oracle的配置信息sid和service_name使用其中一个即可

    args:
        如果想执行SQL,则将SQL最为元素写在sql后的list中，proc同理
        demo:
            args = {
            'sql': ['truncate table A; insert into A select * from B;']
            }
    ====================================================================
    """

    oracle_config = {
        'username': 'erp',
        'password': 'erp1324',
        'host': '192.168.158.219',
        'port': 1521,
        'service_name': 'bfcecdw',
        'sid': ''
    }

    args = {
        'sql': [
        ]
    }

    file_name = __file__
    print(f"{file_name} ,start.")
    worker(oracle_config, args)
    print(f"{file_name} ,end.")


if __name__ == '__main__':
    main()
