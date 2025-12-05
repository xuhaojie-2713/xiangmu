#!/usr/bin/env python3
from utils.Condata import connect
import pandas as pd

con = connect()
cursor = con.cursor()


# 执行语句
def ddelete():
    r = "DROP TABLE IF EXISTS JOB"
    cursor.execute(r)
    con.commit()
    print("删除成功")


# 创建表
def createtable():
    r = """
    CREATE TABLE IF NOT EXISTS JOB(
        id INTEGER PRIMARY KEY,
        city VARCHAR,
        companyFullName VARCHAR,
        companyId INTEGER,
        companyLabelList VARCHAR,
        companyShortName VARCHAR,
        companySize INTEGER,
        businessZones VARCHAR,
        firstType VARCHAR,
        secondType VARCHAR,
        education VARCHAR,
        industryField VARCHAR,
        positionId INTEGER,
        positionAdvantage VARCHAR,
        positionName VARCHAR,
        positionLables VARCHAR,
        salary INTEGER,
        workYear VARCHAR
    )
    """
    cursor.execute(r)
    con.commit()
    con.close()
    print("创建成功")


# 输入数据
i = 0

def inputdata(i):
    filepath = r"F:\vs\hbaseproject\data\job.xlsx"
    file = pd.read_excel(filepath)
    r = """
    UPSERT INTO JOB (
    id,
    city,
    companyFullName,
    companyId, 
    companyLabelList, 
    companyShortName, 
    companySize, 
    businessZones, 
    firstType, 
    secondType, 
    education, 
    industryField, 
    positionId, 
    positionAdvantage, 
    positionName, 
    positionLables, 
    salary, 
    workYear)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    with con.cursor() as cursor:
        cursor.arraysize = 1000  # 批量提交大小
        for index, row in file.iterrows():
            # 构造参数列表
            params = (
                row['id'],
                row['city'],
                row['companyFullName'],
                row['companyId'],
                row['companyLabelList'],
                row['companyShortName'],
                row['companySize'],
                row['businessZones'],
                row['firstType'],
                row['secondType'],
                row['education'],
                row['industryField'],
                row['positionId'],
                row['positionAdvantage'],
                row['positionName'],
                row['positionLables'],
                row['salary'],
                row['workYear'],
            )
            # 执行 UPSERT 语句
            cursor.execute(r, params)
            if index % cursor.arraysize == 0:
                con.commit()  # 定期提交事务
            i += 1
            print(f"第{i}条数据已插入")

    # 最后一次提交
    con.commit()
    con.close()


# createtable()
# ddelete()
# inputdata(0)
