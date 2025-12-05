# 导入需要的库
import pandas as pd
import numpy as np

# 1. 读取数据(注意分隔符和小数点格式)
file_path = r'D:\worklocation\PycharmProjects\可视化\air_quality_viz\data\raw\AirQualityUCI.csv'
try:
    # 先不解析日期，只读取数据
    data = pd.read_csv(
        file_path,
        sep=';',  # 指定分隔符为分号
        decimal=',',  # 指定小数点格式为逗号
        na_values=[-200]  # 将-200视为缺失值
    )
    print("✅ 文件读取成功")
except FileNotFoundError:
    print("❌ 文件未找到，请检查路径是否正确")
    exit()
except Exception as e:
    print(f"❌ 读取文件时出错: {e}")
    exit()

# 2. 合并日期和时间列为一个日期时间列
try:
    # 如果时间部分使用的是点号作为分隔符，先替换为冒号
    data['Time'] = data['Time'].str.replace('.', ':', regex=False)
    # 将 'Date' 和 'Time' 列合并为一个日期时间列
    # 格式说明: %d/%m/%Y %H:%M:%S 表示日/月/年 时:分:秒
    data['Datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], format='%d/%m/%Y %H:%M:%S')
    print("✅ 日期时间列合并成功")
except KeyError:
    print("❌ 未找到 'Date' 或 'Time' 列，请检查文件列名")
    exit()
except Exception as e:
    print(f"❌ 合并日期时间列时出错: {e}")
    exit()

# 3. 将合并后的日期时间列设置为索引
try:
    data.set_index('Datetime', inplace=True)
    print("✅ 索引设置成功")
except KeyError:
    print("❌ 未找到 'Datetime' 列，请检查列名")
    exit()
except Exception as e:
    print(f"❌ 设置索引时出错: {e}")
    exit()

# 4. 删除无效列
try:
    # 删除所有名称包含 'Unnamed' 的列
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
    print("✅ 无效列已删除")
except Exception as e:
    print(f"❌ 删除无效列时出错: {e}")
    exit()

# 5. 处理缺失和重复值
try:
    # 检查索引中是否有NaN值
    if data.index.hasnans:
        print("⚠️ 索引中存在NaN值，正在进行处理...")
        # 重置索引，将日期时间列转换为普通列
        data = data.reset_index()
        # 填充索引中的NaN值，使用前向填充
        data['Datetime'] = data['Datetime'].ffill()
        # 将Datetime列重新设置为索引
        data = data.set_index('Datetime')

    # 删除重复索引，保留第一个出现的
    data = data[~data.index.duplicated(keep='first')]

    # 推断数据类型（避免FutureWarning）
    data = data.infer_objects(copy=False)

    # 进行时间加权插值填充缺失值
    data = data.interpolate(method='time', limit_direction='forward')
    print("✅ 缺失值处理完成")
except Exception as e:
    print(f"❌ 处理缺失值时出错: {e}")
    exit()

# 6. 提取时间特征
try:
    # 从索引中提取年份、月份、日期、小时和星期几
    data['Year'] = data.index.year
    data['Month'] = data.index.month
    data['Day'] = data.index.day
    data['Hour'] = data.index.hour
    data['Weekday'] = data.index.weekday  # 0 = 周一, 6 = 周日
    print("✅ 时间特征提取成功")
except Exception as e:
    print(f"❌ 提取时间特征时出错: {e}")
    exit()

# 7. 定义中国50个主要城市及其经纬度
china_cities = {
    '北京': (39.9042, 116.4074), '上海': (31.2304, 121.4737), '广州': (23.1291, 113.2644),
    '深圳': (22.5431, 114.0579), '杭州': (30.2741, 120.1551), '南京': (32.0603, 118.7969),
    '天津': (39.3434, 117.3616), '重庆': (29.5630, 106.5516), '成都': (30.5728, 104.0668),
    '武汉': (30.5928, 114.3055), '西安': (34.3416, 108.9398), '长沙': (28.2282, 112.9388),
    '郑州': (34.7466, 113.6254), '青岛': (36.0671, 120.3826), '大连': (38.9140, 121.6147),
    '厦门': (24.4798, 118.0894), '合肥': (31.8206, 117.2272), '济南': (36.6512, 117.1201),
    '宁波': (29.8683, 121.5440), '佛山': (23.0215, 113.1214), '苏州': (31.2989, 120.5853),
    '无锡': (31.4912, 120.3119), '昆明': (25.0389, 102.7189), '南昌': (28.6829, 115.8582),
    '南宁': (22.8170, 108.3669), '太原': (37.8706, 112.5489), '贵阳': (26.6477, 106.6302),
    '呼和浩特': (40.8426, 111.7492), '兰州': (36.0611, 103.8343), '哈尔滨': (45.8038, 126.5349),
    '长春': (43.8171, 125.3235), '沈阳': (41.8057, 123.4315), '石家庄': (38.0428, 114.5149),
    '唐山': (39.6305, 118.1809), '包头': (40.6574, 109.8403), '西宁': (36.6171, 101.7782),
    '银川': (38.4872, 106.2309), '海口': (20.0440, 110.1983), '乌鲁木齐': (43.8256, 87.6168),
    '拉萨': (29.6520, 91.1721), '珠海': (22.2707, 113.5767), '中山': (22.5159, 113.3926),
    '惠州': (23.1115, 114.4158), '东莞': (23.0207, 113.7518), '江门': (22.5751, 113.0815),
    '扬州': (32.3932, 119.4127), '镇江': (32.1896, 119.4250), '洛阳': (34.6186, 112.4536),
    '宜昌': (30.6919, 111.2865), '芜湖': (31.3525, 118.4335)
}

# 8. 平均划分数据到不同城市
try:
    df_list = []
    num_cities = len(china_cities)
    data_length = len(data)
    n = data_length // num_cities

    if data_length % num_cities != 0:
        print(f"⚠️ 数据行数({data_length})不能整除城市数({num_cities})，最后城市将多一点数据")

    for i, (city, (lat, lon)) in enumerate(china_cities.items()):
        # 计算当前城市的数据起始和结束索引
        start_idx = i * n
        # 如果是最后一个城市，确保包含所有剩余数据
        end_idx = data_length if i == (num_cities - 1) else start_idx + n

        chunk = data.iloc[start_idx:end_idx].copy()

        # 对污染物数据添加 ±5% 的随机噪声，模拟城市差异
        pollutants = ['CO(GT)', 'NMHC(GT)', 'C6H6(GT)', 'NOx(GT)', 'NO2(GT)']
        for p in pollutants:
            if p in chunk.columns:
                chunk[p] = chunk[p] * (1 + np.random.uniform(-0.05, 0.05, size=len(chunk)))

        # 添加城市信息
        chunk['Station'] = city
        chunk['Latitude'] = lat
        chunk['Longitude'] = lon

        df_list.append(chunk)

    print("✅ 城市数据分配完成")
except Exception as e:
    print(f"❌ 分配数据到城市时出错: {e}")
    exit()

# 9. 合并所有城市数据
try:
    multi_city_df = pd.concat(df_list).sort_index()
    print("✅ 数据合并成功")
except Exception as e:
    print(f"❌ 合并数据时出错: {e}")
    exit()

# 10. 保存处理后的数据
output_path = r'D:\worklocation\PycharmProjects\可视化\air_quality_viz\data\processed\china_50_cities.csv'
try:
    multi_city_df.to_csv(output_path)
    print(f"✅ 数据成功保存到 {output_path}")
except Exception as e:
    print(f"❌ 保存文件时出错: {e}")
    exit()