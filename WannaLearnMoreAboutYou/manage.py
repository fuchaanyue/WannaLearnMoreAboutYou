#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

def main():
    """Run administrative tasks."""
    # 添加当前目录到Python路径
    current_path = Path(__file__).parent
    if str(current_path) not in sys.path:
        sys.path.append(str(current_path))
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wannalearnmoreaboutyou.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()