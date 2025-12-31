# 导入Django路由核心模块
from django.urls import path
# 导入当前应用的所有视图（已编写的类视图）
from . import views

# 配置应用命名空间（关键：避免不同应用路由名称冲突）
app_name = 'users'

# 路由列表：配置URL路径与视图的映射关系
urlpatterns = [
    # 9.2.1 基础功能路由
    # 注册页：URL路径 /users/register/，映射UserRegisterView，路由名称 register
    path('register/', views.UserRegisterView.as_view(), name='register'),
    # 登录页：URL路径 /users/login/，映射UserLoginView，路由名称 login
    path('login/', views.UserLoginView.as_view(), name='login'),
    # 退出登录：URL路径 /users/logout/，映射UserLogoutView，路由名称 logout
    path('logout/', views.UserLogoutView.as_view(), name='logout'),

    # 9.2.2 个人中心功能路由
    # 个人资料展示：URL路径 /users/profile/，映射UserProfileView，路由名称 profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    # 个人资料修改：URL路径 /users/profile/update/，映射UserProfileUpdateView，路由名称 profile_update
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile_update'),

    # 9.2.3 密码重置功能路由
    # 密码重置：URL路径 /users/password/reset/，映射UserPasswordResetView，路由名称 password_reset
    path('password/reset/', views.UserPasswordResetView.as_view(), name='password_reset'),

    # 9.2.4 管理员功能路由
    # 登录日志查询：URL路径 /users/login/logs/，映射LoginLogQueryView，路由名称 login_log_list
    path('login/logs/', views.LoginLogQueryView.as_view(), name='login_log_list'),
    # 用户状态管理（禁用/启用）：URL路径 /users/status/update/用户ID/，映射UserStatusUpdateView，路由名称 user_status_update
    path('status/update/<int:user_id>/', views.UserStatusUpdateView.as_view(), name='user_status_update'),
]