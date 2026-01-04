# apps/rbac/permissions.py
from rest_framework import permissions
from apps.rbac.models import Permission

class RbacApiPermission(permissions.BasePermission):
    """
    RBAC接口级权限类（基于DRF）：
    1.  校验用户登录状态
    2.  超级管理员豁免权限校验
    3.  非超级管理员校验「用户→角色→权限」是否匹配接口所需权限
    """
    # 接口所需权限标识（可在视图中动态指定，此处为默认值）
    required_permission_code = None

    def has_permission(self, request, view):
        """
        校验接口访问权限（视图级别权限）
        :param request: DRF的Request对象
        :param view: DRF的视图对象
        :return: True（有权限）/ False（无权限）
        """
        # 1. 校验用户登录状态
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. 超级管理员直接放行
        if request.user.is_superuser:
            return True

        # 3. 获取视图中指定的权限标识（优先使用视图的配置）
        required_perm_code = getattr(view, 'required_permission_code', self.required_permission_code)
        if not required_perm_code:
            # 若未指定权限标识，默认放行（可根据业务需求改为禁止）
            return True

        # 4. 非超级管理员：校验「用户→角色→权限」是否包含指定权限标识
        try:
            # 4.1 获取用户所有角色
            user_roles = request.user.roles.all()
            if not user_roles:
                return False

            # 4.2 获取指定权限标识的权限对象
            perm = Permission.objects.get(permission_code=required_perm_code)

            # 4.3 校验用户角色是否绑定该权限
            for role in user_roles:
                if perm in role.permissions.all():
                    return True
            return False
        except Permission.DoesNotExist:
            return False
        except Exception as e:
            return False

    def has_object_permission(self, request, view, obj):
        """
        校验对象级权限（如：修改指定用户时，校验是否有权限）
        可根据业务需求扩展，此处默认返回视图级权限结果
        """
        return self.has_permission(request, view)