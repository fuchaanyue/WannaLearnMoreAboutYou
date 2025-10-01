# 确保Python将此目录识别为包
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_path = Path(__file__).parent.parent
if str(current_path) not in sys.path:
    sys.path.insert(0, str(current_path))