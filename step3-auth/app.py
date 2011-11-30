# coding: utf-8
#
# step 1
# 这个实例使用kaixin.py事件机制创建一个WSGI应用，并启动一个WSGI服务器接受客户端请求。
# WSGI是Web Server Gateway Interface的缩写，关于WSGI的详细信息请访问wsgi.org。
# step 2:
# 添加URL映射，访问 http://127.0.0.1:9000/sayhi/Wilbur输入hello, Wilbur。
# step 3:
# 添加token认证，在URL末尾加一个token=123456的参数以示拥有访问的权限。
# 访问 http://127.0.0.1:9000/saihi/Wilbur返回403禁止访问。
# 访问 http://127.0.0.1:9000/saihi/Wilbur?token=123455则输出hello, Wilbur。
#

from wsgiref.simple_server import make_server
from string import Formatter

from kaixin.core import wsgi
from kaixin.core.http import STATUS
from kaixin.extension.resolver import RegexResolver
from kaixin.core.events import fire_event
from kaixin.core.events import register_listener

# 创建一个WSGI应用实例
def app(environ, start_response):
    request = wsgi.Request(environ) # 创建一个Request对象
    response = wsgi.Response() # 创建一个Response对象
    context = wsgi.Context(request, response) # 创建一个Context对象
    #添加before_dispatch事件，以便进行认证检查。
    if not fire_event('before_dispatch', context=context):
        fire_event('dispatch', context=context) # 激活dispatch事件，sayhi会被调用
    start_response(response.get_response_status(), response.get_response_headers()) # WSGI调用
    return response.get_response_body() # 返回输出内容

# 创建一个全局的resolver，所有的请求都公用这个resovler。
resolver = RegexResolver()

# dispatch事件处理函数
@register_listener('dispatch')
def dispatch(context):
    request = context.request
    handler, params = resolver.dispatch(request.get_request_url()) # 调用resolver解析URL
    if handler is not None: # 找到匹配URL的handler
        handler(context, params)
    else: # 未找到匹配URL的handler，返回404错误
        response = context.response
        response.set_response_status(STATUS._404)
        response.append_response_body('File not foud')
    return False # 让事件可以继续传播下去，返回True则表示中断事件传播


# 注册before_dispatch事件监听函数
@register_listener('before_dispatch')
def before_dispatch(context):
    token = context.request.GET('token')
    if token == '123456':
        return False
    else:
        context.response.set_response_status(STATUS._403)
        context.response.append_response_body('Forbidden')
        return True # 如果token不等于'123456'则返回True，dispatch就不会被触发。

# 创建一个python decorator方便注册handler。
# 关于decorator的教程请参阅Bruce Eckel的两篇教程。
# Decorators I: Introduction to Python Decorators
# http://www.artima.com/weblogs/viewpost.jsp?thread=240808
# Python Decorators II: Decorator Arguments
# http://www.artima.com/weblogs/viewpost.jsp?thread=240845
class register_handler:
    def __init__(self, regex):
        self._regex = regex
    def __call__(self, f):
        resolver.register_handler(self._regex, f) # 注册handler
        return f
    
# 注册handler
@register_handler('/sayhi/(?P<name>\w+)')
def sayhi(context, params):
    response = context.response
    resp_body = Formatter().format("Hello, {0}!", params['name'])
    response.append_response_body(resp_body) # 添加输出内容
    response.set_response_status(STATUS._200) # 设置HTTP STATUS CODE
    
if __name__ == '__main__':
    httpd = make_server('127.0.0.1', 9000, app) # 创建一个WSGI服务器，并在127.0.0.1监听9000端口
    httpd.serve_forever() # 开始处理请求
