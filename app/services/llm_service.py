"""LLM Service - 基于 Gemini API 的分析服务"""

import requests
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class LLMService:
    """LLM 服务类 - 调用 Gemini API 生成周报分析"""

    def __init__(self, api_url: str, api_key: str, model: str = "gemini-3-pro-preview-thinking"):
        """
        初始化 LLM 服务

        Args:
            api_url: API 地址
            api_key: API 密钥
            model: 模型名称
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
    
    def generate_weekly_analysis(
        self, 
        report_data: Dict[str, Any],
        stream_callback=None
    ) -> Optional[Dict[str, Any]]:
        """
        生成周报分析内容
        
        Args:
            report_data: 周报数据（包含持仓、行情、技术指标等）
            stream_callback: 流式输出回调函数，接收每个token
            
        Returns:
            Dict 包含:
                - core_viewpoint: 核心观点
                - holdings_analysis: 持仓盈亏分析
                - stock_analysis: 个股分析列表
                - action_plan: 调仓建议
                - risk_assessment: 风险评估
                - sector_view: 板块视角
        """
        try:
            # 构建系统提示词
            system_prompt = self._build_system_prompt()

            # 构建用户输入
            user_prompt = self._build_user_prompt(report_data)
            
            # 调用 API
            response = self._call_api(system_prompt, user_prompt, stream_callback=stream_callback)
            
            if response:
                logger.info("✓ LLM 分析内容生成成功")
                return response
            else:
                logger.error("✗ LLM 返回空结果")
                return None
                
        except Exception as e:
            logger.error(f"生成分析内容失败: {e}", exc_info=True)
            return None
        
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """# Role: 专业股票投资分析师

你是一位专业的股票投资分析师，擅长 A 股市场分析和持仓管理，能够撰写**精简但专业、逻辑清晰**的周报分析。

## Goals
基于提供的持仓数据、行情数据和技术指标，提炼本周**核心矛盾和驱动因素**，撰写一篇结构化的周报分析，用于填充 HTML 周报模板。

## 总体写作原则
1. **先找主线，再写结构**  
   - 从所有数据中挑出 2-3 个对组合最关键的变化（如：某股票明显走弱、技术指标反转、仓位过于集中等）
   - 章节结构围绕主线组织

2. **每一节都要有完整逻辑链**  
   - "发生了什么？"——用关键数据点概括
   - "为什么？"——从技术面/基本面/题材逻辑给出解释
   - "影响是什么？"——对持仓、风险、操作有什么含义

3. **优先行业逻辑，而不是堆数字**  
   - 避免流水账式的数据罗列
   - 使用"受××驱动""反映出××""导致××"等逻辑衔接词

## 数据解读约束

1. **技术指标解读**
   - MA（均线）：关注价格与均线的位置关系、均线排列
   - RSI：超买（>70）、超卖（<30）、中性区间
   - MACD：金叉/死叉、DIF/DEA 位置关系
   - BOLL：价格突破上轨/下轨、布林带收口/开口

2. **A 股特色分析**
   - 题材逻辑：当前市场主线、板块轮动、资金偏好
   - 风格判断：成长/价值/高股息/消费等
   - 情绪判断：超跌反弹、追涨杀跌、恐慌性下跌等

3. **操作建议原则**
   - 具体可执行：给出价格区间、分批计划
   - 风险可控：止损位、止盈位
   - 符合 A 股习惯：T+1、涨跌停限制

