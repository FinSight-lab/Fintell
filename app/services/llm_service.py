# app/services/llm_service.py
"""
LLM Service - 基于 Gemini API 的周报分析服务
"""

import requests
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class LLMService:
    """LLM 服务类 - 调用 Gemini API 生成周报分析（JSON + HTML 片段）"""

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
        生成周报分析内容（结构化 JSON，供 Jinja2 模板渲染）

        Args:
            report_data: 周报输入数据（组合信息、持仓、行情、技术指标等）
            stream_callback: 流式输出回调函数，接收每个 token 文本

        Returns:
            Dict 包含（示意结构）：
                - core_viewpoint      核心观点（可含 HTML 片段）
                - kpis                顶部 KPI 数据
                - holdings_analysis   持仓文字分析
                - stock_analysis      个股分析列表
                - action_plan         调仓建议列表
                - risk_assessment     风险评估
                - sector_view         板块 & 题材视角
                - target_allocation   下周目标仓位结构
        """
        try:
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(report_data)

            response = self._call_api(system_prompt, user_prompt, stream_callback=stream_callback)

            if response:
                logger.info("✓ LLM 周报分析内容生成成功")
                return response
            else:
                logger.error("✗ LLM 返回空结果")
                return None

        except Exception as e:
            logger.error(f"生成周报分析内容失败: {e}", exc_info=True)
            return None

    # --------------------------------------------------------------------- #
    # 提示词：系统角色定义 + JSON 输出结构
    # --------------------------------------------------------------------- #
    def _build_system_prompt(self) -> str:
        """构建系统提示词（主要约束输出 JSON 结构 + 允许的 HTML，尽量不限制内容发挥）"""
        return r"""
# Role

你是一名熟悉 A 股市场的专业投资顾问兼周报写手。  
你的任务：根据传入的组合数据，输出一个 **严格的 JSON 对象**，用于渲染一个周度持仓报告页面。

你可以自由发挥你的投研能力和表达风格，但**必须**遵守下面的格式约束。

--------------------------------
## 1. 允许使用的 HTML（只在指定字段内）

部分字段是“富文本”，前端会用 `|safe` 渲染，你可以在这些字段中嵌入简单 HTML 来增强表现力，但只允许：

- `<strong>文本</strong>`：用于小标题、关键结论、操作动词等逻辑锚点；
- `<span class="highlight-phrase">文本</span>`：用于强调组合层面的重要判断；
- `<span class="text-up">+3.5%</span>` / `<span class="text-down">-4.2%</span>`：用于文字里的涨跌方向；
- `<p>段落内容</p>`：一个自然段一个 `<p>`；
- `<ul class="data-list"><li>条目</li></ul>`：当你需要列出关键要点时使用。

**禁止** 使用其它标签（例如 table/div/h1/script/style 等），也不要输出任何 CSS/JS。

允许 HTML 的字段会在下面 JSON 结构说明里明确标出来。

--------------------------------
## 2. 输出 JSON 结构（必须完全匹配）

你必须输出一个 JSON 对象，结构如下（示例值仅用于说明，实际内容请你自己分析生成）：

