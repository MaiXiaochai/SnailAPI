#  SnailAPI接口使用说明

---

##### 1.RESTful规范

+ REST是什么

  REST（Representational State Transfer）表述性状态转换，**REST指的是一组架构约束条件和原则**。

  

+ URI规范
  + 不用大写

  + 用中杠`-`不用下杠`_`

  + 参数列表要`encode`

  + `URI`中的名词表示资源集合，使用复数形式

  + 过深的导航容易导致url膨胀，不易维护，如 

    `GET /zoos/1/areas/3/animals/4`，

    尽量使用查询参数代替路径中的实体导航，如

    `GET /animals?zoo=1&area=3`

    

+ **Request**

  通过标准HTTP方法对资源`CRUD`

  + GET：查询

    + `GET /zoos`
    + `GET /zoos/1`
    + `GET /zoos/1/employees`

    

  + POST：创建单个资源

    一般向“资源集合”型`URI`发起

    + `POST /animals ` 

      新增动物

    + `POST /zoos/1/employees `

      为`id`为`1`的动物园雇佣员工

      

  + PUT：更新单个资源（全量），客户端提供完整的更新后的资源

    + `PUT /animals/1`

    + `PUT /zoos/1`

      

  + PATCH：负责部分更新，客户端提供要更新的那些字段

    + `PATCH /animals/1`
    + `PATCH /zoos/1`

    

  + DELETE：删除

    + `DELETE /zoos/1/employees/2`

    + `DELETE /zoos/1/employees/2;4;5`

    + `DELETE /zoos/1/animals`

      删除`id`为`1`的动物园内的所有动物

+ **筛选**

  + 条件筛选

    + `?type=1&age=16`

    + 允许一定的uri冗余，如`/zoos/1`与`/zoos?id=1`

  + 排序
    + `?sort=age,desc`
  + 投影
    + `?whitelist=id,name,email`
  + 分页
    + `?limit=10&offset=3`

##### 2. SnailAPI 规范

