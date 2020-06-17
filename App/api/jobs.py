# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : __init__.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 15:39
--------------------------------------
"""
from copy import deepcopy

from flask import jsonify
from flask_restful import Resource, marshal
from flask_restful.fields import Integer, String, DateTime, Nested, List
from flask_restful.reqparse import RequestParser
from werkzeug.datastructures import FileStorage

from App.extensions import scheduler
from App.models.jobs import JobData, JobStatus
from App.models.logs import ModLog
from App.setting import *
from App.utils import (set_model_value, job_handler, get_next_time, save_job_data, save_job_status, up_job_status,
                       save_mod_log, cron_to_dict, up_job_data, del_job, rm_empty_kw, FileHandler, gen_cmd, to_lower
                       )

# Request 解析参数。自动去除值两边空格
parser_jobs = RequestParser(trim=True)

# 继承parser_job
parser_actions = parser_jobs.copy()
# 继承 parser_job
parser_put = parser_jobs.copy()
# ============================================== [ parser_job ] ==============================================
parser_jobs.add_argument("timeStyle", dest="time_style", type=str, required=True, choices=[f"{TRIGGER_TYPE_CRON}", ],
                         help=f"请输入时间风格, [{TRIGGER_TYPE_CRON}|{TRIGGER_TYPE_DATE}|{TRIGGER_TYPE_INTERVAL}]")

parser_jobs.add_argument("timeData", dest="time_data", type=str, required=True, help="请输入执行时间，如 0 5 * * *")
parser_jobs.add_argument("jobType", dest="job_type", type=str, required=True,
                         choices=[f"{JOB_TYPE_CLI}", f"{JOB_TYPE_SCRIPT}"],
                         help=f"请输入正确的任务类型,[{JOB_TYPE_CLI}|{JOB_TYPE_SCRIPT}]")

parser_jobs.add_argument("jobCmd", dest="job_cmd", type=str, help="请输入任务运行命令, 如 python test.py")
parser_jobs.add_argument("createdBy", dest="created_by", type=str, required=True, help="请输入任务创建人姓名")
parser_jobs.add_argument("category", dest="category", type=str, required=True,
                         help="请输入任务所属业务，[mes|erp|warranty|radar|pms|stopcard|...]")

parser_jobs.add_argument("desc", dest="desc", type=str, required=True, help="请输入任务描述")
# 文件上传
parser_jobs.add_argument("file", type=FileStorage, help="请上传文件", location=["files"])

# ============================================== [ parser_action ] ==============================================
parser_actions.add_argument("action", type=str, required=True, help="请输入操作名称")

# ================================================ [ parser_put ] ================================================
# 5个参数 action, timeStyle, timeData, desc, category
parser_put.add_argument("timeStyle", dest="time_style", type=str, choices=[f"{TRIGGER_TYPE_CRON}", ],
                        help=f"请输入时间风格, [{TRIGGER_TYPE_CRON}|{TRIGGER_TYPE_DATE}|{TRIGGER_TYPE_INTERVAL}]")

parser_put.add_argument("jobType", dest="job_type", type=str,
                        choices=[f"{JOB_TYPE_CLI}", f"{JOB_TYPE_SCRIPT}"],
                        help=f"请输入正确的任务类型,[{JOB_TYPE_CLI}|{JOB_TYPE_SCRIPT}]")

parser_put.add_argument("jobCmd", dest="job_cmd", type=str, help="请输入任务运行命令, 如 python test.py")
parser_put.add_argument("timeData", dest="time_data", type=str, help="请输入执行时间，如 0 5 * * *")
parser_put.add_argument("createdBy", dest="created_by", type=str, help="请输入需求人")
parser_put.add_argument("category", dest="category", type=str,
                        help="请输入任务所属业务，[mes|erp|warranty|radar|pms|stopcard|...]")
# 文件类型
parser_put.add_argument("file", type=FileStorage, help="请上传文件", location=["files"])
parser_put.add_argument("desc", dest="desc", type=str, help="请输入任务描述")

# ============================================== [ parser done ] ==============================================
post_fields = {
    "jobName": String(attribute="job_name"),
    "job_type": String(attribute="job_type"),
    "jobCmd": String(attribute="job_cmd"),
    "timeStyle": String(attribute="time_style"),
    "timeData": String(attribute="time_data")
}

posts_fields = {
    "status": Integer,
    "msg": String,
    "total": Integer,
    "data": List(Nested(post_fields))
}

job_fields = {
    "jobName": String(attribute="job_name"),
    "job_type": String(attribute="job_type"),
    "jobCmd": String(attribute="job_cmd"),
    "nextRunTime": DateTime(attribute="next_run_time", dt_format="iso8601"),
    "timeStyle": String(attribute="time_style"),
    "category": String(attribute="category"),
    "file": String(attribute="file_name", default=""),
    "desc": String(attribute="desc"),
}

jobs_fields = {
    "status": Integer,
    "msg": String,
    "total": Integer,
    "data": List(Nested(job_fields))
}


class JobsResource(Resource):
    """
    Job CRUD/RUN/PAUSE/RESUME
    rules:
        1) category 字段用小写
        2) file_name 字段大小写敏感
        3) job_type 字段用小写
        4) time_style 字段小写
    """
    def get(self, job_name):
        """
        任务获取,可获取单个，多个
        """
        status, msg, error = HTTP_OK, MSG_JOB_QUERY_SUCCESS, ""
        job_name = str(job_name.strip())
        jobs_data, result_data = [], []

        # 部分job data
        if job_name.lower() != "all":
            if ";" not in job_name:
                jobs_data = [scheduler.get_job(job_name)]

            else:
                job_names = job_name.split(";")
                for name in job_names:
                    jobs_data.append(scheduler.get_job(name))
        else:
            # 全部 job data
            jobs_data = scheduler.get_jobs()

        try:
            jobs_info = get_next_time(jobs_data)

            for item in jobs_info:
                _job = JobData.query.filter(JobData.job_name == item["job_name"]).first()

                _info = deepcopy(item)
                _info["job_type"] = _job.job_type
                _info["job_cmd"] = _job.job_cmd
                _info["time_style"] = _job.time_style
                _info["time_data"] = _job.time_data
                _info["category"] = _job.category
                _info["file_name"] = _job.file_name
                _info["desc"] = _job.desc
                result_data.append(_info)

        except AttributeError as err:
            status, msg = HTTP_QUERY_ERROR, MSG_JOB_QUERY_FAILED
            error = str(err)

        result = {
            "status": status,
            "msg": msg,
            "total": len(result_data),
            "data": result_data
        }

        result_fields = deepcopy(jobs_fields)

        if error:
            result["error"] = error
            result_fields["error"] = String

        return marshal(result, result_fields)

    def post(self, job_name):
        """
        TODO: [2020-06-12]
        改为 job_type 为 script 时，job_cmd 为空时，自动根据 file 上传脚本生成 job_cmd 内容，
        同时，也支持 job_cmd 输入命令， 检测命令中含有的脚本名称。
        更改涉及到 JobData/RunningLog 等表，get/post/put逻辑
        添加一个任务
        """
        job_args = parser_jobs.parse_args()

        full_data = {"job_name": job_name}
        set_model_value(full_data, job_args)

        # 去掉没有值的键值对儿
        full_data = rm_empty_kw(full_data)

        # category/time_style/job_type 都用小写
        to_lower(full_data, LOWER_KEYS)

        status, msg, error = HTTP_CREATED_OK, MSG_JOB_CREATED_SUCCESS, ""

        fh = FileHandler()
        job_data = JobData.query.filter(JobData.job_name == job_name).first()

        try:
            _exist = scheduler.get_job(job_name)
            _exist_cat = _exist_file_name = False

            _arg_cat = full_data.get("category").lower()
            _arg_file_name = ""

            if job_data:
                _exist_cat = _arg_cat == job_data.category

                if "file" in full_data:
                    _filename = full_data.get("file").filename
                    _arg_file_name = fh.secure_name(_filename)
                    _exist_file_name = _arg_file_name == job_data.file_name

            if _exist_cat and _exist_file_name:
                raise Exception(f"Category'{_arg_cat}'下已经存在 文件'{_arg_file_name}'。")

            if not _exist:
                # 准备添加到调度的数据
                sched_dict = {
                    "job_name": job_name,
                    "job_cmd": job_args.job_cmd,
                    "time_style": job_args.time_style.lower(),
                    "time_data": job_args.time_data,
                    "cwd": None
                }
                job_type = full_data["job_type"]

                # 纯粹执行命令
                if job_type == JOB_TYPE_CLI:
                    if "file" in full_data:
                        raise Exception("jobType 为'cli'时，不需要'file' 字段。")

                    work_dir = fh.abs_dirname(full_data["category"])    # 执行脚本或者命令时切换到的目录，即工作目录
                    work_dir = fh.mkdir(work_dir)                       # 创建目录
                    sched_dict["cwd"] = work_dir

                elif job_type == JOB_TYPE_SCRIPT:

                    if "file" not in full_data:
                        raise Exception("'file'字段为空。")

                    # 替换命令中的文件名称为安全的文件名称，防止意外
                    # Demo: "../../test.py" -> "test.py"
                    file_content = job_args.file
                    filename_src = file_content.filename
                    filename_secure = fh.secure_name(filename_src)

                    full_data["file_name"] = filename_secure

                    # 如果 job_cmd 有值
                    # 与这里相反的情况是 job_cmd 没有值，而 file 有值，通过 file 生成 job_cmd
                    if "job_cmd" in full_data:
                        job_cmd = job_args.job_cmd
    
                        if filename_src not in job_cmd:
                            raise Exception("'jobCmd'命令中未发现'file'中的文件名")
                        else:
                            job_cmd = job_cmd.replace(filename_src, filename_secure)

                        full_data["job_cmd"] = sched_dict["job_cmd"] = job_cmd

                    # 如果job_cmd 字段没有值，则根据 file 字段的 filename 推断命令，赋值给 job_cmd
                    else:
                        cmd = gen_cmd(filename_secure)
                        full_data["job_cmd"] = sched_dict["job_cmd"] = cmd

                    # ===================[ 无论有没有 job_cmd 都要进行的操作, start ]====================
                    work_dir = fh.save_file(job_args.category, job_args.file)
                    sched_dict["cwd"] = work_dir
                    # ====================[ 无论有没有 job_cmd 都要进行的操作, end ]=====================

                    if "file" in full_data:
                        # 删除 file 字段，该字段不保存到数据库
                        full_data.pop("file")

                # job 数据保存到数据库, 这步在 job_handler 之前是因为执行器要查 JobData 表
                save_job_data(full_data, JobData)

                # 将 job添加到调度
                job_handler(scheduler, sched_dict)

                # 添加job_name 到job 状态表
                save_job_status(job_name, JobStatus)

                # 添加job 修改日志
                save_mod_log(ACTION_CREATED, full_data, ModLog, JobData)

            else:
                status = HTTP_CONFLICT
                msg = MSG_JOB_EXISTED

        except Exception as err:
            status = HTTP_CREATED_FAILED
            msg = MSG_JOB_CREATED_FAILED
            error = str(err)

        result = {
            "status": status,
            "msg": msg,
            "total": 0 if error else 1,
            "data": full_data
        }

        result_fields = deepcopy(posts_fields)

        # 如果出现错误，则在返回结果中加上报错内容
        if error:
            result["error"] = error
            result_fields["error"] = String
            result_fields.pop("data")

        return marshal(result, result_fields)

    def put(self, job_name):
        """
        处理任务操作 暂停/恢复/立即执行
        """
        args_actions = parser_actions.parse_args()
        action = args_actions.get("action").lower()

        msg, error = "", ""

        # 任务暂停
        if action == "pause":
            try:
                scheduler.pause_job(job_name)  # 暂停
                up_job_status(job_name, JobStatus, STATUS_DICT.get(action))  # 修改任务状态
                save_mod_log(action, {"job_name": job_name}, ModLog, JobData)  # 保存人为动作
                msg = MSG_JOB_PAUSED_SUCCESS
            except Exception as err:
                error = str(err)
                msg = MSG_JOB_PAUSED_FAILED

        # 任务恢复
        elif action == "resume":
            try:
                scheduler.resume_job(job_name)  # 恢复
                up_job_status(job_name, JobStatus, STATUS_DICT.get(action))  # 修改任务状态
                save_mod_log(action, {"job_name": job_name}, ModLog, JobData)  # 保存人为动作
                msg = MSG_JOB_RESUMED_SUCCESS
            except Exception as err:
                error = str(err)
                msg = MSG_JOB_RESUMED_FAILED

        # 任务立刻执行
        elif action == "run":
            """
            [2020-06-03]
            Q: 为什么在 run_job 前后加上 pause_job 和 resume_job？
            A: 主要是考虑到在任务运行期间，假设该任务的调度时间也到了，会造成两次运行。
               对于某些内部逻辑没有限制的任务，同时运行两个实例，结果是灾难性的。
               所以，为了防止这种情况发生,首先暂停该任务的调度（在内部源码上的实现是将 next_run_time 置空）
               在程序运行完成后，再恢复该程序的调度。这样，可以尽最大可能避免两个实例在运行。
               同时在配置中，max_instance=1 和 coalesce=True，这两个组合，也可以避免多个实例同时运行。
            """

            # 获取run之前的状态
            next_time = scheduler.get_job(job_name).next_run_time
            before_run_status = STATUS_SLEEP if next_time else STATUS_PAUSED

            try:
                # 总的思想是，run完成后，恢复run之前的调度状态
                if before_run_status == STATUS_SLEEP:
                    scheduler.pause_job(job_name)

                up_job_status(job_name, JobStatus, STATUS_DICT.get(action))    # 修改任务状态
                save_mod_log(action, {"job_name": job_name}, ModLog, JobData)  # 保存人为动作

                scheduler.run_job(job_name)  # 运行
                msg = MSG_JOB_RUNNING_SUCCESS

            except Exception as err:
                error = str(err)
                msg = MSG_JOB_RUNNING_FAILED

            finally:
                run_result = RESULT_SUCCESS if not error else RESULT_FAILED
                up_job_status(job_name, JobStatus, before_run_status, run_result)  # 修改任务状态

                if before_run_status == STATUS_SLEEP:
                    scheduler.resume_job(job_name)  # 恢复

        # 更改除job_name外的 job信息
        elif action == "update":
            args_update = parser_put.parse_args()

            full_data = {"job_name": job_name}
            set_model_value(full_data, args_update)
            # 移除没有值的键值对儿
            full_data = rm_empty_kw(full_data)

            # 对指定的键值小写
            to_lower(full_data, LOWER_KEYS)

            # 用于更新 job 的数据
            changes = {}

            try:
                # 禁止修改 job_type
                if "job_type" in full_data:
                    raise Exception("'jobType'字段不能修改")

                # ======================[ 这里限定了 time_style 和 time_data 必须同时出现 ] ============================
                # 若修改 time_data 数据，time_style 必须同时指定，若不指定后者，默认 time_style 为 date 风格
                if "time_style" in full_data and "time_data" in full_data:

                    # 字符串时间变字典时间
                    # Demo: "*/1 * * * *" → {"minute": "*/1", "hour": "*", "day": "*", "month": "*", "day_of_week": "*"}
                    trigger_data = cron_to_dict(CRON_KEYS, full_data.get("time_data"))
                    changes["trigger"] = full_data.get("time_style")
                    changes.update(trigger_data)    # 时间风格

                elif "time_style" in full_data and "time_data" not in full_data:
                    raise Exception("'timeData'没有值或者缺失, 该字段要与'timeStyle'字段同时使用")

                elif "time_style" not in full_data and "time_data" in full_data:
                    raise Exception("'timeStyle'没有值或者缺失, 该字段要与'timeData'字段同时使用")

                # =========================[ 这里处理 job_cmd、file 和 category 的关系 ] ===============================
                """
                1> 这里是整个SnailAPI最难的地方，逻辑复杂而繁琐。所以，经多次尝试，决定像图层一样分为三层
                    1）job 参数 kwargs
                    2）文件的移动、删除和更新
                    3）日志记录数据
    
                    这三层在代码上看起来是混乱的，就像多个图层合成一张图片一样。
                    如果按图层的角度去看，结构比较清晰。
                    
                2> 另一种思想是：每个关键字段，只管处理自己相关的操作，不用全局考虑。
                   这样，大家都处理好自己的内容，整个任务都处理好了。
                   由简单的任务，组成复杂的任务，这才是符合计算机的逻辑，才是简单逻辑实现复杂逻辑的最优解思路。
                   
                   这种思想的字段处理顺序就有规定，最优顺序处理为：file > category > job_cmd
                   数据(包括中间数据)先 保存到 full_data 库，最后再组装 kwargs
                   
                   full_data 就是一个流水线托盘，上边放数据, 每一步只放处理好的数据，该删除的删除。
                   full_data 中的临时变量key 前用双单下划线表示，便于最后识别和处理, demo, full_data["__key"]
                   整个流程处理完成后，作为最终数据
                
                    [2020-06-16] 采用 2> 方案
                3> 心得，多个流程控制，不要怕繁琐和运行效率低下，这其实是将大问题分解为固定条件下的诸多小问题，逐个击破的策略。
                   这样，在写逻辑时，不容易出现考虑不到和复杂交织的情况
                """
                tmp_prefix = "__"
                t_secure_filename = f"{tmp_prefix}file_name"
                t_insecure_filename = f"{tmp_prefix}old_filename"
                t_cwd = f"{tmp_prefix}cwd"
                t_cmd = f"{tmp_prefix}cmd"
                t_cat = f"{tmp_prefix}category"

                fh = FileHandler()

                old_job_data = JobData.query.filter(JobData.job_name == job_name).first()
                old_job_type = old_job_data.job_type

                # 执行脚本类型的任务
                if old_job_type in (JOB_TYPE_CLI, JOB_TYPE_SCRIPT):

                    old_cat = old_job_data.category
                    old_filename = old_job_data.file_name

                    if "file" in full_data:
                        file = full_data.get("file")
                        new_filename = fh.secure_name(file.filename)

                        # =============================[ 处理 cmd: start ]==============================
                        old_cmd = old_job_data.job_cmd
                        if old_filename:
                            if old_filename in old_cmd:
                                new_cmd = old_cmd.replace(old_filename, new_filename)
                            else:
                                new_cmd = gen_cmd(new_filename)
                        else:
                            new_cmd = gen_cmd(new_filename)

                        full_data["cmd"] = full_data[t_cmd] = new_cmd
                        # ==============================[ 处理 cmd: end ]================================

                        # 删除旧文件
                        if old_filename:
                            fh.del_file(old_cat, old_filename)

                        # 保存新文件
                        fh.save_file(old_cat, file)

                        full_data["file_name"] = new_filename

                        # 传递给 category 字段处理用
                        # 如果 new != old ,则用 new， 如果 new == old，用 new 或 old 都一样, 所以，统一用 new。
                        full_data[t_secure_filename] = new_filename
                        full_data[t_insecure_filename] = file.filename

                        # file 字段不需要更新到数据库，去除掉
                        full_data.pop("file")

                    if "category" in full_data:
                        new_cat = full_data.get("category")

                        if new_cat != old_cat:
                            # 有可能更新 args 中，没有 file 字段，也就不会有 t_secure_filename
                            # 同理，jobData 中 file_name 也可能为空，也就是说，这是 job_type != "script"的任务

                            if t_secure_filename in full_data:
                                cat_filename = full_data.get(t_secure_filename)

                            else:
                                cat_filename = old_filename

                            if cat_filename:
                                # 有文件, 则将文件移动到新文件夹里
                                _ = fh.move_to(old_cat, new_cat, cat_filename)

                            else:
                                # 针对只是修改 category 且 job_type != "script" 的任务
                                cat_dir = fh.abs_dirname(new_cat)
                                fh.mkdir(cat_dir)

                            full_data["cwd"] = fh.abs_dirname(new_cat)

                        full_data[t_cwd] = fh.abs_dirname(new_cat)
                        full_data[t_cat] = new_cat

                    if "job_cmd" in full_data:
                        new_cmd = full_data.get("job_cmd")
                        filename_insecure = full_data.get(t_insecure_filename)

                        # 如果 t_insecure_filename 不在 job_cmd 中，替换也没问题，相当于没换
                        if filename_insecure:
                            filename_secure = full_data[t_secure_filename]

                            if filename_insecure not in new_cmd:
                                raise Exception(f"file'{filename_insecure}' 不在jobCmd`{new_cmd}`中。")
                            else:
                                new_cmd = new_cmd.replace(filename_insecure, filename_secure)

                        else:
                            # # 这里的完整分分支结构，是为了让思考难度降低
                            # # 没有文件就用原始的命令
                            # # new_cmd = new_cmd
                            pass
                        full_data["job_cmd"] = full_data["cmd"] = new_cmd

                    else:
                        # # 这里的完整分分支结构，是为了让思考难度降低
                        # # 没有 job_cmd 就用之前 file 处理中得到的 cmd 和 t_cmd
                        if "cmd" in full_data:
                            full_data["job_cmd"] = full_data["cmd"]

                    # 去掉临时变量
                    full_data_keys = list(full_data.keys())
                    for k in full_data_keys:
                        if k.startswith(tmp_prefix):
                            full_data.pop(k)

                # =========================[ 一个文件夹内执行某个脚本 ]=========================
                elif old_job_type == JOB_TYPE_DIR:
                    # TODO:
                    raise ValueError(f"'jobType'为'{JOB_TYPE_DIR}'类型的命令暂时不支持")

                # ========================[ 组装 job 参数, start ]=========================
                full_data_keys = set(full_data.keys())

                if "cmd" in full_data_keys or "cwd" in full_data_keys:
                    kwargs = {
                        "job_name": job_name,
                        "cmd": full_data.get("cmd") or old_job_data.job_cmd,
                        "cwd": full_data.get("cwd") or fh.abs_dirname(old_job_data.category)
                    }

                    kwargs_eys = list(kwargs.keys())

                    for _k in kwargs_eys:
                        if _k != "job_name" and _k in full_data_keys:
                            kwargs[_k] = full_data.pop(_k)

                        elif _k == "job_name":
                            continue

                    changes["kwargs"] = kwargs

                # =========================[ 组装 job 参数, end ]==========================

                if changes:
                    # 对调度涉及到的参数的修改生效
                    scheduler.modify_job(job_name, **changes)

                """
                [2020-06-10]
                对于上传文件的分类，是按照 category 字段进行的。
                category 改变，该任务对应的脚本也要移动到对应的文件夹中。
                同时，执行脚本的工作目录值(cwd 参数)也要改变。
                这样，才能保持文件所在目录和 category 是一致的，调度任务执行时才能找到要执行的脚本。
                在查看文件内容时，才能保证能找到文件, 从而展示脚本内容。
                """

                # 更新该job在JobData中的元数据
                up_job_data(full_data, JobData)

                # 将更改记录保存到日志
                save_mod_log(ACTION_UPDATED, full_data, ModLog, JobData)
                msg = MSG_JOB_MODIFIED_SUCCESS

            except Exception as err:
                error = str(err)
                msg = MSG_JOB_MODIFIED_FAILED

        status = HTTP_OK if not error else HTTP_EXECUTE_FAILED
        result = {
            "status": status,
            "msg": msg,
            "jobName": job_name,
            "action": action
        }

        # 如果出现错误，则在返回结果中加上报错内容
        if error:
            result["error"] = error

        return jsonify(result)

    def delete(self, job_name):
        """
        删除指定 job
        :param job_name:        str/list    要删除的 job
        """
        error = ""
        is_exist = scheduler.get_job(job_name)

        try:
            if is_exist:
                args = {"job_name": job_name}
                # 移除
                scheduler.remove_job(job_name)

                # 注意这里的顺序，先添加移除日志，再移除，否则移除日志找不到元数据
                save_mod_log(ACTION_DELETED, args, ModLog, JobData)

                # 删除文件，如果有文件
                job_data = JobData.query.filter(JobData.job_name == job_name).first()
                cat, filename = job_data.category, job_data.file_name

                if filename:
                    FileHandler().del_file(cat, filename)

                # 删除jobStatus/jobData 中的数据
                del_job(job_name, JobStatus, JobData)

        except Exception as err:
            error = str(err)

        status, msg = (HTTP_EXECUTE_FAILED, MSG_JOB_DELETED_FAILED) if error else (HTTP_OK, MSG_JOB_DELETED_SUCCESS)
        msg = MSG_JOB_DELETED_AGAIN if not is_exist else msg

        result = {
            "status": status,
            "msg": msg,
            "jobName": job_name,
            "action": ACTION_DELETED
        }

        # 如果出现错误，则在返回结果中加上报错内容
        if error:
            result["error"] = error

        return jsonify(result)