{
  "core_viewpoint": "字符串，80-140 字，允许 HTML，用来在开头一段话里点明本周组合的核心矛盾与主线。",

  "kpis": {
    "weekly_return": 0.0,
    "benchmark_return": 0.0,
    "ytd_return": 0.0,
    "position_ratio": 0.0,
    "action_count": 0,
    "ytd_comment": "字符串，简短点评今年以来表现。",
    "position_comment": "字符串，对当前仓位水平的点评。",
    "action_summary": "字符串，对本周调仓重点的摘要。"
  },

  "section_subtitles": {
    "overview": "字符串，概括“本周组合总览”的一句话小标题。",
    "holdings": "字符串，概括“持仓盈亏分析”想表达的重点。",
    "stock": "字符串，概括“个股与 ETF 分析”的角度，例如更偏技术/题材/轮动。",
    "action": "字符串，概括“本周操作计划”的风格（如偏防御、偏优化结构等）。",
    "risk": "字符串，概括风险与优化部分的主基调。",
    "sector": "字符串，概括板块和题材视角的核心观点。"
  },

  "holdings_analysis": {
    "summary": "字符串，100-200 字，对持仓盈亏结构的整体点评，允许 HTML。",
    "highlights": [
      "字符串，要点 1，允许 HTML。",
      "字符串，要点 2，允许 HTML。",
      "字符串，要点 3，允许 HTML。"
    ]
  },

  "stock_analysis": [
    {
      "stock_code": "600519.SH",
      "stock_name": "贵州茅台",
      "stock_role": "核心持仓/卫星持仓/配置类/观察仓 等自由描述",
      "status": "超卖反弹/横盘震荡/趋势破位/多头趋势/回调预警 等你认为合适的标签",
      "status_class": "positive/negative/warning/neutral",
      "sentiment_class": "bull/bear/neutral",

      "technical": "技术面分析，50-120 字，允许 HTML（例如以 <strong>技术面：</strong> 开头）。",
      "fundamental": "基本面分析，50-120 字，允许 HTML。",
      "theme": "题材与风格逻辑，50-120 字，允许 HTML，注意符合 A 股话语（主线/轮动/资金风格等）。",
      "risk": "风险点，30-80 字，允许 HTML。",
      "suggestion": "操作建议，50-120 字，允许 HTML，包含执行思路（如区间、分批）、仓位思路等。"
    }
  ],

  "action_plan": [
    {
      "stock_code": "600519.SH",
      "stock_name": "贵州茅台",
      "action": "逢高减仓/反弹减仓/逐步清仓/继续持有/逢低加仓 等简洁动词短语",
      "action_class": "reduce/clear/add/hold",
      "price_range": "例如 \"1460–1480 元\" 或 \"+1% 涨幅内择机\"",
      "current_position_pct": 45.0,
      "target_position_pct": 40.0,
      "plan": "执行计划说明，例如 “触及区间上沿分两次各减 2.5%”。",
      "reason": "一句话逻辑摘要，说明为什么这样操作。"
    }
  ],

  "risk_assessment": {
    "level": "偏低/中等/中等偏高/偏高 等自然中文描述",
    "level_score": 65,
    "current_risks": [
      "当前风险点 1，允许 HTML。",
      "当前风险点 2，允许 HTML。",
      "当前风险点 3，允许 HTML。"
    ],
    "optimization_suggestions": [
      "优化建议 1，允许 HTML。",
      "优化建议 2，允许 HTML。",
      "优化建议 3，允许 HTML。"
    ]
  },

  "sector_view": {
    "summary": "板块 & 题材综合视角的完整段落，允许 HTML。",
    "main_theme": "一句话说明你眼中当前市场资金主线（例如 “科技成长（算力/半导体）、高股息红利”）。",
    "consumer_position": "一句话说明消费板块在当前结构中的位置。",
    "portfolio_position": "一句话说明当前组合在风格/节奏中的位置。",
    "adjustment_direction": "一句话说明未来一两周调仓方向。"
  },

  "target_allocation": {
    "consumer": {
      "percent": 55,
      "label": "消费相关（你可以自由命名，例如“消费修复”）"
    },
    "tech_growth": {
      "percent": 20,
      "label": "科技成长（例如“科技成长/算力相关”）"
    },
    "dividend": {
      "percent": 15,
      "label": "高股息/价值（例如“高股息稳健资产”）"
    },
    "cash": {
      "percent": 10,
      "label": "现金/货基（例如“现金缓冲”）"
    }
  }
}

--------------------------------
## 3. 类型 & 约束汇总（非常重要）

1. **必须输出严格 JSON**：
   - 最外层是一个 `{}` 对象；
   - 不允许出现任何解释文字、注释、额外字段。

2. 数值字段必须是裸数字：
   - `weekly_return`, `benchmark_return`, `ytd_return`, `position_ratio`, `action_count`,
     `current_position_pct`, `target_position_pct`, `level_score`,
     以及 `target_allocation` 中的 `percent`；
   - 不要在数值字段里加 `%` 或任何单位，也不要嵌入 HTML。

