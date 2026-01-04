# apps/rbac/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

# 13.1 角色模型（Role）
class Role(models.Model):
    """
    RBAC角色模型：存储角色名称、描述等信息
    一个角色可对应多个用户，一个角色可对应多个权限
    """
    role_name = models.CharField(
        verbose_name='角色名称',
        max_length=32,
        unique=True,  # 角色名称唯一，不允许重复
        help_text='请输入唯一的角色名称，如：超级管理员、普通管理员'
    )
    description = models.TextField(
        verbose_name='角色描述',
        blank=True,
        null=True,
        help_text='请输入角色的功能描述，可选填'
    )
    create_time = models.DateTimeField(
        verbose_name='创建时间',
        default=timezone.now,  # 默认值为当前时间
        editable=False  # 不可手动编辑，自动生成
    )
    update_time = models.DateTimeField(
        verbose_name='更新时间',
        auto_now=True  # 每次保存模型时，自动更新为当前时间
    )
    permissions = models.ManyToManyField(
        to='Permission',  # 关联当前应用的Permission模型
        verbose_name='绑定权限',
        blank=True,  # 允许角色暂时不绑定任何权限
        related_name='role_permissions',  # 反向关联名称，便于通过权限查询关联的角色
        help_text='请为该角色分配对应的权限，可多选'
    )
    class Meta:
        verbose_name = '角色管理'  # Django后台显示的单数名称
        verbose_name_plural = '角色管理'  # Django后台显示的复数名称（统一为单数，更符合中文习惯）
        ordering = ['-create_time']  # 按创建时间倒序排列

    def __str__(self):
        """模型实例打印时，返回角色名称"""
        return self.role_name
    
# 13.2 权限模型（Permission）
class Permission(models.Model):
    """
    RBAC权限模型：存储权限名称、权限标识、关联路由等信息
    一个权限可对应多个角色，一个权限对应一个具体的业务操作/路由
    """
    permission_name = models.CharField(
        verbose_name='权限名称',
        max_length=64,
        unique=True,  # 权限名称唯一
        help_text='请输入唯一的权限名称，如：查看用户列表、修改用户状态'
    )
    permission_code = models.CharField(
        verbose_name='权限标识',
        max_length=64,
        unique=True,  # 权限标识唯一，用于代码中权限判断（如：user_view、user_status_change）
        help_text='请输入英文唯一标识，仅含字母、下划线，如：user_view'
    )
    url_path = models.CharField(
        verbose_name='关联路由',
        max_length=256,
        blank=True,
        null=True,
        help_text='请输入该权限对应的URL路径，如：/users/login/logs/，可选填'
    )
    description = models.TextField(
        verbose_name='权限描述',
        blank=True,
        null=True,
        help_text='请输入权限的详细描述，可选填'
    )
    create_time = models.DateTimeField(
        verbose_name='创建时间',
        default=timezone.now,
        editable=False
    )
    update_time = models.DateTimeField(
        verbose_name='更新时间',
        auto_now=True
    )

    class Meta:
        verbose_name = '权限管理'
        verbose_name_plural = '权限管理'
        ordering = ['-create_time']

    def __str__(self):
        """模型实例打印时，返回权限名称"""
        return self.permission_name
