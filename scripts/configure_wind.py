"""Configure wind-linker API"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
import subprocess

def configure_wind():
    """配置 wind-linker API 地址"""
    print(f"配置 Wind API: {settings.WIND_API_URL}")
    
    try:
        result = subprocess.run(
            ["python", "-m", "wind_linker", "config", settings.WIND_API_URL],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Wind API 配置成功")
        else:
            print(f"⚠️  Wind API 配置可能失败: {result.stderr}")
    except Exception as e:
        print(f"✗ Wind API 配置失败: {e}")

if __name__ == "__main__":
    configure_wind()
