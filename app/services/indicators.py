"""Technical Indicators Calculation Service - 技术指标计算服务"""

import pandas as pd
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def calc_ma(series: pd.Series, windows: list = None) -> Dict[str, Optional[float]]:
    """
    计算移动平均线（Moving Average）
    
    Args:
        series: 价格序列（通常是收盘价）
        windows: 计算周期列表，默认 [5, 10, 20, 30, 250]
        
    Returns:
        Dict: MA5, MA10, MA20, MA30, MA250
    """
    if windows is None:
        windows = [5, 10, 20, 30, 250]
    
    try:
        result = {}
        for w in windows:
            ma_value = series.rolling(w).mean().iloc[-1]
            result[f"MA{w}"] = ma_value if pd.notna(ma_value) else None
        
        logger.debug(f"MA 计算完成: {result}")
        return result
    except Exception as e:
        logger.error(f"MA 计算失败: {e}")
        return {f"MA{w}": None for w in windows}


def calc_rsi(close: pd.Series, periods: list = None) -> Dict[str, Optional[float]]:
    """
    计算相对强弱指标（Relative Strength Index）
    
    Args:
        close: 收盘价序列
        periods: 计算周期列表，默认 [6, 12, 24]
        
    Returns:
        Dict: RSI6, RSI12, RSI24
    """
    if periods is None:
        periods = [6, 12, 24]
    
    try:
        close = close.dropna()
        if len(close) < max(periods):
            logger.warning(f"数据不足，无法计算 RSI（需要至少 {max(periods)} 条数据）")
            return {f"RSI{p}": None for p in periods}

        rsi_values = {}
        diff = close.diff()

        gain = diff.clip(lower=0)
        loss = -diff.clip(upper=0)

        for p in periods:
            avg_gain = gain.rolling(p).mean()
            avg_loss = loss.rolling(p).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            rsi_value = rsi.iloc[-1]
            rsi_values[f"RSI{p}"] = rsi_value if pd.notna(rsi_value) else None

        logger.debug(f"RSI 计算完成: {rsi_values}")
        return rsi_values
    except Exception as e:
        logger.error(f"RSI 计算失败: {e}")
        return {f"RSI{p}": None for p in periods}


def calc_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Optional[float]]:
    """
    计算 MACD 指标（Moving Average Convergence Divergence）
    
    Args:
        close: 收盘价序列
        fast: 快线周期，默认 12
        slow: 慢线周期，默认 26
        signal: 信号线周期，默认 9
        
    Returns:
        Dict: MACD_DIF, MACD_DEA, MACD
    """
    try:
        ema_fast = close.ewm(span=fast).mean()
        ema_slow = close.ewm(span=slow).mean()
        dif = ema_fast - ema_slow
        dea = dif.ewm(span=signal).mean()
        macd = (dif - dea) * 2

        result = {
            "MACD_DIF": dif.iloc[-1] if pd.notna(dif.iloc[-1]) else None,
            "MACD_DEA": dea.iloc[-1] if pd.notna(dea.iloc[-1]) else None,
            "MACD": macd.iloc[-1] if pd.notna(macd.iloc[-1]) else None
        }
        
        logger.debug(f"MACD 计算完成: {result}")
        return result
    except Exception as e:
        logger.error(f"MACD 计算失败: {e}")
        return {"MACD_DIF": None, "MACD_DEA": None, "MACD": None}


def calc_boll(close: pd.Series, n: int = 20, k: int = 2) -> Dict[str, Optional[float]]:
    """
    计算布林带（Bollinger Bands）
    
    Args:
        close: 收盘价序列
        n: 计算周期，默认 20
        k: 标准差倍数，默认 2
        
    Returns:
        Dict: BOLL_mid, BOLL_upper, BOLL_lower
    """
    try:
        mid = close.rolling(n).mean().iloc[-1]
        std = close.rolling(n).std().iloc[-1]
        
        if pd.notna(mid) and pd.notna(std):
            upper = mid + k * std
            lower = mid - k * std
            result = {
                "BOLL_mid": mid,
                "BOLL_upper": upper,
                "BOLL_lower": lower
            }
        else:
            result = {
                "BOLL_mid": None,
                "BOLL_upper": None,
                "BOLL_lower": None
            }
        
        logger.debug(f"BOLL 计算完成: {result}")
        return result
    except Exception as e:
        logger.error(f"BOLL 计算失败: {e}")
        return {"BOLL_mid": None, "BOLL_upper": None, "BOLL_lower": None}


def calculate_all_indicators(close: pd.Series) -> Dict[str, Optional[float]]:
    """
    计算所有技术指标
    
    Args:
        close: 收盘价序列
        
    Returns:
        Dict: 包含所有技术指标的字典
    """
    logger.info("开始计算技术指标...")
    
    indicators = {}
    
    # MA
    indicators.update(calc_ma(close))
    
    # RSI
    indicators.update(calc_rsi(close))
    
    # MACD
    indicators.update(calc_macd(close))
    
    # BOLL
    indicators.update(calc_boll(close))
    
    logger.info(f"✓ 技术指标计算完成，共 {len(indicators)} 个指标")
    
    return indicators
