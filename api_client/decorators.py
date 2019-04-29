from functools import wraps

from core.exceptions import AppErrors


def member_required(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        # 登录校验
        if not hasattr(request.user, 'member'):
            # 尚未登录
            raise AppErrors.ERROR_LOGIN_REQUIRED
        elif not request.user.is_active:
            # 用户已被锁定
            raise AppErrors.ERROR_USER_INACTIVE
        return view_func(self, request, *args, **kwargs)

    return _wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        # 登录校验
        if not request.user.is_active:
            # 用户已被锁定
            raise AppErrors.ERROR_USER_INACTIVE
        elif not request.user.is_superuser:
            # 必须是管理员
            raise AppErrors.ERROR_SUPERUSER_REQUIRED
        return view_func(self, request, *args, **kwargs)

    return _wrapped_view
