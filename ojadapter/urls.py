import re
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import path, include, re_path
from django.contrib import admin

from ojadapter.entity.UserContext import UserContext


def navigate_to(request, oj_code):
    from ojadapter.adapter import ALL_ADAPTERS
    adapter = ALL_ADAPTERS.get(oj_code)
    if not adapter:
        return HttpResponseNotFound()
    resp = redirect('/')
    # 注册切换的时候就要设置好 cookie 并且重置 cookie jar
    context = UserContext()
    context.save()
    resp.set_cookie('context', context.context_id)
    resp.set_cookie('site', adapter.homepage)
    return resp


# def _proxy_request(method, url):
#
#
def _wrap_response(resp):
    response = HttpResponse()
    if resp.headers['Content-Type'].startswith('text/html'):
        content = resp.content.decode()
        content = content.replace('</body>', '''
        <style type="text/css" rel="stylesheet">
        </style>
        <script>
        console.warn('INJECTED: https://actips.org');
        function cleanTag(tagName, attrName) {
            var els = document.getElementsByTagName(tagName);
            for (var i = 0; i < els.length; ++i) {
                var el = els[i];
                console.log('ELS', el, el.src, attrName, el[attrName]);
                //if (el.src.substr(0, 7) === '/proxy/') continue;
                if (!el[attrName]) continue;
                var path = encodeURIComponent(el[attrName]);
                console.log(path);
                // debugger;
                var _el = el.cloneNode(true);
                _el[attrName] = '/proxy/resource?path=' + path;
                # document.body.appendChild(_el);
            }
        }
        setTimeout(function() {
            cleanTag('script', 'src');
            cleanTag('link', 'href');
        }, 2000);
        </script>
        </body>''')
        response.content = content.encode()
    else:
        response.content = resp.content
    response.status_code = resp.status_code
    # 响应头的处理
    headers = dict(resp.headers)
    for key_to_delete in ['Connection', 'Content-Length', 'Content-Encoding', 'Transfer-Encoding']:
        if key_to_delete in headers:
            del headers[key_to_delete]
    print('>>> resp headers')
    for k, v in sorted(headers.items()):
        print('   ', k, v)
        response[k] = v
    print('<<< headers')
    return response


def proxy_resource(request):
    return _wrap_response(requests.get(request.GET.get('path')))


def proxy_view(request):
    # TODO: 要在当前 session 中保存 cookie jar，每次请求都要载入这个进行代理访问
    site = request.COOKIES.get('site')
    context_id = request.COOKIES.get('context')
    if not site or not context_id:
        return HttpResponseNotFound()
    context = UserContext(context_id)
    print('>>> context headers')
    for k, v in sorted(context.session.headers.items()):
        print('   ', k, v)
    print('<<< headers')
    print('>>> context cookies')
    for k, v in sorted(context.session.cookies.items()):
        print('   ', k, v)
    print('<<< cookies')
    target = urljoin(site, request.get_full_path())
    # print(target)
    # >>>>
    # for k, v in sorted(request.__dict__.items()):
    #     print(k, v)
    headers = dict(request.headers)
    # headers['Host'] = re.match(r'^https?://([^/]+)', site).groups()[0]
    for key_to_delete in ['X-Forwarded-For', 'X-Real-Ip',
                          'Accept', 'Accept-Encoding', 'Accept-Language',
                          'Connection', 'Content-Length', 'Host', 'Cookie'
                          ]:
        if key_to_delete in headers:
            del headers[key_to_delete]
    print('>>> request headers')
    for k, v in sorted(headers.items()):
        print('   ', k, v)
    print('<<< headers')
    # <<<<
    resp = context.session.request(
        method=request.method,
        url=target,
        data=request.body,
        headers=headers,
        cookies=context.session.cookies,
    )
    # print(resp.status_code)
    # print(resp.content.decode())
    context.save()
    return _wrap_response(resp)


urlpatterns = [
    path('navigate/to/<oj_code>', navigate_to),
    path('proxy/resource', proxy_resource),
    re_path(r'^.*$', proxy_view),
]
