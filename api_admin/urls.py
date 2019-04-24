import re

from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from . import views as v

app_name = 'api_admin'

# 注册所有 DRF 路由

router = DefaultRouter()

routers = []

# 类__dict__：获取类的静态函数，类函数，普通函数，全局变量等一些内置的属性
# items()：返回可遍历的(键，值)元组数组
for key, item in v.__dict__.items():
    # 找到数组里的key是以ViewSet结尾
    if key.endswith('ViewSet'):
        # 将ViewSet替换成''
        name = key.replace('ViewSet', '')
        # 首字符替换成小写
        name = re.sub(r'([A-Z])', '_\\1', name)[1:].lower()

        if name:
            # 如果name设置成功，则添加到routers数组中
            routers.append((name, item))

for name, item in sorted(routers):
    # print(name, item)
    # 进行视图集路由注册 register(prefix(视图集的路由前缀),viewset(视图集),base_name(路由名称的前缀))
    router.register(name, item)

# [print(u) for u in router.urls]

# 添加路由数据
urlpatterns = [
    # url(r'^api-auth/', include(rest_framework.urls, namespace='rest_framework')),
    url(r'^', include(router.urls)),
]
