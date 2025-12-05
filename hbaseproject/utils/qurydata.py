# #!/usr/bin/env python3
from utils.Condata import connect

# 行业-公司数据
def get_secondType():
    con = connect()
    cursor = con.cursor()

    # SQL 查询语句，用于选择 secondType 列的所有不同值及其出现次数
    query = """
    SELECT secondType, COUNT(*) as count 
    FROM JOB 
    GROUP BY secondType
    """

    cursor.execute(query)
    # category_counts = []  # 创建一个列表来存储分类和出现次数的字典
    secondTypename = []
    secondTypecount = []

    # 从查询结果中获取所有不同的分类及其出现次数
    for row in cursor:
        # category_dict = {"name": row[0], "value": row[1]}
        # category_counts.append(category_dict)
        secondTypename.append(row[0])
        secondTypecount.append(row[1])
    con.close()
    return secondTypename,secondTypecount


# 公司招聘规模
def get_companysize():
    con = connect()
    cursor = con.cursor()

    # SQL 查询语句，用于按 secondType 统计 companySize 的总和
    # 注意：去掉了语句末尾的分号
    query = """
    SELECT secondType, SUM(companySize) as totalCompanySize
    FROM JOB
    GROUP BY secondType
    """

    cursor.execute(query)
    results = cursor.fetchall()  # 获取所有查询结果

    # 创建列表来存储每个 secondType 对应的 companySize 总和
    companyname = []
    companyvalue = []
    for row in results:
        companyname.append(row[0])
        companyvalue.append(row[1])

    con.close()
    return companyname, companyvalue


# 工作经验数据
def get_workyear_counts():
    con = connect()  # 连接到 Phoenix
    cursor = con.cursor()

    # SQL 查询语句，用于统计 workYear 的不同值及其出现次数
    query = """
    SELECT workYear, COUNT(*) as count 
    FROM JOB
    GROUP BY workYear
    """

    cursor.execute(query)

    # 使用字典来存储 workYear 和它的计数
    # 使用列表来存储包含 name 和 value 的字典
    workyear_counts = []

    for row in cursor:
        # 创建一个字典，包含 name 和 value
        workyear_dict = {"name": row[0], "value": row[1]}
        # 将字典添加到列表中
        workyear_counts.append(workyear_dict)


    con.close()  # 关闭数据库连接

    # 返回字典，其中包含 workYear 和它的计数
    return workyear_counts

# 学历数据
def get_education():
    con = connect()  # 连接到 Phoenix
    cursor = con.cursor()

    # SQL 查询语句，用于统计 education 的不同值及其出现次数
    query = """
    SELECT education, COUNT(*) as count 
    FROM JOB
    GROUP BY education
    """

    cursor.execute(query)

    # 使用列表来存储包含 name 和 value 的字典
    education_counts = []

    for row in cursor:
        # 创建一个字典，包含 name 和 value
        education_dict = {"name": row[0], "value": row[1]}
        # 将字典添加到列表中
        education_counts.append(education_dict)

    con.close()  # 关闭数据库连接

    # 返回包含字典的列表
    return education_counts


# 城市分布数据
def get_city():
    con = connect()  # 连接到 Phoenix
    cursor = con.cursor()

    # SQL 查询语句，用于统计 education 的不同值及其出现次数
    query = """
    SELECT city, COUNT(*) as count 
    FROM JOB
    GROUP BY city
    """

    cursor.execute(query)

    # 使用列表来存储包含 name 和 value 的字典
    city_name = []
    city_value = []

    for row in cursor:
        # 将字典添加到列表中
        city_name.append(row[0])
        city_value.append(row[1])

    con.close()  # 关闭数据库连接

    # 返回包含字典的列表
    return city_value, city_name


def get_top_five_job():
    con = connect()  # 连接到 Phoenix
    cursor = con.cursor()

    # SQL 查询语句，用于获取按 salary 降序排序的前五个 secondType
    query = """
    SELECT secondType, AVG(salary) as average_salary
    FROM JOB
    GROUP BY secondType
    ORDER BY average_salary DESC
    LIMIT 5
    """

    cursor.execute(query)

    job = []
    job_value = []

    for row in cursor:
        # 将查询结果添加到列表中
        job.append(row[0])
        job_value.append(row[1])
    float_salaries = [float(salary) for salary in job_value]

    con.close()  # 关闭数据库连接

    return job, float_salaries


# 公司种类数
def get_count_companies():
    con = connect()  # 连接到 Phoenix
    cursor = con.cursor()

    # SQL 查询语句，用于统计不同的 companyFullName 的数量
    query = """
    SELECT COUNT(DISTINCT companyFullName) AS unique_company_count
    FROM JOB 
    """

    cursor.execute(query)
    companysum = cursor.fetchone()  # 获取查询结果

    con.close()  # 关闭数据库连接

    # 返回唯一公司种类的数量
    return companysum[0]


def get_company_size_sum():
    con = connect()  # 连接到 Phoenix
    cursor = con.cursor()

    # SQL 查询语句，用于计算 companySize 列的总和
    query = """
    SELECT SUM(companySize) AS total_company_size
    FROM JOB
    """

    cursor.execute(query)
    companysize = cursor.fetchone()  # 获取查询结果

    con.close()  # 关闭数据库连接

    # 返回 companySize 列的总和
    return companysize[0]




