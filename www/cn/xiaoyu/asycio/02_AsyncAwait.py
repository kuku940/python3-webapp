#!/usr/bin/env python
# _*_ coding:utf-8 _*_

'''
为了简化并更好地标识异步IO,3.5后引入了新的语法async和await
1.@asyncio.coroutine替换async
2.yield from替换为await
'''

import asyncio
import threading


# @asyncio.coroutine
# def hello(name):
#     print('Hello %s! %s' % (name, threading.Thread.name))
#     r = yield from asyncio.sleep(1)
#     print('Hello %s again! %s' % (name, threading.Thread.name))

async def hello(name):
    print('Hello %s! %s' % (name, threading.Thread.name))
    r = await asyncio.sleep(1)
    print('Hello %s again! %s' % (name, threading.Thread.name))


# 获取EventLoop:
loop = asyncio.get_event_loop()
tasks = [hello(name) for name in ['Jack', 'Robin', 'Pony']]
# 执行coroutine
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
