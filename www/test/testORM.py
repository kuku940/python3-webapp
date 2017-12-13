#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import asyncio
import pdb
import sys
import time

import orm
from models import User
from config import configs

"""
测试ORM操作的数据库的类，这儿使用快捷键Ctrl+shift+F10运行会直接报错
请使用右上角的三角运行
"""


async def test_save(loop):
    """ 测试插入 """
    await orm.create_pool(loop=loop, **configs.db)
    u = User(id='10086', name='Kitty', email='Kitty@example.com', passwd='Kitty', image='about:blank')
    await u.save()
    await orm.destory_pool()


async def test_findAll(loop):
    """ 测试查询 """
    await orm.create_pool(loop=loop, **configs.db)
    # 这里给的关键字参数按照xxx='xxx'的形式给出，会自动分装成dict
    rs = await User.findAll(email='test@example.com')  # rs是一个元素为dict的list
    await orm.destory_pool()
    for i in range(len(rs)):
        print(rs[i])


async def test_findNumber(loop):
    """ 查询条数 """
    await orm.create_pool(loop=loop, **configs.db)
    count = await User.findNumber('email')
    await orm.destory_pool()
    print(count)


async def test_find_by_key(loop):
    """ 根据主键查找，这里试ID """
    await orm.create_pool(loop=loop, **configs.db)
    # rs是一个dict
    # ID请自己通过数据库查询
    rs = await User.find('10086')
    await orm.destory_pool()
    print(rs)


async def test_update(loop):
    """ 根据主键更新 """
    await orm.create_pool(loop=loop, **configs.db)
    # 必须按照列的顺序来初始化：'update `users` set `created_at`=?, `passwd`=?, `image`=?,
    # `admin`=?, `name`=?, `email`=? where `id`=?' 注意这里要使用time()方法，否则会直接返回个时间戳对象，而不是float值
    u = User(id='10086', created_at=time.time(), passwd='Roin2',
             image='about:blank', admin=True, name='Roin2', email='Roin2@example.com')  # id必须和数据库一直，其他属性可以设置成新的值,属性要全
    await u.update()
    await orm.destory_pool()


async def test_remove(loop):
    """ 根据主键删除 """
    await orm.create_pool(loop=loop, **configs.db)
    # 用id初始化一个实例对象
    u = User(id='10086')
    await u.remove()
    await orm.destory_pool()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_save(loop))
    loop.run_until_complete(test_findAll(loop))
    loop.run_until_complete(test_findNumber(loop))
    loop.run_until_complete(test_find_by_key(loop))
    loop.run_until_complete(test_update(loop))
    loop.run_until_complete(test_find_by_key(loop))
    loop.run_until_complete(test_remove(loop))
    loop.run_until_complete(test_findAll(loop))
    loop.close()
