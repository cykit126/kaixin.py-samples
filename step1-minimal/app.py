# coding: utf-8
# 
# 这个实例使用kaixin.py事件机制创建一个WSGI应用，并启动一个WSGI服务器接受客户端请求。
# WSGI是Web Server Gateway Interface的缩写，关于WSGI的详细信息请访问wsgi.org。
#

from wsgiref.simple_server import make_server

from kaixin.core import wsgi
from kaixin.core.http import STATUS
from kaixin.core.events import register_listener
from kaixin.core.events import fire_event

# 创建一个WSGI应用实例
def app(environ, start_response):
    request = wsgi.Request(environ) # 创建一个Request对象
    response = wsgi.Response() # 创建一个Response对象
    context = wsgi.Context(request, response) # 创建一个Context对象
    fire_event('dispatch', context=context) # 激活dispatch事件，sayhi会被调用
    start_response(response.get_response_status(), response.get_response_headers()) # WSGI调用
    return response.get_response_body() # 返回输出内容

# 通过register_listener decorator注册dispatch事件函数
@register_listener('dispatch')
def sayhi(context):
    response = context.response
    response.append_response_body('hello world!') # 添加输出内容
    response.set_response_status(STATUS._200) # 设置HTTP STATUS CODE
    return False # 让事件可以继续传播下去，返回True
    
if __name__ == '__main__':
    httpd = make_server('127.0.0.1', 9000, app) # 创建一个WSGI服务器，并在127.0.0.1监听9000端口
    httpd.handle_request() # 开始处理请求
