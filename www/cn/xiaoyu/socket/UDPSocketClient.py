#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for data in [b'Jack', b'Pony', b'Robin']:
    s.sendto(data, ('127.0.0.1', 9999))
    print(s.recv(1024).decode('utf-8'))

s.close()
