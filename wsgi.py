"""
WSGI config for wannalearnmoreaboutyou project.

This is a compatibility wrapper to support both uppercase and lowercase module imports.
"""

import os
import sys
from pathlib import Path

import django
from django.core.management import execute_from_command_line

# Add project root to Python path
current_path = Path(__file__).parent
if str(current_path) not in sys.path:
    sys.path.insert(0, str(current_path))

# Set the correct Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wannalearnmoreaboutyou.settings')

# 在WSGI应用启动时执行数据库迁移和静态文件收集
try:
    django.setup()
    execute_from_command_line(['manage.py', 'migrate', '--no-input'])
    execute_from_command_line(['manage.py', 'collectstatic', '--no-input'])
except Exception:
    pass  # 忽略过程中可能出现的错误

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()