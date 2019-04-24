from django_base.base_settings import *

# Application definition

INSTALLED_APPS += [
    'core',
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

REST_FRAMEWORK['EXCEPTION_HANDLER'] = 'apps.core.exceptions.exception_handler'

# =========== CRON =======================

CRON_CLASSES = [
    'apps.core.cron.SyncErpCronJob'
]

# =============== SMS Config ===================

SMS_DEBUG = True  # 不真正发送短信，将验证码直接返回

# =============== WeChat API Root =================

WECHAT_API_ROOT = 'http://wx.easecloud.cn'
