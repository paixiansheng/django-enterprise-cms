# apps/rbac/templatetags/rbac_tags.py
from django import template
from apps.rbac.models import Permission

# 注册模板标签库
register = template.Library()

@register.simple_tag(takes_context=True)
def has_permission(context, permission_code):
    """
    自定义简单标签：判断当前用户是否拥有指定权限标识的权限
    :param context: 模板上下文（包含request对象）
    :param permission_code: 权限标识（如：user_status_change）
    :return: True（有权限）/ False（无权限）
    """
    # 1. 获取request对象和当前用户
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return False

    # 2. 超级管理员直接返回有权限
    if request.user.is_superuser:
        return True

    # 3. 非超级管理员：通过「用户→角色→权限」校验权限标识
    try:
        # 3.1 获取用户所有角色
        user_roles = request.user.roles.all()
        if not user_roles:
            return False

        # 3.2 校验是否存在指定权限标识的权限
        permission = Permission.objects.get(permission_code=permission_code)
        for role in user_roles:
            if permission in role.permissions.all():
                return True
        return False
    except Permission.DoesNotExist:
        # 权限不存在，返回无权限
        return False
    except Exception as e:
        return False