#!/usr/bin/env python
# _*_ coding:utf-8 _*_

""" url handlers """

import hashlib
import json
import logging
import re
import time

from aiohttp import web

import markdown2
from apis import Page, APIValueError, APIResourceNotFoundError, APIPermissionError, APIError
from config import configs
from coroweb import get, post
from models import User, Comment, Blog, next_id

logging.basicConfig(level=logging.DEBUG)

COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret


def check_admin(request):
    """ 检测当前用户是不是admin用户 """
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()


def get_page_index(page_str):
    """ 获取页数，主要是做一些容错处理 """
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


def text2html(text):
    """ 把存文本文件转为html格式的文本 """
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;')
                .replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


def user2cookie(user, max_age):
    ''' 根据用户信息拼接一个cookie字符串 '''
    # build cookie string by: id-expires-sha1
    # 过期时间是当前时间+设置的有效时间
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    # 用-隔开，返回
    return '-'.join(L)


async def cookie2user(cookie_str):
    """ 根据cookie字符串，解析出用户信息相关的 """
    if not cookie_str:
        # cookie_str是空则返回
        return None
    try:
        # 通过'-'分割字符串
        L = cookie_str.split('-')

        # 如果不是3个元素的话，与我们当初构造sha1字符串时不符，返回None
        if len(L) != 3:
            return None
        # 分别获取到用户id，过期时间和sha1字符串
        uid, expires, sha1 = L

        # 如果超时，返回None
        if int(expires) < time.time():
            return None

        # 根据用户id查找库，对比有没有该用户
        user = await User.find(uid)

        # 没有该用户返回None
        if user is None:
            return None

        # 根据查到的user的数据构造一个校验sha1字符串
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)

        # 比较cookie里的sha1和校验sha1，一样的话，说明当前请求的用户是合法的
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'

        # 返回合法的user
        return user
    except Exception as e:
        logging.exception(e)
        return None


@get('/')
async def index(*, page='1'):
    # 获取需要展示的博客页数
    page_index = get_page_index(page)
    # 查找博客表里的条目数
    num = await Blog.findNumber('count(id)')
    # 通过Page类来计算当前页相关信息
    page = Page(num, page_index)

    # 如果表里没有条目，则不需要系那是
    if num == 0:
        blogs = []
    else:
        # 否则，根据计算出来的offset(取的初始条目index)和limit(取的条数)，来取出条目
        blogs = await Blog.findAll(orderBy='created_at desc', limit=(page.offset, page.limit))
        # 返回给浏览器
    return {
        '__template__': 'blogs.html',
        'page': page,
        'blogs': blogs
    }


########################### 注册登陆 ###########################

@get('/register')
def register():
    """ 注册页面 """
    return {
        '__template__': 'register.html'
    }


@get('/signin')
def signin():
    """ 登陆页面 """
    return {
        '__template__': 'signin.html'
    }


@get('/signout')
def signout(request):
    """ 登出操作 """
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user sign out.')
    return r


# email和密码 匹配正则表达式
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


@post('/api/users')
async def api_register_user(*, email, name, passwd):
    """ 注册操作 """
    # 判断name是否存在，且是否只是'\n', '\r',  '\t',  ' '，这种特殊字符
    if not name or not name.strip():
        raise APIValueError('name')
        # 判断email是否存在，且是否符合规定的正则表达式
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
        # 判断passwd是否存在，且是否符合规定的正则表达式
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')

    # 查一下库里是否有相同的email地址，如果有的话提示用户email已经被注册过
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')

    # 生成一个当前要注册用户的唯一uid
    uid = next_id()
    # 构建shal_passwd
    sha1_passwd = '%s:%s' % (uid, passwd)

    admin = False
    if email == 'admin@pywebapp.com':
        admin = True

    # 创建一个用户（密码是通过sha1加密保存）
    user = User(id=uid, name=name.strip(), email=email,
                passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(
                    email.encode('utf-8')).hexdigest(), admin=admin)

    # 保存这个用户到数据库用户表
    await user.save()
    logging.info('save user OK')
    # 构建返回信息
    r = web.Response()
    # 添加cookie
    r.set_cookie(COOKIE_NAME, user2cookie(
        user, 86400), max_age=86400, httponly=True)
    # 只把要返回的实例的密码改成'******'，库里的密码依然是正确的，以保证真实的密码不会因返回而暴漏
    user.passwd = '******'
    # 返回的是json数据，所以设置content-type为json的
    r.content_type = 'application/json'
    # 把对象转换成json格式返回
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@post('/api/authenticate')
async def authenticate(*, email, passwd):
    """ 登陆请求 """
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password.')
    users = await User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')

    # 取第一个查到用户，理论上就一个
    user = users[0]
    # check passwd: 按存储密码的方式获取出请求传入的密码字段的sha1值
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    # 和库里的密码字段的值作比较，一样的话认证成功，不一样的话，认证失败
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid password.')
    # authenticate ok, set cookie: 构建返回信息
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)

    # 只把要返回的实例的密码改成'******'，库里的密码依然是正确的，以保证真实的密码不会因返回而暴漏
    user.passwd = '******'
    r.content_type = 'application/json'
    # 把对象转换成json格式返回
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


