"""
WSGI config for WannaLearnMoreAboutYou project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_path = Path(__file__).parent
if str(current_path) not in sys.path:
    sys.path.append(str(current_path))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WannaLearnMoreAboutYou.settings')

application = get_wsgi_application()