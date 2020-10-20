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

"""
Productcode,
Processno,
Testitem,
Results,
Testingdata,
Datetime

产品码:Productcode
工序号: Processno
检测项目: Testitem
结果: Results
检测数据: Testingdata
日期时间: Datetime
"""
d = {
    "SDate": "2020-07-01",
    "EDate": "2020-07-02",
    "WorkDate": "2020-06-30T00:00:00",
    "BarCode": "P3696436;S202006241238;VSDL0055",
    "MaterialCode": 'null',
    "WorkcenterId": "WKC1000000KQ",
    "WorkcenterName": "H1ZA2-2-福田康明斯P3696436装配线",
    "SpecificationID": "SPE1000001AO",
    "SpecificationName": "OP10-装配",
    "PSpecSequence": 1,
    "CheckItem": "弹簧力",
    "StdRange": "152.6-168.8",
    "CheckValue": "157.1623",
    "CheckStatus": 1,
    "UserCodeList": "阳冬秀",
    "no": "1"
}
