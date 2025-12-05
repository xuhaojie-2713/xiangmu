#!/usr/bin/env python3
import phoenixdb

def connect():
    # 配置完整的Phoenix数据库URL
    # 端口默认8765
    global con
    phoenix_url = 'http://192.168.196.139:8765/'

    # 尝试连接到Phoenix
    try:
        con = phoenixdb.connect(url=phoenix_url,
                                auth_mechanism='PLAIN',
                                user='ye',
                                password='123456')
    except Exception as e:
        print(f"Failed to connect to Phoenix: {e}")

    return con
