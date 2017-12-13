#!/usr/bin/env python
# _*_ coding:utf-8 _*_

mod = __import__('handlers')

for attr in dir(mod):
    # 如果是以'_'开头的，一律pass，我们定义的处理方法不是以'_'开头的
    if attr.startswith('_'):
        continue

    # 获取到非'_'开头的属性或方法
    fn = getattr(mod, attr)
    print(fn)
