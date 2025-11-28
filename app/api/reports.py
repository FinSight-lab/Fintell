"""Reports API - 周报生成接口"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.services.data_service import DataService
from app.services.llm_service import LLMService
from app.services.template_service import TemplateService
from app.models import Report

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/weekly")
async def generate_weekly_report(
    portfolio_id: int = Query(1, description="持仓组合ID"),
    skip_push: bool = Query(False, description="是否跳过推送"),
    save_to_db: bool = Query(True, description="是否保存到数据库"),
    db: Session = Depends(get_db)
):
    """
    生成周报
    
    流程：
    1. 从数据库加载持仓数据
    2. 调用 Wind API 获取最新行情和历史数据
    3. 计算技术指标
    4. 调用 LLM 生成结构化分析（JSON 格式）
    5. 使用 Jinja2 渲染 HTML 模板
    6. 保存周报到数据库（可选）
    7. 推送到微信（可选）
    8. 返回生成的 HTML 和推送状态
    """
    try:
        logger.info("=" * 80)
        logger.info("开始生成周报")
        logger.info("=" * 80)
        logger.info(f"参数: portfolio_id={portfolio_id}, skip_push={skip_push}, save_to_db={save_to_db}")
        
        # 1. 获取数据
        logger.info("\n📊 步骤 1/5: 获取数据...")
        data_service = DataService(db)
        report_data = data_service.get_weekly_report_data(portfolio_id)
        
        if not report_data:
            raise HTTPException(status_code=404, detail="无法获取周报数据")
        
        logger.info(f"✓ 数据获取完成，持仓数量: {len(report_data.get('holdings', []))}")
        
        # 2. LLM 分析
        logger.info("\n🤖 步骤 2/5: LLM 分析...")
        llm_service = LLMService(
            api_url=settings.LLM_API_URL,
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL
        )
        
        analysis = llm_service.generate_weekly_analysis(report_data)
        
        if not analysis:
            raise HTTPException(status_code=500, detail="LLM 分析失败")
        
        logger.info("✓ LLM 分析完成")
        
        # 3. 合并数据
        logger.info("\n📦 步骤 3/5: 合并数据...")
        complete_data = {
            **report_data,
            'analysis': analysis
        }
        
        # 4. 渲染 HTML
        logger.info("\n🎨 步骤 4/5: 渲染 HTML...")
        template_service = TemplateService()
        html = template_service.render_weekly_report(complete_data)
        
        if not html:
            raise HTTPException(status_code=500, detail="HTML 渲染失败")
        
        logger.info(f"✓ HTML 渲染完成，长度: {len(html)} 字符")
        
        # 5. 保存到数据库
        report_id = None
        if save_to_db:
            logger.info("\n💾 步骤 5/5: 保存到数据库...")
            try:
                report = Report(
                    portfolio_id=portfolio_id,
                    report_type="weekly",
                    report_date=datetime.now().date(),
                    content=analysis,  # LLM 生成的 JSON
                    html_content=html,
                    pushed=False
                )
                db.add(report)
                db.commit()
                db.refresh(report)
                report_id = report.id
                logger.info(f"✓ 周报已保存到数据库，ID: {report_id}")
            except Exception as e:
                logger.error(f"保存到数据库失败: {e}")
                db.rollback()
        
        # 6. 推送（暂时跳过，Task 5 实现）
        pushed = False
        if not skip_push:
            logger.info("\n📱 推送功能尚未实现，跳过...")
        
        # 关闭服务
        data_service.close()
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ 周报生成完成！")
        logger.info("=" * 80)
        
        return {
            "success": True,
            "report_id": report_id,
            "html": html,
            "html_length": len(html),
            "pushed": pushed,
            "analysis_summary": {
                "core_viewpoint": analysis.get("core_viewpoint", "")[:100] + "...",
                "stock_count": len(analysis.get("stock_analysis", [])),
                "action_count": len(analysis.get("action_plan", []))
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成周报失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成周报失败: {str(e)}")


@router.get("/latest")
async def get_latest_report(
    portfolio_id: int = Query(1, description="持仓组合ID"),
    db: Session = Depends(get_db)
):
    """获取最新周报"""
    try:
        report = db.query(Report).filter(
            Report.portfolio_id == portfolio_id,
            Report.report_type == "weekly"
        ).order_by(Report.created_at.desc()).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="未找到周报")
        
        return {
            "id": report.id,
            "report_date": report.report_date,
            "created_at": report.created_at,
            "html_content": report.html_content,
            "pushed": report.pushed
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取最新周报失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{report_id}")
async def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """获取指定周报"""
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="周报不存在")
        
        return {
            "id": report.id,
            "portfolio_id": report.portfolio_id,
            "report_type": report.report_type,
            "report_date": report.report_date,
            "created_at": report.created_at,
            "html_content": report.html_content,
            "content": report.content,
            "pushed": report.pushed
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取周报失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
