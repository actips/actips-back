from .settings_base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '<<enter-your-secret-key-here>>'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES['default']['NAME'] = 'django_actips'
DATABASES['default']['USER'] = 'root'
DATABASES['default']['PASSWORD'] = 'root'
DATABASES['default']['HOST'] = '127.0.0.1'
DATABASES['default']['PORT'] = 3306

# =============== SMS Config ===================

SMS_ACCESS_KEY_ID = '*****'
SMS_ACCESS_KEY_SECRET = '*****'

SMS_SEND_INTERVAL = 60  # 短信发送时间间隔限制
SMS_EXPIRE_INTERVAL = 1800
SMS_SIGN_NAME = 'ACTIPS'
SMS_TEMPLATES = dict(
    SIGN_IN='SMS_#########',
    CHANGE_PASSWORD='SMS_#########',
    CHANGE_MOBILE_VERIFY='SMS_#########',
    CHANGE_MOBILE_UPDATE='SMS_#########',
)
SMS_DEBUG = True  # 不真正发送短信，将验证码直接返回

# ================== Business ============================

WECHAT_API_ROOT = 'https://wx.easecloud.cn/'
WECHAT_APPID = 'wx765be0001df065a6'
