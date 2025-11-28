import json
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
from stock_query import get_stock_recent_info
import numpy as np
import os
import datetime

os.environ['NO_PROXY'] = '*'
# API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
#
# API_KEY = os.getenv("DASHSCOPE_API_KEY")
# if not API_KEY:
#     raise ValueError("DASHSCOPE_API_KEY environment variable is not set")


SERVER_CHAN_KEY = os.getenv("SERVER_CHAN_KEY")
if not SERVER_CHAN_KEY:
    raise ValueError("SERVER_CHAN_KEY 未设置")


API_URL = "http://frp3.ccszxc.site:14266/v1/chat/completions"
API_KEY = os.getenv("GEMINI_API_KEY")

def sanitize_dataframe(df):
    return df.replace({np.nan: None}).astype(object).to_dict(orient="records")

def load_config():
    # 暂时需要预先设置好持仓数据
    with open("stock_position.json", "r", encoding="utf-8") as f:
        return json.load(f)

def push_wechat(text):
    url = f"https://sctapi.ftqq.com/{SERVER_CHAN_KEY}.send"
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "title": f'{current_time} 投资分析报告',
        "desp": text
    }
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"微信推送失败: {e}")

def analyze_portfolio():
    try:
        cfg = load_config()
        stocks = cfg["stocks"]
        total_assets = cfg["total_assets"]

        # 获取行情
        print("正在获取股票数据...")
        stock_data = get_stock_recent_info(stocks)
        stock_data = stock_data[
            ["stock", "name", "current_price", "volume", "pe_ttm", "turnover",
             "MA5", "MA10", "MA20", "MA30", "MA250", "RSI6", "RSI12", "RSI24",
             "MACD_DIF", "MACD_DEA", "MACD", "BOLL_mid", "BOLL_upper", "BOLL_lower"]
        ]

        stock_json = json.dumps(sanitize_dataframe(stock_data), ensure_ascii=False)

        # 添加当前时间戳
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        prompt = f"""
        # Role：你是一名专业的投资分析师兼量化交易顾问。

        # Task：
        根据以下数据生成一份《每周投资分析报告》，需包含技术分析、基本面、仓位风险、组合风险、操作建议等完整内容。

        # Requirements：
        1. 每只股票趋势 + 支撑阻力 + 技术结构分析
        2. 商业模式与基本面分析 + 当前估值
        3. 持仓盈亏及来源分析
        4. 仓位风险评估（集中度、波动）
        5. 组合风险分析 + 调整建议
        6. 下周操作建议（明确买/卖/减仓/观望）
        7. 最后给出专业总结

        # Inputs：
        当前时间：{current_time}

        股票指标数据：
        {stock_json}

        持仓：
        {json.dumps(cfg['positions'], ensure_ascii=False)}

        成本：
        {json.dumps(cfg['cost_prices'], ensure_ascii=False)}

        总资产：{total_assets}

        # Output：
        请输出完整的【每周投资分析报告】
        """

        payload = {
            "model": "gemini-3-pro-preview-thinking",
            "stream": True,
            "messages": [
                {"role": "system", "content": "你是一名专业投资顾问，擅长技术面+基本面分析"},
                {"role": "user", "content": prompt}
            ]
        }

        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

        # 流式输出
        print("正在获取分析报告...")
        buffer = ""
        proxies = {
            "http": None,
            "https": None,
        }

        with requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=30, proxies=proxies) as r:
            for line in r.iter_lines():
                if line:
                    line = line.decode("utf-8").strip()
                    if line.startswith("data: "):
                        line = line[len("data: "):]
                    if line == "[DONE]":
                        break
                    try:
                        data = json.loads(line)
                        delta = data.get("choices", [{}])[0].get("delta", {}).get("content")
                        if delta:
                            print(delta, end="", flush=True)
                            buffer += delta
                    except Exception as e:
                        continue

        print()
        final_report = ''
        # 过滤掉不想要的内部思考内容，只保留正式报告
        if buffer:
            # 查找报告开始的标记
            report_start_keywords = ["【每周投资分析报告】", "每周投资分析报告", "# 每周投资分析报告"]
            start_index = -1
            for keyword in report_start_keywords:
                start_index = buffer.find(keyword)
                if start_index != -1:
                    break

            # 如果找到了开始标记，则只保留从标记开始的内容
            if start_index != -1:
                final_report = buffer[start_index:]
            else:
                # 如果没有找到标记，尝试过滤掉内部思考内容
                if "Framing the User Profile" in buffer:
                    # 找到正式报告的开始位置
                    report_start = buffer.find("【每周投资分析报告】")
                    if report_start != -1:
                        final_report = buffer[report_start:]
                    else:
                        # 如果还是找不到，就使用全部内容（作为后备方案）
                        final_report = buffer
                else:
                    # 没有内部思考内容，使用全部内容
                    final_report = buffer

        if buffer:
            push_wechat(final_report)
            print("📨 每周分析报告已推送！")
        else:
            print("❌ 未能获取到分析报告内容")

    except Exception as e:
        error_msg = f"❌ 执行出错: {str(e)}"
        print(error_msg)

def main():
    # scheduler = BlockingScheduler()

    # #每周五下午 16:00 执行
    # scheduler.add_job(
    #     analyze_portfolio,
    #     "cron",
    #     day_of_week="fri",
    #     hour=16,
    #     minute=0
    # )

    analyze_portfolio()

    # scheduler.start()

if __name__ == "__main__":
    main()