from utils.Condata import connect
import pandas as pd

con = connect()
cursor = con.cursor()

# 执行语句
def ddelete():
    r = "DROP TABLE IF EXISTS JOB2"
    cursor.execute(r)
    con.commit()
    print("删除成功")

# 创建表
def createtable():
    r = """
    CREATE TABLE IF NOT EXISTS JOB2 (
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
    print("创建成功")

# 输入数据
i = 0
def putdata(i):
    filepath = r"F:\vs\hbaseproject\data\job.xlsx"
    file = pd.read_excel(filepath)
    r = """
    UPSERT INTO JOB2 (
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

    # 将 companyLabelList 和 businessZones ,positionLables数组类型的字段转换为 JSON 字符串
    # row['companyLabelList'] = str(row['companyLabelList'])
    # row['businessZones'] = str(row['businessZones'])
    # row['positionLables'] = str(row['positionLables'])
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


    #     # 执行插入操作
    # with con.cursor() as cursor:
    #     for index, row in file.iterrows():
    #         params = (
    #             row['id'],
    #             row['city'],
    #             row['companyFullName'],
    #             row['companyId'],
    #             row['companyLabelList'],
    #             row['companyShortName'],
    #             row['companySize'],
    #             row['businessZones'],
    #             row['firstType'],
    #             row['secondType'],
    #             row['education'],
    #             row['industryField'],
    #             row['positionId'],
    #             row['positionAdvantage'],
    #             row['positionName'],
    #             row['positionLables'],
    #             row['salary'],
    #             row['workYear'],
    #         )
    #         cursor.execute(r, params)
    #         i += 1
    #         print(f"第{i}条数据已插入")
    #         try:
    #             # 插入数据的代码
    #             pass
    #         except Exception as e:
    #             print(f"在插入第 {i} 条数据时发生错误: {e}")
    #             # 可以在这里记录详细的错误信息或者进行其他的错误处理
    #     con.commit()
    #     con.close()



# createtable()
#ddelete()
putdata(0)