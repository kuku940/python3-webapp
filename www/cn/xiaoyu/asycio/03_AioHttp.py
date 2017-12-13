#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""
编写一个Http服务器，分别处理一下URL
/ - 首页返回b'<h1>Index</h1>';
/hello/{name} - 根据URL参数返回文本hello, %s!
"""

import asyncio

from aiohttp import web


async def index(request):
    """
    定义首页
    :param request:
    :return:
    """
    await asyncio.sleep(0.5)
    return web.Response(body=b'<h1>Index</h1>', content_type="text/html")


async def hello(request):
    """
    定义其他页面
    :param request:
    :return:
    """
    await asyncio.sleep(0.5)
    text = '<h1>hello, %s!</h1>' % request.match_info['name']
    return web.Response(body=text.encode('utf-8'), content_type="text/html")


async def init(loop):
    """
    初始化init()也是一个coroutine
    loop.create_server()则利用asyncio创建TCP服务
    :param loop:
    :return:
    """
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    app.router.add_route('GET', '/hello/{name}', hello)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 8000)
    print('Server started at http://127.0.0.1:8000...')
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
