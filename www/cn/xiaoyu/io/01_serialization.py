#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""
序列化
"""

import pickle
import json

##### pickle #####
d = dict(name='Roin', age='24', score=98)
# 将对象序列化成字节数组
print(pickle.dumps(d))

with open('dump.pickle', 'wb') as f:
    pickle.dump(d, f)

with open('dump.pickle', 'rb') as f:
    df = pickle.load(f)
    print(df)

##### json #####
d = dict(name='Roin', age='24', score=98)
print(json.dumps(d))

json_str = '{"score": 98, "name": "Roin", "age": "24"}'
print(json.loads(json_str))


##### json object #####
class Student(object):
    def __init__(self, name, age, score):
        self.name = name
        self.age = age
        self.score = score


def student2dict(std):
    """ 将str转化为数组 """
    return {
        'name': std.name,
        'age': std.age,
        'score': std.score
    }


def dict2student(d):
    return Student(d['name'], d['age'], d['score'])


stu = Student("Roin", 23, 97)
print(json.dumps(stu, default=student2dict))
print(json.dumps(stu, default=lambda obj: obj.__dict__))

json_str = '{"age": 22, "score": 96, "name": "Roin"}'
print(json.loads(json_str, object_hook=dict2student))