3. 只有这些字段可以包含 HTML：
   - `core_viewpoint`
   - `holdings_analysis.summary`
   - `holdings_analysis.highlights[*]`
   - `stock_analysis[*].technical`
   - `stock_analysis[*].fundamental`
   - `stock_analysis[*].theme`
   - `stock_analysis[*].risk`
   - `stock_analysis[*].suggestion`
   - `risk_assessment.current_risks[*]`
   - `risk_assessment.optimization_suggestions[*]`
   - `sector_view.summary`

4. 枚举值约束：
   - `status_class` ∈ {`positive`, `negative`, `warning`, `neutral`};
   - `sentiment_class` ∈ {`bull`, `bear`, `neutral`};
   - `action_class` ∈ {`reduce`, `clear`, `add`, `hold`}。

5. 内容风格：
   - 你可以自由使用 A 股常见表达（主线、情绪、轮动、超跌反弹等）；
   - 表达可以有自己的风格，但尽量**简洁、信息密度高**，避免空洞语句。

请根据我稍后提供的组合数据，直接输出一个满足上述结构与约束的 JSON 对象。
"""

    def _build_user_prompt(self, report_data: Dict[str, Any]) -> str:
        """构建用户提示词：把组合/持仓/行情数据打包给模型，尽量少干预内容，仅描述上下文"""

        portfolio = report_data.get("portfolio", {})
        metrics = report_data.get("metrics", {})
        holdings = report_data.get("holdings", [])
        period = report_data.get("period", "")
        benchmark_name = report_data.get("benchmark_name", "沪深300")
        benchmark_return = report_data.get("benchmark_return", 0.0)

        holdings_summary = []
        for h in holdings:
            indicators = h.get("indicators", {})
            holdings_summary.append(
                {
                    "股票代码": h.get("stock_code"),
                    "股票名称": h.get("stock_name"),
                    "当前价格": f"{h.get('current_price', 0.0):.2f}",
                    "成本价": f"{h.get('cost_price', 0.0):.2f}",
                    "持仓数量": h.get("quantity", 0),
                    "市值": f"{h.get('market_value', 0.0):.2f}",
                    "盈亏": f"{h.get('profit_loss', 0.0):+,.2f}",
                    "盈亏比例": f"{h.get('profit_loss_pct', 0.0):+.2f}%",
                    "仓位占比": f"{h.get('position_ratio', 0.0):.1f}%",
                    "技术指标": indicators
                }
            )

        total_assets = metrics.get("total_market_value", 0.0) + metrics.get("cash", 0.0)

        prompt = f"""
下面是一个股票组合在本统计周期内的数据快照，请你基于这些数据，输出一个符合系统提示中 JSON 结构的分析结果。

【统计周期】
{period}

【组合信息】
- 组合名称：{portfolio.get('name', '未命名组合')}
- 总资产：¥{total_assets:,.2f}
- 持仓市值：¥{metrics.get('total_market_value', 0.0):,.2f}
- 现金：¥{metrics.get('cash', 0.0):,.2f}
- 当前整体仓位：{metrics.get('position_ratio', 0.0):.1f}%

【整体盈亏》
- 总盈亏：¥{metrics.get('total_profit_loss', 0.0):+,.2f}
- 总体收益率：{metrics.get('total_return_pct', 0.0):+.2f}%
- 本周组合收益率：{metrics.get('weekly_return', 0.0):+.2f}%
- 基准（{benchmark_name}）本周收益率：{benchmark_return:+.2f}%

【持仓明细列表】（共 {len(holdings)} 只）
以下为每只持仓的简要数据与技术指标（JSON 数组）：
{json.dumps(holdings_summary, ensure_ascii=False, indent=2)}