## JSON 输出结构
{
  "core_viewpoint": "核心观点文本（80-120字，可包含 <span class='highlight'>高亮</span>）",
  "kpis": {
    "weekly_return": 0.0,  // 本周收益率（%）
    "ytd_return": 0.0,     // 年初至今收益率（%）
    "position_ratio": 0.0, // 仓位占比（%）
    "action_count": 0      // 建议调仓数量
  },
  "holdings_analysis": {
    "summary": "持仓盈亏总结（100-150字）",
    "highlights": ["要点1", "要点2", "要点3"]
  },
  "stock_analysis": [
    {
      "stock_code": "600519.SH",
      "stock_name": "贵州茅台",
      "status": "超卖反弹/横盘震荡/趋势破位/多头趋势/回调预警",
      "status_class": "warning/neutral/negative/positive",
      "technical": "技术面分析（50-80字）",
      "fundamental": "基本面分析（50-80字）",
      "theme": "题材逻辑分析（50-80字）",
      "risk": "风险点（30-50字）",
      "suggestion": "操作建议（50-80字，加粗关键词）"
    }
  ],
  "action_plan": [
    {
      "stock_code": "600519.SH",
      "stock_name": "贵州茅台",
      "action": "逢高减仓/反弹减仓/逐步清仓/继续持有/加仓",
      "action_class": "reduce/clear/add/hold",
      "price_range": "1460-1480元",
      "current_position": "45%",
      "target_position": "40%",
      "plan": "触及区间上沿分两次各减2.5%",
      "reason": "单票仓位过重，利用超跌反弹优化集中度"
    }
  ],
  "risk_assessment": {
    "level": "中等偏高/中等/偏低",
    "level_score": 65,  // 0-100
    "current_risks": [
      "行业集中度：近100%集中在泛消费领域",
      "个股集中度：贵州茅台单只仓位约45%",
      "风格单一：防御性消费占比高，进攻性不足"
    ],
    "optimization_suggestions": [
      "去重叠：建议逐步减仓食品ETF和消费LOF",
      "止损弱势：对珀莱雅等趋势破位标的减仓",
      "增加多样性：适度配置科技成长、高股息红利"
    ]
  },
  "sector_view": {
    "summary": "从当前市场结构看，消费并非绝对主线...",
    "main_theme": "科技成长（如半导体、算力）、高股息红利",
    "consumer_position": "消费处于深跌后震荡修复阶段",
    "portfolio_position": "当前组合更接近'进可攻能力有限、退可守尚可'的状态",
    "adjustment_direction": "释放部分消费仓位，引入科技成长 & 高股息"
  },
  "target_allocation": {
    "consumer": 55,
    "tech_growth": 20,
    "dividend": 15,
    "cash": 10
  }
}

## Constraints
1. 必须输出**严格的 JSON 格式**
2. `core_viewpoint` 字数 80-120 字
3. 个股分析要全面覆盖所有持仓
4. 操作建议要具体可执行
5. 风险评估要客观中肯
6. 语言风格：专业、客观、数据驱动
"""
    
    def _build_user_prompt(self, report_data: Dict[str, Any]) -> str:
        """构建用户提示词"""
        # 提取关键数据
        portfolio = report_data.get('portfolio', {})
        metrics = report_data.get('metrics', {})
        holdings = report_data.get('holdings', [])
        period = report_data.get('period', '')
        
        # 构建持仓数据摘要
        holdings_summary = []
        for h in holdings:
            holdings_summary.append({
                "股票代码": h['stock_code'],
                "股票名称": h['stock_name'],
                "当前价格": f"{h['current_price']:.2f}",
                "成本价": f"{h['cost_price']:.2f}",
                "持仓数量": h['quantity'],
                "市值": f"{h['market_value']:.2f}",
                "盈亏": f"{h['profit_loss']:+.2f}",
                "盈亏比例": f"{h['profit_loss_pct']:+.2f}%",
                "仓位占比": f"{h.get('position_ratio', 0):.1f}%",
                "技术指标": h.get('indicators', {})
            })
        
        prompt = f"""请基于以下持仓数据和市场行情，撰写一篇周报分析。

**统计周期**：{period}

**组合信息**：
- 组合名称：{portfolio.get('name')}
- 总资产：¥{metrics.get('total_market_value', 0) + metrics.get('cash', 0):,.2f}
- 持仓市值：¥{metrics.get('total_market_value', 0):,.2f}
- 现金：¥{metrics.get('cash', 0):,.2f}
- 仓位占比：{metrics.get('position_ratio', 0):.1f}%

**盈亏情况**：
- 总盈亏：¥{metrics.get('total_profit_loss', 0):+,.2f}
- 收益率：{metrics.get('total_return_pct', 0):+.2f}%

**持仓明细**（{len(holdings)} 只股票）：
{json.dumps(holdings_summary, ensure_ascii=False, indent=2)}

**要求**：
1. 分析每只股票的技术面、基本面、题材逻辑
2. 给出具体的操作建议（价格区间、分批计划）
3. 评估组合风险并提出优化建议
4. 分析当前市场主线和板块轮动
5. 输出严格的 JSON 格式

