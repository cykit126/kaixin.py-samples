# coding: utf-8

from wsgiref.simple_server import make_server

from kaixin.core import wsgi
from kaixin.core.http import STATUS

def sayhi(context):
    response = context.response
    response.append_response_body('hello world!')
    response.set_response_status(STATUS._200)

def app(environ, start_response):
    request = wsgi.Request(environ)
    response = wsgi.Response()
    context = wsgi.Context(request, response)
    context.events.add_listener('dispatch', sayhi)
    context.events.fire_event('dispatch', context=context)
    start_response(response.get_response_status(), response.get_response_headers())
    return response.get_response_body()
    
if __name__ == '__main__':
    httpd = make_server('127.0.0.1', 9000, app)
    httpd.handle_request()
