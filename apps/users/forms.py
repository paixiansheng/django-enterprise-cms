from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from captcha.fields import CaptchaField

# 获取自定义User模型（推荐使用get_user_model()，而非直接导入User）
User = get_user_model()

# 7.1 用户注册表单
class UserRegisterForm(forms.Form):
    # 1. 用户名：必填，3-16位，仅允许字母、数字、下划线
    username = forms.CharField(
        label='用户名',
        min_length=3,
        max_length=16,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='用户名仅允许字母、数字和下划线',
                code='invalid_username'
            )
        ],
        error_messages={
            'min_length': '用户名长度不能少于3位',
            'max_length': '用户名长度不能超过16位',
            'required': '用户名不能为空'
        }
    )
    # 2. 手机号：必填，11位纯数字
    phone = forms.CharField(
        label='手机号',
        max_length=11,
        min_length=11,
        validators=[
            RegexValidator(
                regex=r'^1[3-9]\d{9}$',
                message='请输入有效的11位手机号',
                code='invalid_phone'
            )
        ],
        error_messages={
            'required': '手机号不能为空',
            'min_length': '手机号必须为11位',
            'max_length': '手机号必须为11位'
        }
    )
    # 3. 邮箱：可选，若填写则校验格式合法性
    email = forms.EmailField(
        label='邮箱',
        required=False,
        error_messages={
            'invalid': '请输入有效的邮箱格式'
        }
    )
    # 4. 密码：必填，6-20位，支持字母、数字、特殊字符
    password = forms.CharField(
        label='密码',
        min_length=6,
        max_length=20,
        widget=forms.PasswordInput(),  # 渲染为密码输入框（隐藏输入内容）
        error_messages={
            'required': '密码不能为空',
            'min_length': '密码长度不能少于6位',
            'max_length': '密码长度不能超过20位'
        }
    )
    # 5. 确认密码：必填，与密码保持一致
    password2 = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(),
        error_messages={
            'required': '请再次输入密码'
        }
    )
    # 6. 图形验证码：必填，校验验证码有效性（依赖django-simple-captcha）
    captcha = CaptchaField(
        label='图形验证码',
        error_messages={
            'required': '请输入图形验证码',
            'invalid': '图形验证码错误，请重新输入'
        }
    )

    # 自定义校验：验证用户名是否已存在
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('该用户名已被注册，请更换用户名')
        return username

    # 自定义校验：验证手机号是否已存在
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('该手机号已被注册，请更换手机号')
        return phone

    # 自定义校验：验证两次密码是否一致
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise forms.ValidationError('两次输入的密码不一致，请重新输入')
        return cleaned_data

# 7.2 用户登录表单
class UserLoginForm(forms.Form):
    # 登录账号：支持手机号/邮箱，必填
    account = forms.CharField(
        label='登录账号',
        error_messages={
            'required': '请输入手机号或邮箱'
        }
    )
    # 密码：必填，6-20位
    password = forms.CharField(
        label='密码',
        min_length=6,
        max_length=20,
        widget=forms.PasswordInput(),
        error_messages={
            'required': '请输入密码',
            'min_length': '密码长度不能少于6位',
            'max_length': '密码长度不能超过20位'
        }
    )
    # 图形验证码：必填
    captcha = CaptchaField(
        label='图形验证码',
        error_messages={
            'required': '请输入图形验证码',
            'invalid': '图形验证码错误，请重新输入'
        }
    )

    # 自定义校验：验证账号（手机号/邮箱）是否存在，并返回用户对象
    def clean_account(self):
        account = self.cleaned_data.get('account')
        # 判断是手机号还是邮箱
        is_phone = RegexValidator(r'^1[3-9]\d{9}$').__call__(account) is None
        is_email = forms.EmailField().clean(account) is not None

        try:
            if is_phone:
                # 手机号登录：查询用户
                user = User.objects.get(phone=account)
            elif is_email:
                # 邮箱登录：查询用户
                user = User.objects.get(email=account)
            else:
                raise forms.ValidationError('请输入有效的手机号或邮箱')
        except User.DoesNotExist:
            raise forms.ValidationError('该账号不存在，请先注册')
        return user

    # 自定义校验：验证密码是否正确
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('account')  # 从clean_account获取用户对象
        password = cleaned_data.get('password')

        if user and password:
            # 校验密码（Django内置密码校验方法，自动匹配加密后的密码）
            if not user.check_password(password):
                raise forms.ValidationError('密码错误，请重新输入')
        return cleaned_data