请开始分析："""

        return prompt
    
    def _call_api(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_retries: int = 3,
        stream_callback=None
    ) -> Optional[Dict[str, Any]]:
        """
        调用 Gemini API（流式输出，带重试机制）

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            max_retries: 最大重试次数
            stream_callback: 流式输出回调函数

        Returns:
            解析后的 JSON 响应
        """
        import time
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": True,
            "max_tokens": 50000,
            "temperature": 0.85,
            "top_p": 0.9,
            "top_k": 50,
            "frequency_penalty": 0.3,
            "response_format": {"type": "json_object"}
        }

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    wait_time = 2 ** attempt
                    logger.info(f"⏳ 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                
                logger.info(f"🤖 正在调用大模型生成分析内容... (尝试 {attempt + 1}/{max_retries})")
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=300
                )
                response.raise_for_status()

                # 收集流式输出
                full_content = ""
                chunk_count = 0
                last_log_length = 0

                for line in response.iter_lines():
                    if not line:
                        continue

                    line = line.decode('utf-8')

                    if not line.startswith('data: '):
                        continue

                    data_str = line[6:]

                    if data_str.strip() == '[DONE]':
                        logger.info("✓ 大模型内容生成完成")
                        break

                    try:
                        data = json.loads(data_str)
                        delta = data.get('choices', [{}])[0].get('delta', {})
                        content_chunk = delta.get('content', '')

                        if content_chunk:
                            full_content += content_chunk
                            chunk_count += 1

                            if stream_callback:
                                stream_callback(content_chunk, len(full_content))

                            current_length = len(full_content)
                            if current_length - last_log_length >= 100:
                                logger.info(f"📝 大模型正在工作中，已生成 {current_length} 字...")
                                last_log_length = current_length

                    except json.JSONDecodeError:
                        continue

                logger.info(f"✓ 大模型输出完成，共生成 {len(full_content)} 字")

                if full_content:
                    # 保存原始内容用于调试
                    original_content = full_content
                    
                    # 1. 过滤掉 <think> 标签内容（Gemini 的思考过程）
                    if '<think>' in full_content:
                        think_end = full_content.find('</think>')
                        if think_end != -1:
                            full_content = full_content[think_end + 8:].strip()
                            logger.info(f"✓ 已过滤思考内容，剩余 {len(full_content)} 字")
                    
                    # 2. 尝试提取 JSON（可能在 markdown 代码块中）
                    if '```json' in full_content:
                        start = full_content.find('```json') + 7
                        end = full_content.find('```', start)
                        if end != -1:
                            full_content = full_content[start:end].strip()
                            logger.info("✓ 从 markdown 代码块中提取 JSON")
                    elif '```' in full_content:
                        start = full_content.find('```') + 3
                        end = full_content.find('```', start)
                        if end != -1:
                            full_content = full_content[start:end].strip()
                            logger.info("✓ 从代码块中提取内容")
                    
                    # 3. 尝试找到 JSON 对象的开始和结束
                    if not full_content.strip().startswith('{'):
                        # 查找第一个 {
                        json_start = full_content.find('{')
                        if json_start != -1:
                            full_content = full_content[json_start:]
                            logger.info("✓ 找到 JSON 起始位置")
                    
                    # 4. 使用正则表达式提取 JSON
                    import re
                    
                    # 尝试直接解析
                    try:
                        parsed_content = json.loads(full_content)
                        logger.info("✓ JSON 解析成功，分析报告已生成")
                        return parsed_content
                    except json.JSONDecodeError:
                        logger.warning("⚠️ 直接解析失败，尝试使用正则表达式提取 JSON...")
                        
                        # 使用正则表达式查找 JSON 对象
                        # 匹配最外层的 { ... }
                        json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'
                        matches = re.findall(json_pattern, full_content, re.DOTALL)
                        
                        if matches:
                            # 尝试解析找到的每个 JSON 对象
                            for i, match in enumerate(matches):
                                try:
                                    parsed_content = json.loads(match)
                                    # 验证是否包含必要的字段
                                    if 'core_viewpoint' in parsed_content or 'stock_analysis' in parsed_content:
                                        logger.info(f"✓ 使用正则表达式成功提取并解析 JSON (匹配 {i+1}/{len(matches)})")
                                        return parsed_content
                                except json.JSONDecodeError:
                                    continue
                        
                        logger.error("✗ 所有 JSON 提取尝试均失败")
                        logger.error(f"处理后内容前500字: {full_content[:500]}...")
                        
                        # 保存原始内容用于调试
                        with open("llm_error_output.txt", 'w', encoding='utf-8') as f:
                            f.write(original_content)
                        logger.error(f"原始内容已保存到: llm_error_output.txt")
                        
                        return None
                else:
                    logger.error("✗ API 返回内容为空")
                    return None

            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [503, 502, 504, 429]:
                    logger.warning(f"⚠️ API 暂时不可用 ({e.response.status_code})，将重试...")
                    if attempt == max_retries - 1:
                        logger.error(f"❌ 已达到最大重试次数，放弃请求")
                        return None
                    continue
                else:
                    logger.error(f"API 请求失败: {e}")
                    return None
            except requests.exceptions.RequestException as e:
                logger.error(f"API 请求失败: {e}")
                if attempt == max_retries - 1:
                    return None
                continue
            except Exception as e:
                logger.error(f"处理流式输出时发生错误: {e}", exc_info=True)
                return None
        
        logger.error("❌ 所有重试尝试均失败")
        return None
