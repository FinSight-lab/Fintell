"""测试 ServerChan 推送"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置环境变量
os.environ['NO_PROXY'] = '*'

import requests

# ServerChan Key
SERVERCHAN_KEY = "SCT304146TbleYgvIhcisTvxmzihJINLWK"

def test_push():
    """测试推送"""
    url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
    
    data = {
        "title": "🧪 Smart Portfolio Manager 推送测试",
        "desp": """
## 测试消息

这是一条来自 **Smart Portfolio Manager** 的测试消息。

### 测试内容
- ✅ ServerChan 推送功能正常
- ✅ 微信通知已配置
- ✅ 系统运行正常

---
*此消息用于验证推送功能*
""",
        "short": "推送功能测试"
    }
    
    print(f"正在推送到: {url}")
    
    try:
        response = requests.post(url, data=data, timeout=30)
        print(f"HTTP 状态码: {response.status_code}")
        
        result = response.json()
        print(f"响应: {result}")
        
        if result.get("code") == 0:
            print("✓ 推送成功！")
            return True
        else:
            print(f"✗ 推送失败: {result.get('message')}")
            return False
    except Exception as e:
        print(f"✗ 推送异常: {e}")
        return False


if __name__ == "__main__":
    success = test_push()
    sys.exit(0 if success else 1)
