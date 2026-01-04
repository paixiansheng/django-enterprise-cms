# apps/rbac/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .models import Role, Permission
from apps.users.models import User
from django.shortcuts import get_object_or_404, render, redirect

# 超级管理员校验Mixin（复用）
class SuperAdminRequiredMixin(UserPassesTestMixin):
    """自定义Mixin：仅允许超级管理员访问"""
    def test_func(self):
        # 校验用户是否登录且为超级管理员
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def handle_no_permission(self):
        # 无权限时返回提示并重定向到个人中心
        messages.error(self.request, "仅超级管理员可访问该功能！")
        return reverse_lazy('users:profile')

# 15.1.1 角色列表视图（查）
class RoleListView(LoginRequiredMixin, SuperAdminRequiredMixin, ListView):
    model = Role
    template_name = 'rbac/role_list.html'  # 对应模板文件
    context_object_name = 'role_list'  # 模板中使用的变量名
    paginate_by = 10  # 分页功能，每页显示10条

# 15.1.2 角色新增视图（增）
class RoleCreateView(LoginRequiredMixin, SuperAdminRequiredMixin, CreateView):
    model = Role
    template_name = 'rbac/role_form.html'
    fields = ['role_name', 'description']  # 表单需要填写的字段
    success_url = reverse_lazy('rbac:role_list')

    def form_valid(self, form):
        messages.success(self.request, f"角色「{form.cleaned_data['role_name']}」创建成功！")
        return super().form_valid(form)

# 15.1.3 角色编辑视图（改）
class RoleUpdateView(LoginRequiredMixin, SuperAdminRequiredMixin, UpdateView):
    model = Role
    template_name = 'rbac/role_form.html'
    fields = ['role_name', 'description']
    success_url = reverse_lazy('rbac:role_list')

    def form_valid(self, form):
        messages.success(self.request, f"角色「{form.cleaned_data['role_name']}」修改成功！")
        return super().form_valid(form)

# 15.1.4 角色删除视图（删）
class RoleDeleteView(LoginRequiredMixin, SuperAdminRequiredMixin, DeleteView):
    model = Role
    template_name = 'rbac/role_confirm_delete.html'
    success_url = reverse_lazy('rbac:role_list')

    def delete(self, request, *args, **kwargs):
        role = self.get_object()
        messages.success(self.request, f"角色「{role.role_name}」删除成功！")
        return super().delete(request, *args, **kwargs)

# 15.2.1 权限列表视图（查）
class PermissionListView(LoginRequiredMixin, SuperAdminRequiredMixin, ListView):
    model = Permission
    template_name = 'rbac/permission_list.html'
    context_object_name = 'permission_list'
    paginate_by = 10

# 15.2.2 权限新增视图（增）
class PermissionCreateView(LoginRequiredMixin, SuperAdminRequiredMixin, CreateView):
    model = Permission
    template_name = 'rbac/permission_form.html'
    fields = ['permission_name', 'permission_code', 'url_path', 'description']
    success_url = reverse_lazy('rbac:permission_list')

    def form_valid(self, form):
        messages.success(self.request, f"权限「{form.cleaned_data['permission_name']}」创建成功！")
        return super().form_valid(form)

# 15.2.3 权限编辑视图（改）
class PermissionUpdateView(LoginRequiredMixin, SuperAdminRequiredMixin, UpdateView):
    model = Permission
    template_name = 'rbac/permission_form.html'
    fields = ['permission_name', 'permission_code', 'url_path', 'description']
    success_url = reverse_lazy('rbac:permission_list')

    def form_valid(self, form):
        messages.success(self.request, f"权限「{form.cleaned_data['permission_name']}」修改成功！")
        return super().form_valid(form)

# 15.2.4 权限删除视图（删）
class PermissionDeleteView(LoginRequiredMixin, SuperAdminRequiredMixin, DeleteView):
    model = Permission
    template_name = 'rbac/permission_confirm_delete.html'
    success_url = reverse_lazy('rbac:permission_list')

    def delete(self, request, *args, **kwargs):
        permission = self.get_object()
        messages.success(self.request, f"权限「{permission.permission_name}」删除成功！")
        return super().delete(request, *args, **kwargs)
    
# 15.3 用户-角色分配视图
class UserRoleAssignView(LoginRequiredMixin, SuperAdminRequiredMixin):
    """用户-角色分配视图：展示用户已有角色，支持分配/移除角色"""
    template_name = 'rbac/user_role_assign.html'

    def get(self, request, user_id):
        # 获取目标用户和所有角色
        user = get_object_or_404(User, id=user_id)
        all_roles = Role.objects.all()
        # 获取用户已绑定的角色ID列表
        user_role_ids = user.roles.values_list('id', flat=True)

        context = {
            'user_obj': user,
            'all_roles': all_roles,
            'user_role_ids': user_role_ids,
        }
        return render(request, self.template_name, context)

    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        # 获取提交的角色ID列表（多选框提交的数组）
        selected_role_ids = request.POST.getlist('role_ids', [])

        # 更新用户角色：先清空原有角色，再添加选中的角色（简化分配逻辑）
        user.roles.clear()
        for role_id in selected_role_ids:
            role = get_object_or_404(Role, id=role_id)
            user.roles.add(role)

        messages.success(request, f"用户「{user.username}」的角色分配成功！")
        return redirect('users:user_list')  # 重定向到用户列表页

# 15.4 角色-权限分配视图
class RolePermissionAssignView(LoginRequiredMixin, SuperAdminRequiredMixin):
    """角色-权限分配视图：展示角色已有权限，支持分配/移除权限"""
    template_name = 'rbac/role_permission_assign.html'

    def get(self, request, role_id):
        # 获取目标角色和所有权限
        role = get_object_or_404(Role, id=role_id)
        all_permissions = Permission.objects.all()
        # 获取角色已绑定的权限ID列表
        role_perm_ids = role.permissions.values_list('id', flat=True)

        context = {
            'role_obj': role,
            'all_permissions': all_permissions,
            'role_perm_ids': role_perm_ids,
        }
        return render(request, self.template_name, context)

    def post(self, request, role_id):
        role = get_object_or_404(Role, id=role_id)
        # 获取提交的权限ID列表
        selected_perm_ids = request.POST.getlist('perm_ids', [])

        # 更新角色权限：先清空再添加
        role.permissions.clear()
        for perm_id in selected_perm_ids:
            perm = get_object_or_404(Permission, id=perm_id)
            role.permissions.add(perm)

        messages.success(request, f"角色「{role.role_name}」的权限分配成功！")
        return redirect('rbac:role_list')  # 重定向到角色列表页