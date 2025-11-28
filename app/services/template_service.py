"""Template Service - Jinja2 模板渲染服务"""

from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TemplateService:
    """模板渲染服务类"""
    
    def __init__(self, template_dir: str = "templates"):
        """
        初始化模板服务
        
        Args:
            template_dir: 模板目录路径
        """
        self.template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self._register_filters()
        logger.info(f"✓ 模板服务初始化成功，模板目录: {self.template_dir}")
    
    def _register_filters(self):
        """注册自定义过滤器"""
        # 格式化金额
        self.env.filters['format_price'] = lambda x: f"{x:,.2f}" if x is not None else "N/A"
        
        # 格式化百分比
        self.env.filters['format_percent'] = lambda x: f"{x:+.2f}%" if x is not None else "N/A"
        
        # 格式化日期
        self.env.filters['format_date'] = lambda x: x.strftime('%Y年%m月%d日') if x else ""
        
        # 格式化数字（带符号）
        self.env.filters['format_number'] = lambda x: f"{x:+,.2f}" if x is not None else "N/A"
        
        # 判断涨跌
        self.env.filters['is_positive'] = lambda x: x > 0 if x is not None else False
        self.env.filters['is_negative'] = lambda x: x < 0 if x is not None else False
        
        logger.info("✓ 自定义过滤器注册完成")
    
    def render_weekly_report(self, data: Dict) -> str:
        """
        渲染周报 HTML
        
        Args:
            data: 包含所有周报数据的字典，包括：
                - report_data: 原始数据（持仓、行情等）
                - analysis: LLM 生成的分析内容
                
        Returns:
            str: 渲染后的 HTML 字符串
        """
        try:
            logger.info("开始渲染周报 HTML...")
            
            # 加载模板
            template = self.env.get_template('weekly_report.html')
            
            # 渲染模板
            html = template.render(**data)
            
            logger.info(f"✓ 周报 HTML 渲染成功，长度: {len(html)} 字符")
            
            return html
        
        except Exception as e:
            logger.error(f"渲染周报 HTML 失败: {e}", exc_info=True)
            return ""
    
    def save_html(self, html: str, output_path: str) -> bool:
        """
        保存 HTML 到文件
        
        Args:
            html: HTML 内容
            output_path: 输出文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"✓ HTML 已保存到: {output_file}")
            return True
        
        except Exception as e:
            logger.error(f"保存 HTML 失败: {e}")
            return False