########################### 评论管理 ###########################

@get('/manage/')
def manage():
    return 'redirect:/manage/comments'


@get('/manage/comments')
def manage_comments(*, page='1'):
    # 查看所有评论
    return {
        '__template__': 'manage_comments.html',
        'page_index': get_page_index(page)
    }


@get('/api/comments')
async def api_comments(*, page='1'):
    # 根据page获取评论，注释可参考 index 函数的注释，不细写了
    page_index = get_page_index(page)
    num = await Comment.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    comments = await Comment.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, comments=comments)


@post('/api/blogs/{id}/comments')
async def api_create_comment(id, request, *, content):
    # 对某个博客发表评论
    user = request.__user__
    # 必须为登陆状态下，评论
    if user is None:
        raise APIPermissionError('content')
    # 评论不能为空
    if not content or not content.strip():
        raise APIValueError('content')
    # 查询一下博客id是否有对应的博客
    blog = await Blog.find(id)
    # 没有的话抛出错误
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    # 构建一条评论数据
    comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name,
                      user_image=user.image, content=content.strip())
    # 保存到评论表里
    await comment.save()
    return comment


@post('/api/comments/{id}/delete')
async def api_delete_comments(id, request):
    # 删除某个评论
    logging.info(id)
    # 先检查是否是管理员操作，只有管理员才有删除评论权限
    check_admin(request)
    # 查询一下评论id是否有对应的评论
    c = await Comment.find(id)
    # 没有的话抛出错误
    if c is None:
        raise APIResourceNotFoundError('Comment')
    # 有的话删除
    await c.remove()
    return dict(id=id)


########################### 用户管理 ###########################

@get('/show_all_users')
async def show_all_users():
    # 显示所有的用户
    users = await User.findAll()
    logging.info('to index...')
    # return (404, 'not found')

    return {
        '__template__': 'test.html',
        'users': users
    }


@get('/api/users')
async def api_get_users(*, page='1'):
    # 返回分页的用户信息jason格式
    page_index = get_page_index(page)
    num = await User.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = await User.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    logging.info('users = %s and type = %s' % (users, type(users)))
    for u in users:
        u.passwd = '******'
    return dict(page=p, users=users)


@get('/manage/users')
async def manage_users(*, page='1'):
    # 查看所有用户
    return {
        '__template__': 'manage_users.html',
        'page_index': get_page_index(page)
    }


########################### 博客管理 ###########################

@get('/manage/blogs/create')
def manage_create_blog():
    # 写博客页面
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs'  # 对应HTML页面中VUE的action名字
    }


@get('/manage/blogs')
def manage_blogs(*, page='1'):
    # 博客管理页面
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page)
    }


@get('/api/blogs')
async def api_blogs(*, page='1'):
    # 获取博客信息
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)


@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content):
    # 只有管理员可以写博客
    check_admin(request)
    # name，summary,content 不能为空
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty')

    # 根据传入的信息，构建一条博客数据
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name,
                user_image=request.__user__.image, name=name.strip(), summary=summary.strip(), content=content.strip())
    # 保存
    await blog.save()
    return blog


@get('/blog/{id}')
async def get_blog(id):
    # 根据博客id查询该博客信息
    blog = await Blog.find(id)
    # 根据博客id查询该条博客的评论
    comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    # markdown2是个扩展模块，这里把博客正文和评论套入到markdonw2中
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content)
    # 返回页面
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments
    }


@get('/api/blogs/{id}')
async def api_get_blog(*, id):
    # 获取某条博客的信息
    blog = await Blog.find(id)
    return blog


@post('/api/blogs/{id}/delete')
async def api_delete_blog(id, request):
    # 删除一条博客
    logging.info("删除博客的博客ID为：%s" % id)
    # 先检查是否是管理员操作，只有管理员才有删除评论权限
    check_admin(request)
    # 查询一下评论id是否有对应的评论
    b = await Blog.find(id)
    # 没有的话抛出错误
    if b is None:
        raise APIResourceNotFoundError('Comment')
    # 有的话删除
    await b.remove()
    return dict(id=id)


@post('/api/blogs/modify')
async def api_modify_blog(request, *, id, name, summary, content):
    # 修改一条博客
    logging.info("修改的博客的博客ID为：%s", id)
    # name，summary,content 不能为空
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty')

    # 获取指定id的blog数据
    blog = await Blog.find(id)
    blog.name = name
    blog.summary = summary
    blog.content = content

    # 保存
    await blog.update()
    return blog


@get('/manage/blogs/modify/{id}')
def manage_modify_blog(id):
    # 修改博客的页面
    return {
        '__template__': 'manage_blog_modify.html',
        'id': id,
        'action': '/api/blogs/modify'
    }
