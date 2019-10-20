from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'proxy', 'ojadapter.urls', name='proxy'),  # 用于反向代理 OJ
    host(r'', 'core.urls', name='default'),  # 默认 host
)
