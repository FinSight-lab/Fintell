"""Reports API - 周报生成接口"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.core.logging import get_logger, ProgressTracker
from app.core.exceptions import (
    PortfolioManagerError,
    PortfolioNotFoundError,
    EmptyPortfolioError,
    LLMAPIError,
    TemplateRenderError,
    ReportGenerationError
)
from app.services.data_service import DataService
from app.services.llm_service import LLMService
from app.services.template_service import TemplateService
from app.models import Report

logger = get_logger(__name__)

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
    # 创建进度跟踪器
    progress = ProgressTracker(logger, total_steps=5, task_name="周报生成")
    progress.start()
    
    data_service = None
    
    try:
        logger.info(f"参数: portfolio_id={portfolio_id}, skip_push={skip_push}, save_to_db={save_to_db}")
        
        # 步骤 1: 获取数据
        progress.step("获取持仓和行情数据")
        data_service = DataService(db)
        report_data = data_service.get_weekly_report_data(portfolio_id)
        
        if not report_data:
            raise ReportGenerationError("数据获取", "无法获取周报数据")
        
        holdings_count = len(report_data.get('holdings', []))
        logger.info(f"   ✓ 数据获取完成，持仓数量: {holdings_count}")
        
        # 步骤 2: LLM 分析
        progress.step("LLM 智能分析")
        llm_service = LLMService(
            api_url=settings.LLM_API_URL,
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL
        )
        
        analysis = llm_service.generate_weekly_analysis(report_data)
        
        if not analysis:
            raise ReportGenerationError("LLM分析", "LLM 返回空结果")
        
        # 步骤 3: 合并数据
        progress.step("合并数据")
        complete_data = {
            **report_data,
            'analysis': analysis
        }
        logger.info("   ✓ 数据合并完成")
        
        # 步骤 4: 渲染 HTML
        progress.step("渲染 HTML 模板")
        template_service = TemplateService()
        html = template_service.render_weekly_report(complete_data)
        
        if not html:
            raise ReportGenerationError("HTML渲染", "渲染结果为空")
        
        # 步骤 5: 保存和推送
        progress.step("保存和推送")
        report_id = None
        if save_to_db:
            try:
                report = Report(
                    portfolio_id=portfolio_id,
                    report_type="weekly",
                    report_date=datetime.now().date(),
                    content=analysis,
                    html_content=html,
                    pushed=False
                )
                db.add(report)
                db.commit()
                db.refresh(report)
                report_id = report.id
                logger.info(f"   ✓ 周报已保存，ID: {report_id}")
            except Exception as e:
                logger.error(f"   ⚠️ 保存到数据库失败: {e}")
                db.rollback()
        
        # 推送（暂时跳过）
        pushed = False
        if not skip_push:
            logger.info("   ⏭️ 推送功能尚未实现，跳过")
        
        # 完成
        progress.complete(
            success=True, 
            message=f"报告ID: {report_id}, HTML长度: {len(html)} 字符"
        )
        
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
    
    except PortfolioNotFoundError as e:
        progress.complete(success=False, message=str(e))
        raise HTTPException(status_code=404, detail=e.to_dict())
    
    except EmptyPortfolioError as e:
        progress.complete(success=False, message=str(e))
        raise HTTPException(status_code=400, detail=e.to_dict())
    
    except LLMAPIError as e:
        progress.complete(success=False, message=str(e))
        raise HTTPException(status_code=502, detail=e.to_dict())
    
    except TemplateRenderError as e:
        progress.complete(success=False, message=str(e))
        raise HTTPException(status_code=500, detail=e.to_dict())
    
    except PortfolioManagerError as e:
        progress.complete(success=False, message=str(e))
        raise HTTPException(status_code=500, detail=e.to_dict())
    
    except HTTPException:
        raise
    
    except Exception as e:
        progress.complete(success=False, message=str(e))
        logger.error(f"生成周报失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={
            "error_code": "UNKNOWN_ERROR",
            "message": f"生成周报失败: {str(e)}"
        })
    
    finally:
        # 确保关闭服务
        if data_service:
            try:
                data_service.close()
            except Exception:
                pass


@router.get("/latest")
async def get_latest_report(
    portfolio_id: int = Query(1, description="持仓组合ID"),
    db: Session = Depends(get_db)
):
    """获取最新周报"""
    try:
        logger.debug(f"获取最新周报: portfolio_id={portfolio_id}")
        
        report = db.query(Report).filter(
            Report.portfolio_id == portfolio_id,
            Report.report_type == "weekly"
        ).order_by(Report.created_at.desc()).first()
        
        if not report:
            logger.warning(f"未找到周报: portfolio_id={portfolio_id}")
            raise HTTPException(status_code=404, detail={
                "error_code": "REPORT_NOT_FOUND",
                "message": "未找到周报"
            })
        
        logger.debug(f"✓ 获取周报成功: ID={report.id}")
        
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
        logger.error(f"✗ 获取最新周报失败: {e}")
        raise HTTPException(status_code=500, detail={
            "error_code": "DATABASE_ERROR",
            "message": str(e)
        })


@router.get("/{report_id}")
async def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """获取指定周报"""
    try:
        logger.debug(f"获取周报: ID={report_id}")
        
        report = db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            logger.warning(f"周报不存在: ID={report_id}")
            raise HTTPException(status_code=404, detail={
                "error_code": "REPORT_NOT_FOUND",
                "message": f"周报不存在: ID={report_id}"
            })
        
        logger.debug(f"✓ 获取周报成功: ID={report.id}")
        
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
        logger.error(f"✗ 获取周报失败: {e}")
        raise HTTPException(status_code=500, detail={
            "error_code": "DATABASE_ERROR",
            "message": str(e)
        })
