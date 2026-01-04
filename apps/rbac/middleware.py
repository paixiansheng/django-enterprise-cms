# apps/rbac/middleware.py
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

class RbacPagePermissionMiddleware:
    """
    RBAC页面级权限中间件：
    1.  排除无需权限校验的路由（如登录、注册、静态资源等）
    2.  校验登录状态：未登录用户重定向到登录页
    3.  校验权限：已登录用户通过「用户→角色→权限」判断是否有权访问当前URL
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # 无需权限校验的白名单路由（可在settings.py中全局配置，此处先内置）
        self.white_list = set([
            reverse('users:login'),
            reverse('users:register'),
            '/admin/',
            '/captcha/',
            '/static/',
            '/media/'
        ])

    def __call__(self, request):
        # 1. 获取当前请求的URL路径
        current_path = request.path_info
        # 2. 排除白名单路由，直接放行
        for white_path in self.white_list:
            if current_path.startswith(white_path):
                response = self.get_response(request)
                return response

        # 3. 校验用户登录状态：未登录则重定向到登录页
        if not request.user.is_authenticated:
            return HttpResponseRedirect(f"{reverse('users:login')}?next={current_path}")

        # 4. 校验用户权限：超级管理员（is_superuser）直接放行
        if request.user.is_superuser:
            response = self.get_response(request)
            return response

        # 5. 非超级管理员：获取用户所有角色对应的权限，匹配当前URL
        has_permission = False
        try:
            # 5.1 通过「用户→角色→权限」反向查询，获取用户所有权限
            user_roles = request.user.roles.all()  # 用户关联的所有角色
            # 5.2 提取所有权限的关联路由（去重）
            permission_urls = set()
            for role in user_roles:
                role_permissions = role.permissions.all()  # 角色关联的所有权限
                for perm in role_permissions:
                    if perm.url_path:  # 仅当权限配置了关联路由时才参与匹配
                        permission_urls.add(perm.url_path)

            # 5.3 匹配当前URL是否在权限路由列表中（支持前缀匹配）
            for perm_url in permission_urls:
                if current_path.startswith(perm_url):
                    has_permission = True
                    break
        except Exception as e:
            # 异常情况下，默认无权限
            has_permission = False

        # 6. 权限判断：有权限放行，无权限返回403禁止访问
        if has_permission:
            response = self.get_response(request)
            return response
        else:
            return HttpResponseForbidden("您没有访问该页面的权限，请联系管理员！")