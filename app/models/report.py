"""Report model"""

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Report(Base):
    """周报模型"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, comment="所属组合ID")
    report_type = Column(String(20), nullable=False, default="weekly", comment="报告类型（weekly/daily）")
    report_date = Column(Date, nullable=False, index=True, comment="报告日期")
    
    # 报告内容
    content = Column(JSON, nullable=True, comment="结构化内容（LLM 生成的 JSON）")
    html_content = Column(Text, nullable=True, comment="HTML 格式内容")
    
    # 推送状态
    pushed = Column(Boolean, default=False, comment="是否已推送")
    push_time = Column(DateTime(timezone=True), nullable=True, comment="推送时间")
    push_result = Column(Text, nullable=True, comment="推送结果")
    
    # 元数据
    generation_time = Column(Integer, nullable=True, comment="生成耗时（秒）")
    llm_tokens = Column(Integer, nullable=True, comment="LLM 使用的 token 数")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    portfolio = relationship("Portfolio", back_populates="reports")

    def __repr__(self):
        return f"<Report(id={self.id}, type='{self.report_type}', date={self.report_date}, pushed={self.pushed})>"