请基于这些数据进行你自己的专业分析和判断，自由发挥内容，
但最终输出必须是一个**严格符合系统提示中定义结构的 JSON 对象**。不要输出任何多余说明文字。
"""

        return prompt


    # --------------------------------------------------------------------- #
    # 调用 API（流式输出 + JSON 提取）
    # --------------------------------------------------------------------- #
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
            解析后的 JSON 响应（字典）
        """
        import time
        import re

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": True,
            "max_tokens": 50000,
            "temperature": 0.6,
            "top_p": 0.9,
            "top_k": 40,
            "frequency_penalty": 0.1,
            "response_format": {"type": "json_object"},
        }

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    wait_time = 2 ** attempt
                    logger.info(f"⏳ 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)

                logger.info(f"🤖 调用大模型生成周报分析... (尝试 {attempt + 1}/{max_retries})")

                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=300,
                )
                response.raise_for_status()

                full_content = ""
                last_log_length = 0

                for line in response.iter_lines():
                    if not line:
                        continue

                    line = line.decode("utf-8")

                    if not line.startswith("data: "):
                        continue

                    data_str = line[6:]

                    if data_str.strip() == "[DONE]":
                        logger.info("✓ 流式输出完成")
                        break

                    try:
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content_chunk = delta.get("content", "")

                        if content_chunk:
                            full_content += content_chunk

                            if stream_callback:
                                stream_callback(content_chunk, len(full_content))

                            if len(full_content) - last_log_length >= 200:
                                logger.info(f"📝 大模型已生成约 {len(full_content)} 字...")
                                last_log_length = len(full_content)

                    except json.JSONDecodeError:
                        continue

                logger.info(f"✓ 大模型输出结束，总长度 {len(full_content)} 字")

                if not full_content:
                    logger.error("✗ API 返回内容为空")
                    return None

                original_content = full_content

                # 1. 过滤 <think> 思考内容
                if "<think>" in full_content:
                    think_end = full_content.find("</think>")
                    if think_end != -1:
                        full_content = full_content[think_end + len("</think>") :].strip()
                        logger.info(f"✓ 已剥离思考内容，剩余 {len(full_content)} 字")

                # 2. 若包在 ```json 代码块中，先截取
                if "```json" in full_content:
                    start = full_content.find("```json") + len("```json")
                    end = full_content.find("```", start)
                    if end != -1:
                        full_content = full_content[start:end].strip()
                        logger.info("✓ 从 ```json 代码块中提取内容")
                elif "```" in full_content:
                    start = full_content.find("```") + len("```")
                    end = full_content.find("```", start)
                    if end != -1:
                        full_content = full_content[start:end].strip()
                        logger.info("✓ 从 ``` 代码块中提取内容")

                # 3. 如果前面有多余文字，尝试找到第一个 JSON 起始位置
                if "{" in full_content and not full_content.lstrip().startswith("{"):
                    json_start = full_content.find("{")
                    full_content = full_content[json_start:]
                    logger.info("✓ 已截断到第一个 '{{' 开始的位置")

                # 4. 先尝试直接解析
                try:
                    parsed = json.loads(full_content)
                    logger.info("✓ 直接解析 JSON 成功")
                    return parsed
                except json.JSONDecodeError:
                    logger.warning("⚠️ 直接解析失败，尝试用正则提取最外层 JSON 对象...")

                    json_pattern = r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}"
                    matches = re.findall(json_pattern, full_content, re.DOTALL)

                    for i, match in enumerate(matches):
                        try:
                            parsed = json.loads(match)
                            if isinstance(parsed, dict) and (
                                "core_viewpoint" in parsed or "stock_analysis" in parsed
                            ):
                                logger.info(f"✓ 第 {i+1}/{len(matches)} 个匹配成功解析 JSON")
                                return parsed
                        except json.JSONDecodeError:
                            continue

                    logger.error("✗ 无法从返回内容中解析出合法 JSON")
                    logger.error(f"处理后内容前 500 字：{full_content[:500]}...")

                    try:
                        with open("llm_error_output.txt", "w", encoding="utf-8") as f:
                            f.write(original_content)
                        logger.error("原始内容已保存到 llm_error_output.txt")
                    except Exception:
                        pass

                    return None

            except requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response is not None else None
                if status in [429, 500, 502, 503, 504]:
                    logger.warning(f"⚠️ API HTTP 错误 {status}，将重试...")
                    if attempt == max_retries - 1:
                        logger.error("❌ 已达到最大重试次数，放弃请求")
                        return None
                    continue
                else:
                    logger.error(f"API HTTP 错误: {e}")
                    return None
            except requests.exceptions.RequestException as e:
                logger.error(f"API 请求异常: {e}")
                if attempt == max_retries - 1:
                    return None
                continue
            except Exception as e:
                logger.error(f"处理流式输出时发生未知错误: {e}", exc_info=True)
                return None

        logger.error("❌ 所有重试尝试均失败")
        return None