# 7.3 个人资料修改表单（关联User模型，使用ModelForm简化开发）
class UserProfileUpdateForm(forms.ModelForm):
    # 性别字段（手动添加，提供下拉选项，更友好）
    gender = forms.ChoiceField(
        label='性别',
        choices=(('male', '男'), ('female', '女'), ('other', '其他')),
        required=False,
        widget=forms.Select()  # 渲染为下拉选择框
    )

    class Meta:
        model = User  # 关联自定义User模型
        fields = ['username', 'email', 'phone', 'birthday', 'avatar', 'gender']  # 需要修改的字段
        exclude = ['password', 'is_superuser', 'is_staff']  # 排除不可修改的字段
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),  # 渲染为日期选择框
            'email': forms.EmailInput(attrs={'readonly': False}),  # 邮箱可修改
            'phone': forms.TextInput(attrs={'readonly': True}),  # 手机号不可修改（可根据业务调整）
        }
        error_messages = {
            'username': {
                'min_length': '用户名长度不能少于3位',
                'max_length': '用户名长度不能超过16位',
                'invalid': '用户名仅允许字母、数字和下划线'
            },
            'email': {
                'invalid': '请输入有效的邮箱格式'
            }
        }

    # 自定义校验：用户名唯一性（排除当前用户自身）
    def clean_username(self):
        username = self.cleaned_data.get('username')
        current_user = self.instance  # 获取当前登录用户对象（ModelForm自带）
        # 排除当前用户，查询是否有其他用户使用该用户名
        if User.objects.filter(username=username).exclude(id=current_user.id).exists():
            raise forms.ValidationError('该用户名已被占用，请更换用户名')
        return username

# 7.4 密码重置表单（用户已登录，修改自身密码）
class UserPasswordResetForm(forms.Form):
    # 1. 原密码：必填，校验正确性
    old_password = forms.CharField(
        label='原密码',
        widget=forms.PasswordInput(),
        error_messages={
            'required': '请输入原密码'
        }
    )
    # 2. 新密码：必填，6-20位
    new_password = forms.CharField(
        label='新密码',
        min_length=6,
        max_length=20,
        widget=forms.PasswordInput(),
        error_messages={
            'required': '请输入新密码',
            'min_length': '新密码长度不能少于6位',
            'max_length': '新密码长度不能超过20位'
        }
    )
    # 3. 确认新密码：必填，与新密码一致
    new_password2 = forms.CharField(
        label='确认新密码',
        widget=forms.PasswordInput(),
        error_messages={
            'required': '请再次输入新密码'
        }
    )

    # 初始化方法：接收当前用户对象
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # 弹出用户对象，避免传递给父类
        super().__init__(*args, **kwargs)

    # 自定义校验：验证原密码是否正确
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        # 校验原密码（使用用户对象的check_password方法）
        if not self.user.check_password(old_password):
            raise forms.ValidationError('原密码错误，请重新输入')
        return old_password

    # 自定义校验：验证两次新密码是否一致
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password2 = cleaned_data.get('new_password2')

        if new_password and new_password2 and new_password != new_password2:
            raise forms.ValidationError('两次输入的新密码不一致，请重新输入')
        
        # 额外校验：新密码不能与原密码一致（可选，提升安全性）
        old_password = cleaned_data.get('old_password')
        if new_password and old_password and new_password == old_password:
            raise forms.ValidationError('新密码不能与原密码一致，请更换新密码')
        return cleaned_data