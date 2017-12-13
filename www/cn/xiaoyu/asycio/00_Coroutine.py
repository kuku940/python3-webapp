#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""
协程，又称微线程，纤程。英文名Coroutine
"""


def consumer():
    # 通过yield拿到消息，处理，又通过yield把结果传回
    r = ''
    while True:
        n = yield r
        if not n:
            return
        print('[CONSUMER] Consuming %s...' % n)
        r = '200 OK'


def produce(c):
    # 启动生成器
    c.send(None)
    n = 0
    while n < 5:
        n = n + 1
        print('[PRODUCER] Producing %s...' % n)
        # 生产了东西，通过c.send(n)切换到consumer执行
        # 拿到consumer处理的结果，继续生产下一条消息
        r = c.send(n)
        print('[PRODUCER] Consumer return: %s' % r)
    c.close()  # 通过c.close()关闭consumer，整个过程结束


c = consumer()
produce(c)
