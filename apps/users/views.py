from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import FormView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm
from .models import User, LoginLog
from django.utils import timezone
import socket
from apps.rbac.permissions import RbacApiPermission

# 辅助函数：获取用户登录IP
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip

# 辅助函数：获取用户登录设备（简单判断，可扩展）
def get_client_device(request):
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    if 'Mobile' in user_agent:
        return 'Mobile'
    elif 'iPad' in user_agent:
        return 'Pad'
    elif 'PC' in user_agent or 'Windows' in user_agent:
        return 'PC'
    else:
        return 'Unknown'

# 8.1.1 注册视图（FormView：处理表单提交更简洁）
class UserRegisterView(FormView):
    template_name = 'users/register.html'  # 对应注册模板（后续创建）
    form_class = UserRegisterForm  # 关联注册表单
    success_url = reverse_lazy('users:login')  # 注册成功后跳转登录页

    # 表单验证通过后执行的逻辑
    def form_valid(self, form):
        # 获取表单数据
        username = form.cleaned_data.get('username')
        phone = form.cleaned_data.get('phone')
        email = form.cleaned_data.get('email', '')
        password = form.cleaned_data.get('password')

        # 创建用户（使用create_user方法，自动加密密码）
        User.objects.create_user(
            username=username,
            phone=phone,
            email=email,
            password=password
        )

        # 添加成功提示
        messages.success(self.request, '注册成功，请登录！')
        return super().form_valid(form)

    # 表单验证失败后执行的逻辑
    def form_invalid(self, form):
        # 添加错误提示
        messages.error(self.request, '注册失败，请检查表单信息！')
        return super().form_invalid(form)

# 8.1.2 登录视图（FormView）
class UserLoginView(FormView):
    template_name = 'users/login.html'  # 对应登录模板（后续创建）
    form_class = UserLoginForm  # 关联登录表单
    success_url = reverse_lazy('users:profile')  # 登录成功后跳转个人中心

    # 表单验证通过后执行的逻辑
    def form_valid(self, form):
        # 从表单清洁数据中获取用户对象（clean_account已返回用户）
        user = form.cleaned_data.get('account')
        # 登录用户（Django内置login方法，创建session）
        login(self.request, user)

        # 记录登录日志
        LoginLog.objects.create(
            user=user,
            login_ip=get_client_ip(self.request),
            login_time=timezone.now(),
            device=get_client_device(self.request),
            status=True  # 登录成功
        )

        # 添加成功提示
        messages.success(self.request, f'欢迎回来，{user.username}！')
        return super().form_valid(form)

    # 表单验证失败后执行的逻辑
    def form_invalid(self, form):
        # 记录失败日志（若账号存在）
        account = self.request.POST.get('account')
        try:
            is_phone = self.request.POST.get('account').isdigit() and len(account) == 11
            if is_phone:
                user = User.objects.get(phone=account)
            else:
                user = User.objects.get(email=account)
            # 记录登录失败日志
            LoginLog.objects.create(
                user=user,
                login_ip=get_client_ip(self.request),
                login_time=timezone.now(),
                device=get_client_device(self.request),
                status=False  # 登录失败
            )
        except User.DoesNotExist:
            pass

        # 添加错误提示
        messages.error(self.request, '登录失败，请检查账号、密码或验证码！')
        return super().form_invalid(form)

# 8.1.3 退出登录视图（View）
class UserLogoutView(LoginRequiredMixin, View):
    # LoginRequiredMixin：要求用户必须登录才能访问该视图
    def get(self, request):
        # 退出登录（Django内置logout方法，清除session）
        logout(request)
        # 添加提示信息
        messages.info(request, '已成功退出登录！')
        # 跳转登录页
        return redirect('users:login')

from .forms import UserProfileUpdateForm

# 8.2.1 个人资料展示视图（LoginRequiredMixin + View）
class UserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        # 获取当前登录用户对象
        user = request.user
        # 渲染个人中心模板，传递用户数据
        return render(request, 'users/profile.html', {
            'user': user
        })

