#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""
连接mysql数据库
"""

import mysql.connector

conn = mysql.connector.connect(user='root', password='123456', database='test')
cursor = conn.cursor()

# 创建user表
cursor.execute("create table user (id VARCHAR(20) PRIMARY KEY, name VARCHAR(20))")
cursor.execute("insert into user (id, name) VALUES (%s, %s)", ("1", "Roin"))

print("rowcount=", cursor.rowcount)
conn.commit()
cursor.close()

# 运行查询
cursor = conn.cursor()
cursor.execute("select * from user where id = %s", ('1',))
rs = cursor.fetchall()
print(rs)

cursor.close()
conn.close()
