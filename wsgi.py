"""
WSGI config for WannaLearnMoreAboutYou project.

This is a compatibility wrapper to support both uppercase and lowercase module imports.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
current_path = Path(__file__).parent
if str(current_path) not in sys.path:
    sys.path.insert(0, str(current_path))

# Set the correct Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WannaLearnMoreAboutYou.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()