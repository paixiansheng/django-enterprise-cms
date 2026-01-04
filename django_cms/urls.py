"""
URL configuration for django_cms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
# 导入include模块（用于分发应用路由）
from django.urls import path, include
# 导入静态资源和媒体文件配置（可选，确保头像、静态资源可访问）
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django后台管理路由
    path('admin/', admin.site.urls),
    # 验证码路由（django-simple-captcha）
    path('captcha/', include('captcha.urls')),
    # 9.3 分发users应用路由：所有以 /users/ 开头的URL，转发到users应用的urls.py
    path('users/', include('users.urls')),
    path('rbac/', include('rbac.urls')),  # 新增：分发RBAC应用路由
]

# 开发环境下：配置媒体文件访问路由（使浏览器能访问上传的头像等文件）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
