import pandas as pd

# 读取原始数据
df = pd.read_csv('china_50_cities.csv', parse_dates=['Datetime'])

# 重命名列名（可选）
df.rename(columns={
    'CO(GT)': 'CO',
    'NOx(GT)': 'NOx',
    'NMHC(GT)': 'NMHC',
    'C6H6(GT)': 'C6H6',
    'NO2(GT)': 'NO2'
}, inplace=True)

# 提取关心的污染物
pollutants = ['CO', 'NOx', 'NMHC', 'C6H6', 'NO2']

# 保留关键信息
df_keep = df[['Datetime', 'Year', 'Month', 'Day', 'Hour', 'Latitude', 'Longitude'] + pollutants]

# 转换为长格式
df_melted = df_keep.melt(
    id_vars=['Datetime', 'Year', 'Month', 'Day', 'Hour', 'Latitude', 'Longitude'],
    value_vars=pollutants,
    var_name='Pollutant',
    value_name='Concentration'
)

# 去除缺失值
df_melted.dropna(subset=['Concentration'], inplace=True)

# 保存为 Tableau 使用的格式
df_melted.to_csv('tableau_ready_china_50_cities.csv', index=False)
