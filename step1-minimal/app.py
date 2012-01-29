# coding: utf-8
#
# step 1:
#
# [简体中文]
# 这个实例使用kaixin.py事件机制创建一个WSGI应用，并启动一个WSGI服务器接受客户端请求。
# WSGI是Web Server Gateway Interface的缩写，关于WSGI的详细信息请访问wsgi.org。
# [English]
# This example start a WSGI service to accept client request, using event-based plugins.
# WSIG stands for Web Server Gateway Interface, visit wsgi.org to get more information.

from wsgiref.simple_server import make_server

from kaixin.core import wsgi
from kaixin.core.http import STATUS
from kaixin.core.events import register_listener
from kaixin.core.events import fire_event

# 创建一个WSGI应用实例
# Create a WSGI application instance
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
    
    # 激活dispatch事件，sayhi会被调用
    # Fire dispatch event, sayhi gets called
    fire_event('dispatch', context=context) 
    
    # WSGI调用
    # WSGI call
    start_response(response.get_response_status(), response.get_response_headers()) 
    
    # 返回输出内容
    # Return output
    return response.get_response_body() 

# 通过register_listener decorator注册dispatch事件函数
# Register dispatch event handler by using register_listener decorator
@register_listener('dispatch')
def sayhi(context):
    response = context.response
    
    # 添加输出内容 
    # Add output
    response.append_response_body('hello world!') 
    
    # 设置HTTP STATUS CODE
    # Set HTTP STATUS CODE
    response.set_response_status(STATUS._200) 
    
    # 返回False表示事件可以继续传播下去
    # Return False to propagate the event
    return False 
    
if __name__ == '__main__':
    # 创建一个WSGI服务器，并在127.0.0.1监听9000端口
    # Create a WSGI service, listening on 127.0.0.1:9000
    httpd = make_server('127.0.0.1', 9000, app) 
    
    # 开始处理请求
    # Start to handle requests
    httpd.serve_forever() 
