#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import os
import time
from io import StringIO, BytesIO

########## 文件读写 ##########
# 一次性全部取出
with open('../../../tmp/baidu.html', 'r', errors='ignore') as f:
    print(f.read())  # 一次性全部取出

# 一行行的获取
with open('../../../tmp/baidu.html', 'r', encoding='utf-8') as f:
    for line in f.readlines():
        print(line.strip())  # 把末尾的'\n'去掉

# 一行行的获取
for line in open('../../../tmp/baidu.html', 'r', encoding='utf-8'):
    print(line.strip())

f = open('../../../tmp/1.jpg', 'rb')
print(f.read())  # 十六进制表示的字节
f.close()

f = open('../../../tmp/2.txt', 'w')
f.write('hello world!')
f.close()

########## StringIO ##########
### 在内存中读写str
f = StringIO()
f.write('hello')
f.write(' ')
f.write('world')
print(f.getvalue())

### 读取StringIO，可以用str初始化StringIO，然后和读取文件一样读取
f = StringIO("Hello!\nRoin!\nGoodbye!")
while True:
    s = f.readline()
    if s == '':
        break
    print(s.strip())

########## BytesIO ##########
### 在内存中操作二进制数据
f = BytesIO()
f.write('中文'.encode('utf-8'))
print(f.getvalue())

f = BytesIO(b'\xe4\xb8\xad\xe6\x96\x87')
print(f.read())

########## 操作文件和目录 ##########
print(os.name)  # 操作系统类型，nt -> windows;posix -> linux/unix/mac
print(os.environ)  # 环境变量
print(os.environ.get('PATH'))
print(os.environ.get('x', 'default'))

print(os.path.abspath('.'))
print(os.path.abspath('/'))
print(os.path.join('D:/', 'testdir'))

path = 'D:/testdir'
if not os.path.exists(path):
    os.makedirs(path)

filepath = 'D:/testdir/1.txt'
print(os.path.split(filepath))
print(os.path.splitext(filepath))

f = open(filepath, 'w')
f.write('hello world!')
f.close()

# os.rename(f, '2.txt')

time.sleep(1)
os.remove('D:/testdir/1.txt')
os.rmdir(path)

## 列出所有的文件夹和py文件
print([x for x in os.listdir('.') if os.path.isdir(x)])
print([x for x in os.listdir('.') if os.path.isfile(x) and os.path.splitext(x)[1] == '.py'])
