# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : api.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 15:47
--------------------------------------
"""
from os import makedirs, remove, listdir, rmdir
from os.path import join, exists
from shutil import move

from sqlalchemy import func
from werkzeug.utils import secure_filename

from App.models import BaseModel
from App.setting import (ACTION_CREATED, ACTION_UPDATED, ACTION_DELETED, STATUS_PAUSED, STATUS_SLEEP, STATUS_RUNNING,
                         STATUS_DICT, SUFFIX_CMD
                         )


def model_to_dict(model: BaseModel):
    """
    获取模型对应的数据库字段
    :param model:           BaseModel           数据库模型
    :return:                dict(key, value)    该模型包含的字段
    """
    result = {}
    for k in model.__dict__.keys():
        if k.startswith("_"):
            continue

        v = getattr(model, k)
        result[k] = v

    return result


def rm_bad_cols(mod, base_mod):
    """
    移除mod中存在的base_mod中的字段, save_mod_log 用到此函数
    base_mod 有可能是 mod 的基础类
    :param mod:             BaseModel
    :param base_mod:        BaseModel
    :return:                Boolean     True：成功，False：失败
    """
    bad_keys = get_bad_keys(base_mod)

    try:
        if isinstance(mod, base_mod):
            mod = model_to_dict(mod)

        if isinstance(mod, dict):
            for key in bad_keys:
                if key in mod:
                    mod.pop(key)
        else:
            raise Exception(f"[{__file__}:rm_bad_cols: invalid mod type.]")

    except Exception as err:
        raise Exception(f"[ {__file__}:rm_bad_cols: {str(err)}.]")

    return mod


def save_mod_log(action, args, model_mod, model_data):
    """
    保存job数据和人为状态修改记录,每次人为的CRUD、pause、resume、run操作都会记录。
    :param action:          str         job信息修改的操作名称
    :param args:            dict        job 信息
    :param model_mod:       Model       job数据修改日志模型
    :param model_data:      Model       job数据模型
    """
    # 传入的actions有可能是单词（如"pause"）,为了统一标准，这里统一使用单个字母标识
    action = action if len(action) == 1 else STATUS_DICT.get(action)
    name = args.get("job_name")

    t_mod = model_mod()
    executable = False

    # 新创建的 job
    if action == ACTION_CREATED:
        set_model_value(t_mod, args)
        executable = True

    # job 内容（主要是时间风格和时间内容）有变更
    # 注意，这里的思路是记录日志，变动一次就插入一条数据。
    # 所以，update job最后在ORM中用的是插入，而不是更新
    elif action == ACTION_UPDATED:
        job_data = model_data.query.filter(model_data.job_name == name).first()
        if job_data:
            job_data = rm_bad_cols(job_data, BaseModel)
            # 先赋予全部的值，然后再更新变动的字段的值
            set_model_value(t_mod, job_data)
            set_model_value(t_mod, args)
            executable = True

    elif action in (ACTION_DELETED, STATUS_PAUSED, STATUS_SLEEP, STATUS_RUNNING):
        job_data = model_data.query.filter(model_data.job_name == name).first()
        if job_data:
            job_data = rm_bad_cols(job_data, BaseModel)
            set_model_value(t_mod, job_data)
            executable = True

    if executable:
        setattr(t_mod, "action", action)
        t_mod.insert_save()

    return executable


def save_job_data(args, model_data):
    """
    保存job数据到数据库
    :param args:        Parse.args  job数据对象
    :param model_data:  Model       job数据库模型
    :return:            Boolean     True:成功，False:失败
    """

    t_data = model_data()

    # 给model job_data对象的字段赋值
    set_model_value(t_data, args)

    return t_data.insert_save()


def up_job_data(args, model_data):
    """
    保存job数据到数据库
    :param args:        dict        job数据对象
    :param model_data:  Model       job数据库模型
    :return:            Boolean     True:成功，False:失败
    """
    name = args.get("job_name")
    t_data = model_data.query.filter(model_data.job_name == name).first()

    # 给model job_data对象的字段赋值
    set_model_value(t_data, args)

    return t_data.commit()


def save_job_status(name, model):
    """
    保存或者修改job 状态
    :param name:        str         job name
    :param name:        str         job status
    :param model:       Model       job status 数据模型
    :return:            Boolean     True:成功，False:失败
    """
    t_status = model()
    t_status.job_name = name

    return t_status.insert_save()


def up_job_status(name, model, status, result=None):
    """
    更新job 状态
    :param name:        str     job name
    :param model:       Model   job status 模型
    :param status:      str     job 状态
    :param result:      str     job 运行结果
    :return:            Boolean True：更新成功，False：更新失败
    """
    t_status = model.query.filter(model.job_name == name).first()
    t_status.run_status = status

    if status == "run":
        t_status.start_on = func.now()

    if result:
        t_status.end_on = func.now()
        t_status.run_result = result

    return t_status.commit()


def del_job(name, model_status, model_data):
    """
    删除job数据
    因为JobData和JobStatus有一对一关系，后者使用了前者的job_name作为外键，所以，先删除JobStatus再删除JobData
    :param name:                str         job name
    :param model_status:        JobStatus   job status模型
    :param model_data:          JobData     job data模型
    """
    t_status = model_status.query.filter(model_status.job_name == name).first()
    t_data = model_data.query.filter(model_data.job_name == name).first()

    result = t_status.delete() and t_data.delete()

    return result


def get_bad_keys(base_model):
    """
    获取BaseModel或者其它基础Model的字段名称
    :param base_model:       BaseModel          基础数据模型
    :return:                 list[str, str]     字段名称
    """
    result = []
    for k in base_model.__dict__.keys():
        if k.startswith("_") or callable(getattr(base_model, k)):
            continue
        result.append(k)

    return result


def set_model_value(obj, args):
    """
    给 model_data 实例赋值,
    前提是args中解析的keys都包含在model的cols中
    :param obj:         可以设置属性的对象
    :param args:        flask_restful.RequestParser解析出来的对象
    """
    if isinstance(args, BaseModel):
        args = model_to_dict(args)

    if isinstance(obj, dict):
        for item in args.items():
            k, v = item
            obj[k] = v
    else:
        for item in args.items():
            k, v = item
            setattr(obj, k, v)


def rm_empty_kw(data: dict):
    """
    删除字典中值为空的键值对
    """
    result = {}
    if not isinstance(data, dict):
        raise Exception("The object is not a dict")

    for k, v in data.items():
        if v:
            result[k] = v

    return result


def get_next_time(job_list):
    """
    获取 scheduler.get_job(s)结果中的下次运行时间
    :param job_list:        list        job查询结果
    :return:                list        格式化好的结果
    """
    result = []

    for item in job_list:
        _tmp = {
            "job_name": item.id,
            "next_run_time": item.next_run_time,

        }
        result.append(_tmp)
        _tmp = {}

    return result


def gen_cmd(filename: str) -> str:
    """
    根据后缀名称，生成默认命令
    """
    split_str = "."
    if split_str not in filename:
        raise Exception("gen_cmd: 所给的文件名称没有后缀")

    suffix = filename.split(split_str)[-1].lower()
    program = SUFFIX_CMD[suffix]
    cmd = f"{program}{filename}"

    return cmd


def to_lower(d: dict, args: list):
    """将字典中指定的值最小化"""
    if isinstance(d, dict):
        for k in args:
            if k in d:
                d[k] = d[k].lower()
    else:
        raise


class FileHandler:
    """
    对上传文件的处理，保存、删除等
    """
    def __init__(self):
        from App.setting import UPLOAD_DIR
        self.upload_dir = UPLOAD_DIR

    @staticmethod
    def secure_name(name: str) -> str:
        return secure_filename(name)

    @staticmethod
    def mkdir(dir_path):
        """
        创建文件夹，可创建多层目录，如果目录已经存在，则直接返回 True
        :param dir_path:    str         文件夹路径
        :return:            Boolean     True: 创建成功或者已经存在，False: 创建失败
        """
        return makedirs(dir_path, exist_ok=True)

    def abs_dirname(self, category):
        """
        获取存放文件的路径和文件名
        :param category:        str         所属业务
        :return:                str         abs_dir
        """
        dir_path = join(self.upload_dir, category.lower())
        result = dir_path.replace("\\", "/")

        return result

    def save_file(self, cat: str, file_obj) -> str:
        """保存 file_obj 文件"""
        work_dir = self.abs_dirname(cat)
        filename = self.secure_name(file_obj.filename)
        self.mkdir(work_dir)

        # 保存文件
        abs_filepath = f"{work_dir}/{filename}"
        file_obj.save(abs_filepath)

        return work_dir

    def move_to(self, src_cat: str, dst_cat: str, filename: str) -> str:
        """
        将文件 filename 从 src 移动到 dst 目录
        """
        src_dir = self.abs_dirname(src_cat)
        src_file_path = f"{src_dir}/{filename}"

        dst_dir = self.abs_dirname(dst_cat)
        dst_file_path = f"{dst_dir}/{filename}"

        # 如果目标文件夹不存在，则创建
        self.mkdir(dst_dir)

        # [2020-06-17] 移动文件, 如果目标存在相同文件，则删除后再移动
        if self.exists(dst_file_path):
            remove(dst_file_path)
        move(src_file_path, dst_file_path)

        # [2020-06-17] 如果源目录为空，则删除
        if self.is_dir_empty(src_dir):
            self.rm_dir(src_dir)

        return dst_dir

    def del_file(self, cat: str, filename: str):
        """删除文件, category 专用"""
        work_dir = self.abs_dirname(cat)
        file_path = f"{work_dir}/{filename}"

        if self.exists(file_path):
            remove(file_path)

        # 如果目录是空的，则删除目录，这里指的是名为 {cat} 的目录
        self.rm_dir(work_dir)

    def rm_dir(self, path: str) -> bool:
        """
        category 目录专用
        如果目录是空的，删除末尾的空目录
        非递归删除
        """
        if self.exists(path) and self.is_dir_empty(path) and len(path.strip()) > len(self.upload_dir):
            rmdir(path)

        return True

    @staticmethod
    def is_dir_empty(path: str) -> bool:
        """判断目录(/文件夹)是否为空"""
        return len(listdir(path)) == 0

    def exists(self, path: str) -> bool:
        """文件或者目录是否存在"""
        return exists(path)
