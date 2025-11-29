"""
Custom Exceptions - 自定义异常类

提供统一的异常处理和错误分类
"""

from typing import Optional, Dict, Any


class PortfolioManagerError(Exception):
    """基础异常类"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


# ============================================================================
# 数据相关异常
# ============================================================================

class DataError(PortfolioManagerError):
    """数据相关错误的基类"""
    pass


class PortfolioNotFoundError(DataError):
    """持仓组合不存在"""
    
    def __init__(self, portfolio_id: int):
        super().__init__(
            message=f"持仓组合不存在: ID={portfolio_id}",
            error_code="PORTFOLIO_NOT_FOUND",
            details={"portfolio_id": portfolio_id}
        )


class PositionNotFoundError(DataError):
    """持仓不存在"""
    
    def __init__(self, position_id: Optional[int] = None, stock_code: Optional[str] = None):
        details = {}
        if position_id:
            details["position_id"] = position_id
        if stock_code:
            details["stock_code"] = stock_code
        
        super().__init__(
            message=f"持仓不存在: {position_id or stock_code}",
            error_code="POSITION_NOT_FOUND",
            details=details
        )


class EmptyPortfolioError(DataError):
    """持仓组合为空"""
    
    def __init__(self, portfolio_id: int):
        super().__init__(
            message=f"持仓组合为空: ID={portfolio_id}",
            error_code="EMPTY_PORTFOLIO",
            details={"portfolio_id": portfolio_id}
        )


class InvalidStockCodeError(DataError):
    """无效的股票代码"""
    
    def __init__(self, stock_code: str, reason: str = "格式不正确"):
        super().__init__(
            message=f"无效的股票代码: {stock_code} ({reason})",
            error_code="INVALID_STOCK_CODE",
            details={"stock_code": stock_code, "reason": reason}
        )


# ============================================================================
# 外部服务异常
# ============================================================================

class ExternalServiceError(PortfolioManagerError):
    """外部服务错误的基类"""
    pass


class WindAPIError(ExternalServiceError):
    """Wind API 错误"""
    
    def __init__(
        self, 
        message: str, 
        error_code_wind: Optional[int] = None,
        stock_code: Optional[str] = None
    ):
        details = {}
        if error_code_wind is not None:
            details["wind_error_code"] = error_code_wind
        if stock_code:
            details["stock_code"] = stock_code
        
        super().__init__(
            message=f"Wind API 错误: {message}",
            error_code="WIND_API_ERROR",
            details=details
        )


class WindConnectionError(WindAPIError):
    """Wind API 连接错误"""
    
    def __init__(self, message: str = "无法连接到 Wind API"):
        super().__init__(message)
        self.error_code = "WIND_CONNECTION_ERROR"


class WindDataError(WindAPIError):
    """Wind API 数据获取错误"""
    
    def __init__(self, stock_code: str, message: str = "获取数据失败"):
        super().__init__(
            message=f"{stock_code}: {message}",
            stock_code=stock_code
        )
        self.error_code = "WIND_DATA_ERROR"


class LLMAPIError(ExternalServiceError):
    """LLM API 错误"""
    
    def __init__(
        self, 
        message: str,
        status_code: Optional[int] = None,
        retry_count: int = 0
    ):
        details = {"retry_count": retry_count}
        if status_code:
            details["status_code"] = status_code
        
        super().__init__(
            message=f"LLM API 错误: {message}",
            error_code="LLM_API_ERROR",
            details=details
        )


class LLMResponseParseError(LLMAPIError):
    """LLM 响应解析错误"""
    
    def __init__(self, message: str = "无法解析 LLM 响应"):
        super().__init__(message)
        self.error_code = "LLM_RESPONSE_PARSE_ERROR"


class NotificationError(ExternalServiceError):
    """通知推送错误"""
    
    def __init__(
        self, 
        channel: str, 
        message: str,
        retry_count: int = 0
    ):
        super().__init__(
            message=f"推送失败 ({channel}): {message}",
            error_code="NOTIFICATION_ERROR",
            details={"channel": channel, "retry_count": retry_count}
        )


# ============================================================================
# 业务逻辑异常
# ============================================================================

class BusinessError(PortfolioManagerError):
    """业务逻辑错误的基类"""
    pass


class ReportGenerationError(BusinessError):
    """报告生成错误"""
    
    def __init__(self, step: str, message: str):
        super().__init__(
            message=f"报告生成失败 ({step}): {message}",
            error_code="REPORT_GENERATION_ERROR",
            details={"step": step}
        )


class TemplateRenderError(BusinessError):
    """模板渲染错误"""
    
    def __init__(self, template_name: str, message: str):
        super().__init__(
            message=f"模板渲染失败 ({template_name}): {message}",
            error_code="TEMPLATE_RENDER_ERROR",
            details={"template_name": template_name}
        )


class IndicatorCalculationError(BusinessError):
    """技术指标计算错误"""
    
    def __init__(self, indicator: str, stock_code: str, message: str):
        super().__init__(
            message=f"指标计算失败 ({indicator}): {message}",
            error_code="INDICATOR_CALCULATION_ERROR",
            details={"indicator": indicator, "stock_code": stock_code}
        )


# ============================================================================
# 辅助函数
# ============================================================================

def handle_exception(
    exception: Exception,
    logger,
    context: str = "",
    reraise: bool = True
) -> Optional[Dict[str, Any]]:
    """
    统一异常处理函数
    
    Args:
        exception: 异常对象
        logger: 日志器
        context: 上下文信息
        reraise: 是否重新抛出异常
        
    Returns:
        异常信息字典（如果不重新抛出）
    """
    if isinstance(exception, PortfolioManagerError):
        # 自定义异常
        logger.error(f"[{exception.error_code}] {context}: {exception.message}")
        if exception.details:
            logger.error(f"  详情: {exception.details}")
        
        if reraise:
            raise exception
        return exception.to_dict()
    else:
        # 未知异常
        logger.error(f"未知错误 {context}: {exception}", exc_info=True)
        
        if reraise:
            raise PortfolioManagerError(
                message=str(exception),
                error_code="UNKNOWN_ERROR",
                details={"original_type": type(exception).__name__}
            )
        return {
            "error_code": "UNKNOWN_ERROR",
            "message": str(exception),
            "details": {"original_type": type(exception).__name__}
        }
