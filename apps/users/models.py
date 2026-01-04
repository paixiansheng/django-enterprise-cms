from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# 自定义User模型，继承AbstractUser（保留内置认证功能，扩展字段）
class User(AbstractUser):
    # 扩展字段1：手机号（唯一，用于登录/验证，最大长度11位，不能为空）
    phone = models.CharField(
        verbose_name='手机号',
        max_length=11,
        unique=True,
        blank=False,
        null=False
    )
    # 扩展字段2：头像（上传到media/avatar/目录，按日期分类，可为空）
    avatar = models.ImageField(
        verbose_name='用户头像',
        upload_to='avatar/%Y/%m/%d/',  # 上传路径：media/avatar/年/月/日/
        blank=True,
        null=True
    )
    # 扩展字段3：生日（日期类型，可为空）
    birthday = models.DateField(
        verbose_name='生日',
        blank=True,
        null=True
    )
    # 扩展字段4：创建时间（自动填充当前时间，无需手动赋值）
    create_time = models.DateTimeField(
        verbose_name='创建时间',
        default=timezone.now
    )
    roles = models.ManyToManyField(
        to='rbac.Role',  # 关联rbac应用的Role模型
        verbose_name='用户角色',
        blank=True,
        related_name='user_roles',  # 反向关联名称，便于通过角色查询关联的用户
        help_text='请为该用户分配对应的角色，可多选'
    )    

    # 重新指定用户名字段（可选，默认是username，此处明确指定，便于后续维护）
    USERNAME_FIELD = 'username'
    # 注册时必填字段（除了username和password，额外需要填写的字段）
    REQUIRED_FIELDS = ['email', 'phone']

    class Meta:
        # 6.3 配置模型元信息（提前嵌入，提升后台可读性）
        verbose_name = '用户'  # 单数显示名称（后台管理中显示）
        verbose_name_plural = '用户管理'  # 复数显示名称（后台管理中显示，避免默认加s）
        ordering = ['-create_time']  # 排序规则：按创建时间倒序（最新创建的在前面）

    def __str__(self):
        # 后台显示用户名，便于识别
        return self.username

# 登录日志模型（关联User模型，多对一关系：一个用户对应多条登录日志）
class LoginLog(models.Model):
    # 关联用户（外键，关联自定义User模型，用户删除时日志也同步删除）
    user = models.ForeignKey(
        verbose_name='关联用户',
        to='User',  # 关联当前应用的User模型
        on_delete=models.CASCADE,  # 级联删除：用户删除，日志也删除
        related_name='login_logs'  # 反向关联：用户对象可通过user.login_logs获取所有登录日志
    )
    # 登录IP地址（最大长度32位，记录用户登录IP）
    login_ip = models.CharField(
        verbose_name='登录IP',
        max_length=32,
        blank=False,
        null=False
    )
    # 登录时间（自动填充当前时间）
    login_time = models.DateTimeField(
        verbose_name='登录时间',
        default=timezone.now
    )
    # 登录设备（记录设备类型，如PC、Android、iOS等）
    device = models.CharField(
        verbose_name='登录设备',
        max_length=32,
        blank=True,
        null=True
    )
    # 登录状态（布尔类型，True=登录成功，False=登录失败，默认True）
    status = models.BooleanField(
        verbose_name='登录状态',
        default=True,
        help_text='True=登录成功，False=登录失败'
    )

    # 6.3 配置模型元信息
    class Meta:
        verbose_name = '登录日志'
        verbose_name_plural = '登录日志管理'
        ordering = ['-login_time']  # 按登录时间倒序排序

    def __str__(self):
        # 后台显示：用户名 + 登录IP + 登录状态
        status_text = '成功' if self.status else '失败'
        return f'{self.user.username} - {self.login_ip} - {status_text}'