+ **2.1 任务**

  + **2.1.1 新增单个任务**

    + `request`
      
        +  `timeStyle`:` cron|interval|date`(目前只支持`cron`，可以满足`99%`的需求)
        + `cateogry`: ` mes|erp|warranty|radar|pms|stopcard|...`（所属业务）
        + `jobType`: `cli|script|proc`(目前只支持`cli`)
        
        ```shell
        $ curl -X POST http://localhost:5000/api/jobs/{job_name}
          -H 'Content-Type: application/json'
          -d '{
                "jobType": "cli",
                "jobCmd": "echo %cd%",
                "timeStyle": "cron",
                "timeData": "*/1 * * * *",
                "createdBy": "san.zhang",
                "category": "mes",
                "desc": "打印执行时的路径"
              }'
        ```
        
    + `response`
    
      ```json
        {
            "status": 201,
            "msg": "任务添加成功",
            "jobName": "snail_job"
        }
      ```
    
  + **2.1.2 修改n(n≥1)个任务的状态**

    + 这里的`暂停`和`恢复`作用的对象是从此刻起，以后的执行计划。

      + 源码说明
        + `APScheduler`运行时，会将任务的`下次执行时间`写入数据库，然后去轮询这些时间。
          + `暂停`在内部的实现为，将数据库中的`下次执行时间`置空，这样在轮询的时候，就默认舍弃时间为空的任务
          + `恢复`在内部的实现与`暂停`相反，重新计算`下次执行时间`并写入数据库，运行时间有了，对该任务的轮询便恢复了

    + `request`

      + `pause|resume|run`: 暂停|恢复|立刻运行
      + 注意：`run`的时候，程序执行完成才会返回结果，请根据具体程序执行时长，设置`request` `timeout`
      
      ```shell
      $ curl -X PUT http://localhost:5000/api/jobs/{job_name1};{job_name2}
        -H 'Content-Type: application/json'
        -d '{
        		"action": "pause"
            }'
      ```
      
    + `response`
    
      ```shell
        {
            "status": 200,
            "msg": "任务已暂停",		# 任务恢复成功| 任务开始运行|任务运行成功
            "jobName": "snail_job",
            "action": "pause"
        }
      ```
    
      
    
  + **2.1.3 修改单个任务数据**

    + `request`
      
        + `"action": "update"`为必须字段和值
        + 修改时间信息时，`timeStyle`和`timeData`必须同时出现且有值
        + 可修改的字段为 `timeStyle`, `timeData`,`crea`, `cateogry`,`desc` 
        + 修改部分字段，只需要将值写入`json`内，并赋值即可，只有字段，值为空的字段不会被修改。
        
        ```shell
        $ curl -X PUT http://localhost:5000/api/jobs/{job_name}
          -H 'Content-Type: application/json'
          -d '{
          	    "action": "update",
                "timeStyle": "cron", 	# cron|interval|date
                "timeData": "*/1 * * * *",
                "createdBy": "maixiaochai",
                "category": "mes"， 	   # mes|erp|warranty|radar|pms|stopcard|...（所属业务）
              	"desc": "更新了全部可修改的字段"
              }'
        ```
    
  + **2.1.4 获取n(n≥1)个任务**

    + `request`
      
        ```shell
        $ curl -X GET http://localhost:5000/api/jobs/{job_name1};{job_name2};{job_name3}
        ```
        
    + `response`

      ```json
      {
          "status": 200,
          "msg": "查询成功",
          "total": 2,
          "data": [
              {
                  "jobName": "snail_job1",
                  "job_type": "cli",
                  "jobCmd": "echo [SnailAPI][%date%%time%][ Hello Flask ]",
                  "nextRunTime": "2020-06-02T23:27:00+08:00",
                  "timeStyle": "cron",
                  "timeData": "*/1 * * * *"
              },
              {
                  "jobName": "snail_job",
                  "job_type": "cli",
                  "jobCmd": "echo [SnailAPI][%date%%time%][ Hello Python ]",
                  "nextRunTime": "2020-06-02T23:27:00+08:00",
                  "timeStyle": "cron",
                  "timeData": "*/1 * * * *"
              }
          ]
      }
      ```
      

  + **2.1.5 获取所有任务**

    + `request`
      
        ```shell
      $ curl -X GET http://localhost:5000/api/jobs/all
      ```
      
    + `response`
    
        ```json
    // 因为只有两个任务， 这里只有两条数据
        {
        "status": 200,
            "msg": "查询成功",
            "total": 2,
            "data": [
                {
                    "jobName": "snail_job1",
                    "job_type": "cli",
                    "jobCmd": "echo [SnailAPI][%date%%time%][ Hello Flask ]",
                    "nextRunTime": "2020-06-02T23:27:00+08:00",
                    "timeStyle": "cron",
                    "timeData": "*/1 * * * *"
                },
                {
                    "jobName": "snail_job",
                    "job_type": "cli",
                    "jobCmd": "echo [SnailAPI][%date%%time%][ Hello Python ]",
                    "nextRunTime": "2020-06-02T23:27:00+08:00",
                    "timeStyle": "cron",
                    "timeData": "*/1 * * * *"
                }
            ]
        }
        ```

  + **2.1.6 删除单个任务**

    + `request`

      ```shell
      curl -X DELETE http://127.0.0.1:5000/api/jobs/{job_name}
      ```

    + `response`

      `"action": "D"`，表示任务状态为删除（`D: DELETE`）

      ```json
      {
          "action": "D",
          "jobName": "snail_job",
          "msg": "任务删除成功",
          "status": 200
      }
      ```

      

+ **2.2 日志**

    + **2.2.1 单个任务的最新n(n≥1)条运行日志，默认按开始时间降序**

        + `request`

            ```shell
            $ curl -X GET http://localhost:5000/api/jobs/{jobname}?total={log_number}
            ```
        
        + `response`
        
          + `stderr`，有错误的时候才会出错
          
          ```json
          // /snail_job?total=2
          {
              
              "msg": "查询成功",
              "total": 2,
              "data": [
                  {
                      "jobName": "snail_job",
                      "jobCmd": "echo [SnailAPI][%date%%time%][ Hello SnailAPI. ]",
                      "startDate": "2020-06-01T20:51:07.512103",
                      "endDate": "2020-06-01T20:51:07.524939",
                      "returnCode": 0,
                      "stdout": "[SnailAPI][2020/06/01 周一20:51:00.11][ Hello SnailAPI. ]\n",
                      "stderr": ""
                  },
                  {
                      "jobName": "snail_job",
                      "jobCmd": "echo [SnailAPI][%date%%time%][ Hello SnailAPI. ]",
                      "startDate": "2020-06-01T20:50:07.508854",
                      "endDate": "2020-06-01T20:50:07.519868",
                      "returnCode": 0,
                      "stdout": "[SnailAPI][2020/06/01 周一20:50:00.10][ Hello SnailAPI. ]\n",
                      "stderr": ""
                  }
              ]
        }
          ```
          
          
---

##### 修改历史

[2020-06-09]

+ 根据功能调整，修改部分接口的请求参数和响应数据
+ 新增任务数据修改的接口说明
+ 新增任务状态修改 的接口说明
+ 新增删除任务的接口说明

[2020-05-28]

+ 创建文档

  

参考文献：

+ [《RESTful API接口设计标准及规范》](https://blog.csdn.net/qq_41606973/article/details/86352787)



---
+ 作者：张川
+ Email：chuan.zhang@mabotech.com