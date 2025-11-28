"""Test Weekly Report API"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_generate_weekly_report():
    """测试生成周报 API"""
    print("=" * 80)
    print("测试：生成周报")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/api/reports/weekly"
    params = {
        "portfolio_id": 1,
        "skip_push": True,  # 跳过推送
        "save_to_db": True  # 保存到数据库
    }
    
    print(f"\n请求 URL: {url}")
    print(f"参数: {params}")
    print("\n正在生成周报...")
    print("⏳ 这可能需要 1-2 分钟（获取 Wind 数据 + LLM 分析）...\n")
    
    try:
        response = requests.post(url, params=params, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✓ 周报生成成功！")
            print("=" * 80)
            print(f"报告 ID: {result.get('report_id')}")
            print(f"HTML 长度: {result.get('html_length')} 字符")
            print(f"是否推送: {result.get('pushed')}")
            
            if 'analysis_summary' in result:
                summary = result['analysis_summary']
                print(f"\n分析摘要:")
                print(f"  - 核心观点: {summary.get('core_viewpoint')}")
                print(f"  - 个股分析数: {summary.get('stock_count')}")
                print(f"  - 操作建议数: {summary.get('action_count')}")
            
            # 保存 HTML 到文件
            if 'html' in result:
                output_file = "test_weekly_report.html"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result['html'])
                print(f"\n✓ HTML 已保存到: {output_file}")
                print(f"  可以在浏览器中打开查看效果")
            
            return True
        else:
            print(f"\n✗ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print("\n✗ 请求超时（超过 5 分钟）")
        return False
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        return False


def test_get_latest_report():
    """测试获取最新周报 API"""
    print("\n" + "=" * 80)
    print("测试：获取最新周报")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/api/reports/latest"
    params = {"portfolio_id": 1}
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✓ 获取成功！")
            print(f"报告 ID: {result.get('id')}")
            print(f"报告日期: {result.get('report_date')}")
            print(f"创建时间: {result.get('created_at')}")
            print(f"是否推送: {result.get('pushed')}")
            return True
        else:
            print(f"\n✗ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        return False


def main():
    print("\n" + "=" * 80)
    print("FastAPI 周报生成接口测试")
    print("=" * 80)
    print(f"API 地址: {API_BASE_URL}")
    print("=" * 80)
    
    # 测试 1: 生成周报
    success1 = test_generate_weekly_report()
    
    # 测试 2: 获取最新周报
    if success1:
        success2 = test_get_latest_report()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
