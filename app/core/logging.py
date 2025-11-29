"""
Centralized Logging Configuration - 统一日志配置

提供统一的日志格式、级别控制和进度提示功能
"""

import logging
import sys
from typing import Optional
from datetime import datetime


# 日志格式配置
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 简化格式（用于控制台）
CONSOLE_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
CONSOLE_DATE_FORMAT = "%H:%M:%S"


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器（仅用于控制台）"""
    
    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    enable_color: bool = True
) -> None:
    """
    配置全局日志
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径（可选）
        enable_color: 是否启用颜色输出
    """
    # 获取根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if enable_color and sys.stdout.isatty():
        console_formatter = ColoredFormatter(CONSOLE_FORMAT, CONSOLE_DATE_FORMAT)
    else:
        console_formatter = logging.Formatter(CONSOLE_FORMAT, CONSOLE_DATE_FORMAT)
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（可选）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志器
    
    Args:
        name: 日志器名称（通常使用 __name__）
        
    Returns:
        logging.Logger: 日志器实例
    """
    return logging.getLogger(name)


class ProgressTracker:
    """进度跟踪器 - 用于显示关键步骤的进度"""
    
    def __init__(self, logger: logging.Logger, total_steps: int, task_name: str = "任务"):
        """
        初始化进度跟踪器
        
        Args:
            logger: 日志器
            total_steps: 总步骤数
            task_name: 任务名称
        """
        self.logger = logger
        self.total_steps = total_steps
        self.task_name = task_name
        self.current_step = 0
        self.start_time = datetime.now()
    
    def start(self) -> None:
        """开始任务"""
        self.start_time = datetime.now()
        self.current_step = 0
        self.logger.info(f"{'=' * 60}")
        self.logger.info(f"🚀 开始{self.task_name}（共 {self.total_steps} 步）")
        self.logger.info(f"{'=' * 60}")
    
    def step(self, step_name: str, step_num: Optional[int] = None) -> None:
        """
        记录步骤进度
        
        Args:
            step_name: 步骤名称
            step_num: 步骤编号（可选，默认自动递增）
        """
        if step_num is not None:
            self.current_step = step_num
        else:
            self.current_step += 1
        
        progress = f"[{self.current_step}/{self.total_steps}]"
        self.logger.info(f"\n📌 步骤 {progress}: {step_name}")
    
    def complete(self, success: bool = True, message: str = "") -> None:
        """
        完成任务
        
        Args:
            success: 是否成功
            message: 完成消息
        """
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        self.logger.info(f"\n{'=' * 60}")
        if success:
            self.logger.info(f"✅ {self.task_name}完成！耗时: {elapsed:.1f} 秒")
        else:
            self.logger.error(f"❌ {self.task_name}失败！耗时: {elapsed:.1f} 秒")
        
        if message:
            self.logger.info(f"   {message}")
        self.logger.info(f"{'=' * 60}\n")
    
    def sub_progress(self, current: int, total: int, item_name: str = "") -> None:
        """
        显示子进度
        
        Args:
            current: 当前进度
            total: 总数
            item_name: 项目名称
        """
        percent = (current / total * 100) if total > 0 else 0
        bar_length = 20
        filled = int(bar_length * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        
        msg = f"   [{bar}] {current}/{total} ({percent:.0f}%)"
        if item_name:
            msg += f" - {item_name}"
        
        self.logger.info(msg)
