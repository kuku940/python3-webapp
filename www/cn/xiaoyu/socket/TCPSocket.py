#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""
socket 连接演示
"""

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('www.baidu.com', 80))

# 发送数据
s.send(b'GET / HTTP/1.1\r\nHost: www.baidu.com\r\nConnection: close\r\n\r\n')

# 接受数据
buffer = []
while True:
    # 每次最多接受1k字节
    d = s.recv(1024)
    if d:
        buffer.append(d)
    else:
        break
data = b''.join(buffer)

# 关闭连接
s.close()

header, html = data.split(b'\r\n\r\n', 1)
print(header.decode('utf-8'))

# 写入文件
with open('../../../tmp/baidu.html', 'wb') as f:
    f.write(html)
