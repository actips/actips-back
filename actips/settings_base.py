from django_base.base_settings import *

# Application definition

INSTALLED_APPS += [
    'core',
    'api_admin',
    'api_client',
    'ojadapter',
    'ojtasks',
    'django_base.base_media',
]

MIDDLEWARE += [
]

MIDDLEWARE.remove('django.middleware.csrf.CsrfViewMiddleware')
#
# CSRF_COOKIE_SECURE = False
# print(MIDDLEWARE)

WSGI_APPLICATION = 'actips.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
]

# ============== URLS ================

ROOT_URLCONF = 'core.urls'

# ============== REST FRAMEWORK ================

REST_FRAMEWORK['EXCEPTION_HANDLER'] = 'core.exceptions.exception_handler'

# =========== CRON =======================

CRON_CLASSES = [
]

# =============== SMS Config ===================

SMS_DEBUG = True  # 不真正发送短信，将验证码直接返回

# =============== WeChat API Root =================

WECHAT_API_ROOT = 'http://wx.easecloud.cn'

# ================== CELERY ======================

CELERY_TASK_SERIALIZER = 'msgpack'  # 任务序列化和反序列化使用 msgpack 方案
CELERY_RESULT_SERIALIZER = 'json'  # 读取任务结果一般性能要求不高，所以使用了可读性更好的JSON
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24  # 任务过期时间
CELERY_ACCEPT_CONTENT = ['json', 'msgpack']  # 指定接受的内容类型
