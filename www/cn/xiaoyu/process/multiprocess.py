#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import os
import random
import time
from multiprocessing import Process, Queue
from multiprocessing import Pool
import subprocess


###### multiprocessing ######
def run_proc(name):
    print('Run child process %s (%s)...' % (name, os.getpid()))


###### Pool ######
def long_time_task(name):
    print('Run task %s (%s)...' % (name, os.getpid()))
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print('Task %s runs %0.2f seconds.' % (name, (end - start)))


###### 进程间通信 ######
def write(q):
    print("Process to write: %s" % os.getpid())
    for value in ['A', 'B', 'C']:
        print("Put %s to queue..." % value)
        q.put(value)
        time.sleep(random.random())


def read(q):
    print("Process to read: %s" % os.getpid())
    while True:
        value = q.get(True)
        print('Get %s from queue' % value)


if __name__ == '__main__':
    ## 启动子进程
    print('Parent process %s.' % os.getpid())
    p = Process(target=run_proc, args=('test',))
    print('Child process will start.')
    p.start()
    p.join()
    print('Child process end.')

    ## 进程池的方式批量创建子进程
    print('---------------------------------')
    print('Parent process %s.' % os.getpid())
    p = Pool(4)  # 同时跑4个进程
    for i in range(5):
        p.apply_async(long_time_task, args=(i,))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()  # 等待所有的子进程执行完成
    print('All subprocesses done.')

    ###### 子进程 ######
    print('$ nslookup www.baidu.com')
    r = subprocess.call(['nslookup', 'www.baidu.com'])
    print('Exit code:', r)

    ###### 子进程的输入 ######
    print('$ nslookup')
    p = subprocess.Popen(['nslookup'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate(b'set q=mx\npython.org\nexit\n')
    print(output)
    print('Exit code:', p.returncode)

    # 父进程创建Queue，并传给各个子进程：
    q = Queue()
    pw = Process(target=write, args=(q,))
    pr = Process(target=read, args=(q,))
    # 启动子进程pw，写入:
    pw.start()
    # 启动子进程pr，读取:
    pr.start()
    # 等待pw结束:
    pw.join()
    # pr进程里是死循环，无法等待其结束，只能强行终止:
    pr.terminate()
