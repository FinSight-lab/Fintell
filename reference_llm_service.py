# services/llm_service.py

"""
LLM服务 - 封装硅基流动API调用
用于生成研报第二页的分析内容
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class LLMService:
    """LLM服务类 - 调用硅基流动API"""

    def __init__(self, api_key: str = None):
        """
        初始化LLM服务

        Args:
            api_key: 硅基流动API密钥（如果为None，从config读取）
        """
        if api_key is None:
            from config import LLM_API_KEY
            api_key = LLM_API_KEY

        if not api_key:
            raise ValueError("LLM API密钥未配置，请在.env文件中设置LLM_API_KEY")

        self.api_key = api_key
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.model = "Pro/deepseek-ai/DeepSeek-V3.2-Exp"
    
    def generate_analysis_content(self, price_data: Dict[str, Any], product_name: str, ai_hints: dict = None, stream_callback=None) -> Optional[Dict[str, Any]]:
        """
        生成市场分析内容（第二页）
        
        Args:
            price_data: 价格变化数据
            product_name: 品种名称
            ai_hints: AI生成提示（可选），包含：
                - extra_data: 补充数据/舆情
                - view_preference: 观点偏好
                - history_reference: 历史评述参考
            stream_callback: 流式输出回调函数，接收每个token
            
        Returns:
            Dict包含:
                - core_viewpoint: 核心观点文本
                - sections: 各个分析章节列表
        """
        try:
            # 构建系统提示词
            system_prompt = self._build_system_prompt(product_name)

            # 构建用户输入
            user_prompt = self._build_user_prompt(price_data, product_name, ai_hints)
            
            # 调用API
            response = self._call_api(system_prompt, user_prompt, stream_callback=stream_callback)
            
            if response:
                logger.info("LLM分析内容生成成功")
                return response
            else:
                logger.error("LLM返回空结果")
                return None
                
        except Exception as e:
            logger.error(f"生成分析内容失败: {e}", exc_info=True)
            return None
        
    def _build_system_prompt(self, product_name: str) -> str:
        """构建系统提示词"""
        return f"""# Role: {product_name}品种研究分析师

    你是一位专业的{product_name}品种研究分析师，服务于石油化工产业链大宗商品研究（如LPG、芳烃、轻烃等），擅长撰写**精简但专业、逻辑清晰**的市场评述报告。

    ## Goals
    基于提供的统计周期内的价格、价差/基差、月差等变化数据，提炼本期**核心矛盾和驱动因素**，撰写一篇结构化的市场分析报告，用于填充研报第二页“评述与分析”。

    ## 总体写作原则（比格式更重要）
    1. **先找主线，再写结构**  
    - 从所有数据中先挑出 2–3 个对市场最关键的变化（如：内外盘明显背离、某区域现货显著走弱、月差结构反转、基差从贴水转升水），作为全文主线。  
    - 章节结构围绕主线自由组织，不需要套用固定模板。

    2. **每一节都要有完整逻辑链**  
    - 必须至少回答三件事：  
        - “发生了什么？”——用关键数据点概括结果；  
        - “为什么？”——从成本端/供给端/需求端/预期端给出合理解释；  
        - “影响是什么？”——对现货、期货、基差、区域套利或下游利润有什么含义。  

    3. **优先行业逻辑，而不是堆数字**  
    - 避免出现多句连续的“上涨x元，涨幅x%”式流水账。  
    - 鼓励使用“受××驱动”“反映出××”“导致××”“压制了××”等逻辑衔接词，使文字更像研究员而不是报表说明。

    ## 数据解读与约束（石化品种专用，重要）

    1. **价格水平（期货、现货、CP、FEI等）**  
    - 可以用“绝对变化 + 百分比”描述。  
    - 若波动很小（例如绝对值很小或涨跌幅＜0.3%），可用“基本持平 / 变化有限”概括，无需精确到小数。

    2. **区域价差 / 基差 / 月差 —— 严禁滥用百分比**
    - 这类指标**以绝对变化和结构变化为主**描述：  
        - 示例：  
        - “山东-华南价差由-112元贴水修复至64元升水，价差走扩176元，区域结构由‘南强北弱’转为‘北强南弱’。”  
    - **不要对价差、基差、月差计算或强调百分比涨跌幅**，尤其是接近0或跨零时，诸如“暴增157%”“变化-192.86%”一类表达在研究语境下没有意义，应避免。  
    - 如需表达“特别大”的变化，可以使用：  
        - “大幅走扩 / 大幅走缩 / 明显修复 / 由贴水转为升水 / 由升水转为贴水 / 结构性反转”等行业习惯说法，而不是具体百分比。

    3. **合约与品种约束（避免PG2612这类错误）**  
    - 只能引用输入数据中出现的合约、品种和地区名称，例如表格中出现的是“PG2511 - PG2512”，则分析中不得擅自改写为“PG2612”等。  
    - 严禁凭空杜撰新的合约代码、报价地区、指数名称或具体数值。

    4. **行业逻辑参考（不要硬套，用得上就用）**  
    在解释变化原因和影响时，可优先从以下石化逻辑出发（根据实际数据自由选用）：  
    - 成本端：原油走势、CP/FEI链条、FOB/到岸价、汇率等；  
    - 供给端：炼厂/PDH/裂解装置负荷与检修、进口到港与船期、港口库存、资源集中或分散程度；  
    - 需求端：化工需求（PDH利润、裂解经济性）、民用燃烧/取暖需求、调油/调峰需求等；  
    - 结构端：  
        - 区域间价差（如山东-华东/华南）与货物流向、套利窗口；  
        - 基差强弱与盘面贴水/升水逻辑、盘面安全垫；  
        - 月差陡峭/平坦、近强远弱/近弱远强，对远期预期和套保/正反套策略的含义。  

    5. **信息来源约束**  
    - 只能基于输入中提供的价格和变动信息进行推理，可以定性使用“偏高/偏低/中性/略有压力”等字眼，但不能虚构具体库存、开工率等数字。  
    - 如跨品种引用（例如原油对LPG的成本支撑），前提是这些价格已在输入数据中出现。

    ## Constraints
    1. 必须输出**严格的 JSON 格式**，不得包含多余字段或多余文本。
    2. `core_viewpoint` 字数控制在 **80–120 字**，只提炼本期**最重要的 1–2 个结构性变化**及其含义，避免面面俱到。
    3. 章节数量、标题完全由你自主决定（建议 4–5 个），可以根据本期主线自由命名，不要求统一格式。
    4. 正文支持 HTML 标签：  
    - <strong>加粗</strong>（用于逻辑锚点、小标题，如“<strong>供应端：</strong>”）；  
    - <span class="highlight-phrase">高亮</span>（用于强调判断，如“<span class="highlight-phrase">内强外弱</span>”）；  
    - <ul class="data-list"><li>列表项</li></ul>（仅在需要列举多个关键数据/结构变化时使用，不要滥用）；  
    - <p>段落</p>（每个自然段用一个 <p> 包裹）。  
    5. 情绪标签自由发挥，样式类型：  
    - bull（看涨/利好/走强）、bear（看跌/利空/走弱）、neutral（中性/震荡）；  
    - 其中 `sentiment_class` 字段只能是 bull、bear 或 neutral 三者之一。  
    6. 语言风格：专业、客观、数据驱动，兼顾现货视角与盘面视角，避免空洞措辞（如“有待观察”“后续仍需跟踪”等无信息句）。  
    7. **篇幅控制**：整体分析在一页内排版舒适为前提，避免逐条翻译表格导致内容过长。

    ## JSON输出结构
    {{
    "core_viewpoint": "核心观点文本（可包含<span class="highlight-phrase">高亮</span>；应体现本期最核心的1–2个变化及其含义）",
    "sections": [
        {{
        "title": "01. 章节标题（例如：内外盘走势与成本）",
        "sentiment_tag": "情绪标签文本（如：内强外弱 / 区域分化 / 成本走弱）",
        "sentiment_class": "bull/bear/neutral",
        "content": "<p>段落1：先用数据概括本章节的关键变化。</p><p><strong>逻辑与影响：</strong>从成本/供需/结构等角度解释变化原因，并说明对现货、盘面或套利策略的影响，必要时可用<ul class="data-list"><li>关键数据1</li><li>关键数据2</li></ul>列举。</p>"
        }}
    ]
    }}
    ## 输出示例
    {{
    "core_viewpoint": "本期LPG市场整体呈现<span class="highlight-phrase">内强外弱、北强南稳</span>格局。外盘FEI随原油小幅回调，成本端支撑略有削弱；国内山东因装置检修与到港偏少，现货与基差明显走强，PG盘面贴水收窄，区域价差修复后货流由“南运北”转为以北区自给为主。",
    "sections": [
        {{
        "title": "01. 行情回顾与成本链",
        "sentiment_tag": "成本走弱、内盘偏强",
        "sentiment_class": "neutral",
        "content": "<p>原油价格本期自83美元回落至约81美元，国际FEI丙烷价格小幅下调约10美元/吨，带动进口理论成本边际走弱。但国内PG主力仅回调约30–50元后即获买盘承接，整体运行明显强于外盘，盘面对成本端的安全垫有所压缩。</p><p><strong>逻辑与影响：</strong>成本端的温和走弱并未引发内盘同步回调，说明当前价格重心更多由国内供需与结构主导，后续若原油再度回落，而现货挺价延续，则PG盘面继续上冲空间有限，需警惕成本与盘面错配的回归压力。</p>"
        }}
    ]
    }}
    """



    
    def _build_user_prompt(self, price_data: Dict[str, Any], product_name: str, ai_hints: dict = None) -> str:
        """构建用户提示词"""
        # 提取价格变化数据
        categories = price_data.get('categories', {})
        previous_date = price_data.get('previous_date')
        latest_date = price_data.get('latest_date')

        # 格式化日期
        period = f"{previous_date.strftime('%Y-%m-%d')} ~ {latest_date.strftime('%Y-%m-%d')}" if previous_date and latest_date else "未知周期"

        # 构建数据摘要
        data_summary = []
        for category_name, models in categories.items():
            for model in models:
                indicator = model.get('item_name', model.get('model_name', ''))
                change = model.get('diff')
                change_pct = model.get('diff_pct')
                latest_value = model.get('latest_value')
                prev_value = model.get('prev_value')

                if change is not None and change_pct is not None:
                    data_summary.append({
                        "分类": category_name,
                        "指标": indicator,
                        f"{latest_date.strftime('%Y-%m-%d')}": f"{latest_value:.2f}" if latest_value is not None else "N/A",
                        f"{previous_date.strftime('%Y-%m-%d')}": f"{prev_value:.2f}" if prev_value is not None else "N/A",
                        "变化量": f"{change:+.2f}",
                        "变化幅度": f"{change_pct:+.2f}%"
                    })

        prompt = f"""请基于以下统计周期内的价格变化数据，撰写一篇{product_name}品种的市场分析报告。

