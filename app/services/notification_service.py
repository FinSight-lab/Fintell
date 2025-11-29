"""
Notification Service - 通知推送服务

支持 ServerChan（微信推送）等通知渠道
"""

import requests
import time
from typing import Optional
from datetime import datetime

from app.core.logging import get_logger
from app.core.exceptions import NotificationError

logger = get_logger(__name__)


class NotificationService:
    """通知推送服务类"""
    
    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # 秒
    
    def __init__(self, serverchan_key: Optional[str] = None):
        """
        初始化通知服务
        
        Args:
            serverchan_key: ServerChan 的 SendKey
        """
        self.serverchan_key = serverchan_key
        
        if serverchan_key:
            logger.info("✓ ServerChan 推送服务已配置")
        else:
            logger.warning("⚠️ ServerChan 推送服务未配置（缺少 SendKey）")
    
    def send_serverchan(
        self, 
        title: str, 
        content: str,
        short: Optional[str] = None
    ) -> bool:
        """
        通过 ServerChan 推送消息到微信
        
        Args:
            title: 消息标题（最多 256 字符）
            content: 消息内容（支持 Markdown 和 HTML）
            short: 消息摘要（可选，最多 64 字符）
            
        Returns:
            bool: 是否推送成功
        """
        if not self.serverchan_key:
            logger.error("✗ ServerChan 推送失败：未配置 SendKey")
            return False
        
        url = f"https://sctapi.ftqq.com/{self.serverchan_key}.send"
        
        # 构建请求数据
        data = {
            "title": title[:256],  # 限制标题长度
            "desp": content
        }
        
        if short:
            data["short"] = short[:64]
        
        # 带重试的推送
        for attempt in range(self.MAX_RETRIES):
            try:
                if attempt > 0:
                    wait_time = self.RETRY_DELAY * attempt
                    logger.warning(f"⏳ 第 {attempt} 次重试，等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                
                logger.info(f"📱 正在推送到微信... (尝试 {attempt + 1}/{self.MAX_RETRIES})")
                
                response = requests.post(
                    url, 
                    data=data, 
                    timeout=30
                )
                
                # 检查响应
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("code") == 0:
                        logger.info("✓ 微信推送成功！")
                        logger.debug(f"   推送ID: {result.get('data', {}).get('pushid')}")
                        return True
                    else:
                        error_msg = result.get("message", "未知错误")
                        logger.warning(f"⚠️ ServerChan 返回错误: {error_msg}")
                        
                        # 如果是配额问题，不再重试
                        if "quota" in error_msg.lower():
                            logger.error("✗ 推送配额已用完，停止重试")
                            break
                else:
                    logger.warning(f"⚠️ HTTP 错误: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⚠️ 推送超时")
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ 推送请求异常: {e}")
            except Exception as e:
                logger.error(f"✗ 推送异常: {e}")
        
        logger.error(f"✗ 微信推送失败（已重试 {self.MAX_RETRIES} 次）")
        return False
    
    def send_weekly_report(
        self, 
        html_content: str,
        report_date: Optional[datetime] = None
    ) -> bool:
        """
        推送周报到微信
        
        Args:
            html_content: 周报 HTML 内容
            report_date: 报告日期（可选，默认当前日期）
            
        Returns:
            bool: 是否推送成功
        """
        if report_date is None:
            report_date = datetime.now()
        
        # 构建标题
        date_str = report_date.strftime("%Y-%m-%d")
        title = f"📊 投资周报 {date_str}"
        
        # 构建摘要
        short = f"本周投资分析报告已生成"
        
        logger.info(f"📤 准备推送周报: {title}")
        
        return self.send_serverchan(
            title=title,
            content=html_content,
            short=short
        )
    
    def send_alert(
        self, 
        alert_type: str,
        message: str,
        details: Optional[str] = None
    ) -> bool:
        """
        推送告警消息
        
        Args:
            alert_type: 告警类型（如 "风险预警", "调仓提醒" 等）
            message: 告警消息
            details: 详细信息（可选）
            
        Returns:
            bool: 是否推送成功
        """
        title = f"⚠️ {alert_type}"
        
        content = f"## {alert_type}\n\n{message}"
        if details:
            content += f"\n\n### 详情\n\n{details}"
        
        content += f"\n\n---\n*发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return self.send_serverchan(
            title=title,
            content=content,
            short=message[:64]
        )


# 便捷函数
def push_to_wechat(
    title: str, 
    content: str, 
    serverchan_key: str
) -> bool:
    """
    便捷函数：推送消息到微信
    
    Args:
        title: 消息标题
        content: 消息内容
        serverchan_key: ServerChan SendKey
        
    Returns:
        bool: 是否推送成功
    """
    service = NotificationService(serverchan_key)
    return service.send_serverchan(title, content)
