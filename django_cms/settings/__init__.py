# 从环境变量中读取配置环境，默认使用开发环境
import os
ENV = os.environ.get('DJANGO_ENV', 'dev')

# 根据环境导入对应配置
if ENV == 'prod':
    from .prod import *  # 生产环境：导入prod.py所有配置
else:
    from .dev import *   # 默认：导入dev.py所有配置