**统计周期**：{period}

**价格变化数据**：
{json.dumps(data_summary, ensure_ascii=False, indent=2)}"""

        # 添加AI提示（如果有）
        if ai_hints:
            if 'extra_data' in ai_hints:
                prompt += f"""

**补充背景数据**：
{ai_hints['extra_data']}

在分析时，请重点参考上述补充背景数据，结合价格变化数据进行综合分析。"""

            if 'view_preference' in ai_hints:
                prompt += f"""

**观点偏好**：
{ai_hints['view_preference']}

请在结论表述中体现这一观点偏好，但需基于数据进行合理论证。"""

            if 'history_reference' in ai_hints:
                prompt += f"""

**历史评述参考**（风格与逻辑参考）：
{ai_hints['history_reference']}

请参考上述历史评述的风格、用词习惯和逻辑结构，保持一致的写作风格。"""

        prompt += """

**要求**：
1. 提炼核心观点，概括本周期最重要的市场变化
2. 根据数据特点，自主决定分析章节（建议4-5个章节）
3. 每个章节需要有明确的标题、情绪标签和详细内容
4. 使用HTML标签进行格式化，确保输出符合JSON结构
5. 如果提供了补充数据、观点偏好或历史参考，请充分结合这些信息

必须仅生成符合要求的JSON。"""

        return prompt
    
    def _call_api(self, system_prompt: str, user_prompt: str, max_retries: int = 3, stream_callback=None) -> Optional[Dict[str, Any]]:
        """
        调用硅基流动API（流式输出，带重试机制）

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            max_retries: 最大重试次数
            stream_callback: 流式输出回调函数，接收每个token

        Returns:
            解析后的JSON响应
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
            "stream": True,  # 启用流式输出
            "max_tokens": 50000,
            "temperature": 0.85,  # 提高温度，增加创造性
            "top_p": 0.9,  # 提高top_p，给模型更多自由度
            "top_k": 50,
            "frequency_penalty": 0.3,  # 降低频率惩罚，允许更自然的表达
            "response_format": {"type": "json_object"}
        }

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    wait_time = 2 ** attempt  # 指数退避：2秒、4秒、8秒
                    logger.info(f"⏳ 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                
                logger.info(f"🤖 正在调用大模型生成分析内容... (尝试 {attempt + 1}/{max_retries})")
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=300  # 增加超时时间到5分钟
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

                    # 跳过非数据行
                    if not line.startswith('data: '):
                        continue

                    # 移除 "data: " 前缀
                    data_str = line[6:]

                    # 检查是否是结束标记
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

                            # 调用回调函数（如果提供）
                            if stream_callback:
                                stream_callback(content_chunk, len(full_content))

                            # 每增加100字输出一次进度
                            current_length = len(full_content)
                            if current_length - last_log_length >= 100:
                                logger.info(f"📝 大模型正在工作中，已生成 {current_length} 字...")
                                last_log_length = current_length

                    except json.JSONDecodeError:
                        continue

                logger.info(f"✓ 大模型输出完成，共生成 {len(full_content)} 字")

                if full_content:
                    # 解析JSON
                    try:
                        parsed_content = json.loads(full_content)
                        logger.info("✓ JSON解析成功，分析报告已生成")
                        return parsed_content
                    except json.JSONDecodeError as e:
                        logger.error(f"✗ JSON解析失败: {e}")
                        logger.error(f"原始内容前500字: {full_content[:500]}...")
                        return None
                else:
                    logger.error("✗ API返回内容为空")
                    return None

            except requests.exceptions.HTTPError as e:
                # HTTP错误（如503）- 可以重试
                if e.response.status_code in [503, 502, 504, 429]:
                    logger.warning(f"⚠️ API暂时不可用 ({e.response.status_code})，将重试...")
                    if attempt == max_retries - 1:
                        logger.error(f"❌ 已达到最大重试次数，放弃请求")
                        return None
                    continue
                else:
                    # 其他HTTP错误不重试
                    logger.error(f"API请求失败: {e}")
                    return None
            except requests.exceptions.RequestException as e:
                logger.error(f"API请求失败: {e}")
                if attempt == max_retries - 1:
                    return None
                continue
            except Exception as e:
                logger.error(f"处理流式输出时发生错误: {e}", exc_info=True)
                return None
        
        # 所有重试都失败
        logger.error("❌ 所有重试尝试均失败")
        return None

