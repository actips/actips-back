from django.http import Http404
from rest_framework import exceptions
from rest_framework.exceptions import PermissionDenied, ErrorDetail
from rest_framework.response import Response
from rest_framework.views import set_rollback

from django_base.base_utils.app_error.exceptions import AppError


class AppErrors:
    ERROR_WECHAT_TICKET_INVALID = AppError(20001, '微信登录凭据失效')
    ERROR_USER_INACTIVE = AppError(20002, '账户已被冻结')
    ERROR_NOT_SIGN_IN = AppError(20003, '用户尚未登录')
    ERROR_MEMBER_INEXISTS = AppError(20004, '用户不存在')


def exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc.detail, ErrorDetail):
            if exc.detail.code == 'not_authenticated':
                exc.status_code = 401
                data = dict(
                    ok=False,
                    msg=str(exc.detail),
                    errcode=10006
                )
            else:
                data = dict(
                    ok=False,
                    msg=exc.detail
                )
        elif isinstance(exc.detail, (list, dict)):
            data = dict(
                ok=False,
                msg=str(exc.detail),
                data=exc.detail
            )
        else:
            data = dict(
                ok=False,
                msg=exc.detail
            )

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    return None
