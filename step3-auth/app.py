# coding: utf-8
#
# step 1:
# [简体中文]
# 这个实例使用kaixin.py事件机制创建一个WSGI应用，并启动一个WSGI服务器接受客户端请求。
# WSGI是Web Server Gateway Interface的缩写，关于WSGI的详细信息请访问wsgi.org。
# [English]
# This example start a WSGI service to accept client request, using event-based plugins.
# WSIG stands for Web Server Gateway Interface, visit wsgi.org to get more information.
#
# step 2:
# [简体中文]
# 添加URL映射，访问 http://127.0.0.1:9000/sayhi/Wilbur显示hello, Wilbur。
# [English]
# Add URL Mapping, visit http://127.0.0.1:9000/sayhi/Wilbur, print hello, Wilbur.
#
# step 3:
# [简体中文]
# 添加token认证，在URL末尾加一个token=123456的参数以示拥有访问的权限。
# 访问 http://127.0.0.1:9000/saihi/Wilbur返回403禁止访问。
# 访问 http://127.0.0.1:9000/saihi/Wilbur?token=123455则输出hello, Wilbur。
# [English]
# Add token authentication, adding a query string token 'token=123456'.
# Visit http://127.0.0.1:9000/saihi/Wilbur returns 403 forbidden.
# Visit http://127.0.0.1:9000/saihi/Wilbur?token=123455 print hello, Wilbur.

from wsgiref.simple_server import make_server
from string import Formatter

from kaixin.core import wsgi
from kaixin.core.http import STATUS
from kaixin.extension.resolver import RegexResolver
from kaixin.core.events import fire_event
from kaixin.core.events import register_listener

# 创建一个WSGI应用实例
def app(environ, start_response):
    # 创建一个Request对象
    # Create a Request object
    request = wsgi.Request(environ)
    
    # 创建一个Response对象
    # Create a Response object
    response = wsgi.Response()
    
    # 创建一个Context对象
    # Create a Context object
    context = wsgi.Context(request, response) 
    
    # 添加before_dispatch事件，以便进行认证检查。
    # Add event before_dispatch to do authentication.
    if not fire_event('before_dispatch', context=context):
        # 激活dispatch事件，sayhi会被调用
        # Fire event dispatch, sayhi gets called
        fire_event('dispatch', context=context) 
    
    # WSGI调用
    # WSGI call
    start_response(response.get_response_status(), response.get_response_headers()) 
    
    # 返回输出内容
    # Return output
    return response.get_response_body() 

# 创建一个全局的resolver，所有的请求都公用这个resovler。
# Create a global resolver to handle request dispatch.
resolver = RegexResolver()

# dispatch事件处理函数
# dispatch event handler
@register_listener('dispatch')
def dispatch(context):
    request = context.request
    
    # 调用resolver解析URL
    # Call resolver to parse URL
    handler, params = resolver.dispatch(request.get_request_url()) 
    
    # 找到匹配URL的handler
    # URL handler matched
    if handler is not None: 
        handler(context, params)
    # 未找到匹配URL的handler，返回404错误
    # No handler found, return 404 error
    else: 
        response = context.response
        response.set_response_status(STATUS._404)
        response.append_response_body('File not foud')
    
    # 返回False表示事件可以继续传播下去
    # Return False to propagate the event
    return False

# 注册before_dispatch事件监听函数
# Register before_dispatch event handler
@register_listener('before_dispatch')
def before_dispatch(context):
    token = context.request.GET('token')
    if token == '123456':
        return False
    else:
        context.response.set_response_status(STATUS._403)
        context.response.append_response_body('Forbidden')
        # 如果token不等于'123456'则返回True，dispatch就不会被触发。
        # If token is not '123456' return True to stop dispatch event.
        return True 

# 创建一个python decorator方便注册handler。
# Create a python decorator for handler registration.
# 关于decorator的教程请参阅Bruce Eckel的两篇教程。
# The following are two articles on python decorator.
# Decorators I: Introduction to Python Decorators
# http://www.artima.com/weblogs/viewpost.jsp?thread=240808
# Python Decorators II: Decorator Arguments
# http://www.artima.com/weblogs/viewpost.jsp?thread=240845
class register_handler:
    def __init__(self, regex):
        self._regex = regex
    def __call__(self, f):
        # 注册handler
        # Register handler
        resolver.register_handler(self._regex, f) 
        return f
    
# 注册handler
# Register handler
@register_handler('/sayhi/(?P<name>\w+)')
def sayhi(context, params):
    response = context.response
    resp_body = Formatter().format("Hello, {0}!", params['name'])
    
    # 添加输出内容
    # Append output content
    response.append_response_body(resp_body) 
    
    # 设置HTTP STATUS CODE
    # Set HTTP STATUS CODE
    response.set_response_status(STATUS._200) 
    
if __name__ == '__main__':
    # 创建一个WSGI服务器，并在127.0.0.1监听9000端口
    # Create a WSGI service, listening on 127.0.0.1:9000
    httpd = make_server('127.0.0.1', 9000, app) 
    
    # 开始处理请求
    # Start to handle requests
    httpd.serve_forever() 

