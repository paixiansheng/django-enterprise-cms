# apps/rbac/urls.py
from django.urls import path
from . import views

app_name = 'rbac'

urlpatterns = [
    # 15.1 角色管理路由
    path('role/list/', views.RoleListView.as_view(), name='role_list'),
    path('role/create/', views.RoleCreateView.as_view(), name='role_create'),
    path('role/update/<int:pk>/', views.RoleUpdateView.as_view(), name='role_update'),
    path('role/delete/<int:pk>/', views.RoleDeleteView.as_view(), name='role_delete'),
    # 15.2 权限管理路由
    path('permission/list/', views.PermissionListView.as_view(), name='permission_list'),
    path('permission/create/', views.PermissionCreateView.as_view(), name='permission_create'),
    path('permission/update/<int:pk>/', views.PermissionUpdateView.as_view(), name='permission_update'),
    path('permission/delete/<int:pk>/', views.PermissionDeleteView.as_view(), name='permission_delete'),
    # 15.3 用户-角色分配路由
    path('user/role/assign/<int:user_id>/', views.UserRoleAssignView.as_view(), name='user_role_assign'),
    # 15.4 角色-权限分配路由
    path('role/permission/assign/<int:role_id>/', views.RolePermissionAssignView.as_view(), name='role_permission_assign'),
]