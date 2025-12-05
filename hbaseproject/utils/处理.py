import re
import time
import pandas as pd

path = r"F:\vs\hbaseproject\data\Data.csv"
path2 = r"F:\vs\hbaseproject\data\job2.csv"


def process_size(size_str):
    if '-' in size_str:
        # 如果存在"-"，分割字符串并取第二部分
        return int(size_str.split('-')[1].strip())
    else:
        # 否则，直接转换为整型
        return int(size_str)



# k
# def process_salary(salary_str):
#     # 去除"k"，并将"-"保留
#     # cleaned_str = salary_str.replace('K', '')
#     # return cleaned_str
#     str = salary_str
#     # 检查是否包含"以上"，并相应处理
#     if '以下' in str:
#         # 如果包含"以上"，我们只取"以上"前的数字部分
#         number_part = re.search(r'\d+', str.split('以下')[0]).group(0)
#         return number_part
#     else:
#         return str

# df = pd.read_csv(path, encoding="UTF-8")

# 使用正则表达式提取数字（数字-数字）
# df['companySize'] = df['companySize'].str.extract(r'(\d+-?\d*)')
# df.to_csv(path2, index=False)
# time.sleep(4)

df2 = pd.read_csv(path2, encoding="UTF-8")

# df2['salary'] = df2['salary'].apply(process_salary)
# df.to_csv(path2, index=False)
# # 应用函数到每一行
# df2['companySize'] = df2['companySize'].apply(process_size)
#
# df2['salary'] = df2['salary'].apply(process_size)
#
# df2.to_csv(path2, index=False)
# df_filled = df2.fillna('[nan]').astype(str)
# df_filled.to_csv(r"F:\vs\hbaseproject\data\job2.csv", index=False)

# for i in df2['positionLables']:
#     print(type(i))
# print(type(df2["companyLabelList"]))
def clean_value(value):
    if isinstance(value, str):
        # 替换或移除 Excel 不允许的字符
        return value.replace('"', '').replace(':', '').replace('/', '\\')
    return value

# 应用清理函数
df2 = df2.applymap(clean_value)

df2.to_excel(r"F:\vs\hbaseproject\data\job.xlsx")