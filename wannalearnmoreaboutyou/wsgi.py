"""
WSGI config for wannalearnmoreaboutyou project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

import django
from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application

# 添加项目根目录到Python路径
current_path = Path(__file__).parent
if str(current_path) not in sys.path:
    sys.path.append(str(current_path))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wannalearnmoreaboutyou.settings')

django.setup()
try:
    execute_from_command_line(['manage.py', 'migrate', '--no-input'])
except Exception:
    pass  # 忽略迁移过程中可能出现的错误

application = get_wsgi_application()