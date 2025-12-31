"""
WSGI config for django_cms project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""


import os
from django.core.wsgi import get_wsgi_application

# 方式1：默认读取环境变量（推荐）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_cms.settings')

# 方式2：手动指定生产环境（线上部署时可使用，注释方式1，启用该方式）
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_cms.settings.prod')

application = get_wsgi_application()