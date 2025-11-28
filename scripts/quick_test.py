"""快速测试脚本"""
import sys
import os
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

print("1. 检查环境变量...")
api_key = os.getenv('GEMINI_API_KEY')
print(f"   API Key: {'已设置' if api_key else '未设置'}")

print("\n2. 检查测试数据...")
import json
try:
    with open('test_data_output.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"   持仓数量: {len(data.get('holdings', []))}")
except Exception as e:
    print(f"   错误: {e}")

print("\n3. 测试模板服务...")
try:
    from app.services.template_service import TemplateService
    ts = TemplateService()
    print("   模板服务初始化成功")
except Exception as e:
    print(f"   错误: {e}")

print("\n4. 测试 LLM 服务...")
try:
    from app.services.llm_service import LLMService
    print("   LLM 服务导入成功")
except Exception as e:
    print(f"   错误: {e}")

print("\n测试完成!")