# 8.2.2 个人资料修改视图（LoginRequiredMixin + FormView）
class UserProfileUpdateView(LoginRequiredMixin, FormView):
    template_name = 'users/profile_update.html'  # 资料修改模板
    form_class = UserProfileUpdateForm  # 关联资料修改表单
    success_url = reverse_lazy('users:profile')  # 修改成功后跳转个人中心

    # 初始化表单，传入当前用户实例（用于ModelForm的instance参数）
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 传入当前登录用户对象作为表单实例
        kwargs['instance'] = self.request.user
        return kwargs

    # 表单验证通过后执行的逻辑
    def form_valid(self, form):
        # 保存修改后的用户资料（ModelForm自带save方法）
        form.save()
        messages.success(self.request, '个人资料修改成功！')
        return super().form_valid(form)

    # 表单验证失败后执行的逻辑
    def form_invalid(self, form):
        messages.error(self.request, '资料修改失败，请检查表单信息！')
        return super().form_invalid(form)

from .forms import UserPasswordResetForm

# 8.3.1 密码重置页面视图（展示表单，LoginRequiredMixin + View）
class UserPasswordResetView(LoginRequiredMixin, View):
    def get(self, request):
        # 渲染密码重置模板，传递空表单
        form = UserPasswordResetForm(user=request.user)
        return render(request, 'users/password_reset.html', {
            'form': form
        })

    # 处理表单提交（POST请求）
    def post(self, request):
        # 实例化表单，传入用户对象和POST数据
        form = UserPasswordResetForm(request.POST, user=request.user)
        if form.is_valid():
            # 获取新密码
            new_password = form.cleaned_data.get('new_password')
            # 修改用户密码（set_password方法自动加密）
            user = request.user
            user.set_password(new_password)
            user.save()
            # 重置密码后强制退出登录，要求重新登录
            logout(request)
            messages.success(request, '密码重置成功，请使用新密码重新登录！')
            return redirect('users:login')
        else:
            messages.error(request, '密码重置失败，请检查表单信息！')
            return render(request, 'users/password_reset.html', {
                'form': form
            })
        
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q

# 8.4 登录日志查询视图（仅超级管理员/有查看权限的管理员可访问）
class LoginLogQueryView(LoginRequiredMixin, PermissionRequiredMixin, View):
    # 权限要求：必须是超级管理员，或拥有查看登录日志的权限
    permission_required = 'users.view_loginlog'
    # 若权限不足，跳转至登录页（可自定义跳转地址）
    login_url = reverse_lazy('users:login')

    def get(self, request):
        # 获取查询参数
        username = request.GET.get('username', '')
        status = request.GET.get('status', '')
        start_time = request.GET.get('start_time', '')
        end_time = request.GET.get('end_time', '')

        # 初始化查询集
        login_logs = LoginLog.objects.all()

        # 按用户名筛选（模糊查询）
        if username:
            login_logs = login_logs.filter(user__username__icontains=username)

        # 按登录状态筛选
        if status in ['True', 'False']:
            login_logs = login_logs.filter(status=(status == 'True'))

        # 按时间范围筛选
        if start_time:
            login_logs = login_logs.filter(login_time__gte=start_time)
        if end_time:
            login_logs = login_logs.filter(login_time__lte=end_time)

        # 渲染日志查询模板，传递日志数据和查询参数
        return render(request, 'users/login_log_list.html', {
            'login_logs': login_logs,
            'username': username,
            'status': status,
            'start_time': start_time,
            'end_time': end_time
        })

# 8.5 用户状态管理视图（禁用/启用普通用户，仅超级管理员可访问）
class UserStatusUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'users.change_user'  # 拥有修改用户的权限
    login_url = reverse_lazy('users:login')

    def get(self, request, user_id):
        # 获取要修改状态的用户（排除超级管理员自身）
        target_user = get_object_or_404(User, id=user_id)
        current_user = request.user

        # 禁止修改超级管理员状态，禁止自身修改自身状态
        if target_user.is_superuser or target_user.id == current_user.id:
            messages.error(request, '无法修改该用户状态！')
            return redirect('users:user_list')  # 跳转用户列表页（后续创建）

        # 切换用户状态（is_active：True=启用，False=禁用）
        target_user.is_active = not target_user.is_active
        target_user.save()

        # 添加提示信息
        status_text = '启用' if target_user.is_active else '禁用'
        messages.success(request, f'已成功{status_text}用户「{target_user.username}」！')

        # 跳转用户列表页
        return redirect('users:user_list')
    
# 定义用户序列化器
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'email', 'is_active']

# 定义用户接口视图集
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # 指定该接口所需的权限标识（与RBAC权限模型中的permission_code一致）
    required_permission_code = 'user_view'
    # 若未配置DRF全局权限类，可在此处单独指定
    # permission_classes = [RbacApiPermission]