#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""
asyncio是Python 3.4版本引入的标准库，直接内置了对异步IO的支持
"""

import asyncio


# 可以把一个generator标记为coroutine类型
@asyncio.coroutine
def wget(host):
    print('wget %s...' % host)
    connect = asyncio.open_connection(host, 80)
    # 用yield from调用另一个coroutine实现异步操作
    reader, writer = yield from connect
    header = 'GET / HTTP/1.0\r\nHost: %s\r\n\r\n' % host
    writer.write(header.encode('utf-8'))
    yield from writer.drain()
    while True:
        line = yield from reader.readline()
        if line == b'\r\n':
            break
        print('%s header > %s' % (host, line.decode('utf-8').rstrip()))
    # Ignore the body, close the socket
    writer.close()


# 获取EventLoop
loop = asyncio.get_event_loop()
tasks = [wget(host) for host in ['www.sina.com.cn', 'www.sohu.com', 'www.163.com']]
# 执行coroutime
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
