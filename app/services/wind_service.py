"""Wind API Service - 封装 Wind 数据接口"""

import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from wind_linker import w

from app.core.logging import get_logger
from app.core.exceptions import (
    WindAPIError, 
    WindConnectionError, 
    WindDataError
)

logger = get_logger(__name__)

# Wind API 错误码映射
WIND_ERROR_CODES = {
    -40520007: "数据不存在",
    -40521001: "无权限访问",
    -40521002: "超出数据范围",
    -40522001: "参数错误",
    0: "成功"
}


class WindService:
    """Wind API 客户端服务"""
    
    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # 秒
    
    def __init__(self):
        """初始化 Wind 连接"""
        try:
            # wind-linker 会自动连接，不需要显式 start
            logger.info("✓ Wind API 服务初始化成功")
        except Exception as e:
            logger.error(f"✗ Wind API 初始化失败: {e}")
            raise WindConnectionError(str(e))
    
    def _get_error_message(self, error_code: int) -> str:
        """获取错误码对应的消息"""
        return WIND_ERROR_CODES.get(error_code, f"未知错误 (代码: {error_code})")
    
    def _retry_on_failure(self, func, *args, **kwargs):
        """带重试的函数调用"""
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_DELAY * (2 ** attempt)  # 指数退避
                    logger.warning(f"⚠️  第 {attempt + 1} 次尝试失败，{wait_time}秒后重试...")
                    time.sleep(wait_time)
        
        logger.error(f"✗ 已达到最大重试次数 ({self.MAX_RETRIES})")
        raise last_error
    
    @staticmethod
    def wind_to_df(res) -> pd.DataFrame:
        """
        将 Wind API 响应转换为 DataFrame
        
        Args:
            res: Wind API 响应对象
            
        Returns:
            pd.DataFrame: 包含时间索引的数据框
        """
        return pd.DataFrame(
            {res.Fields[i]: res.Data[i] for i in range(len(res.Fields))},
            index=pd.to_datetime(res.Times)
        )
    
    def get_stock_info(self, stock_code: str) -> Dict:
        """
        获取股票基本信息
        
        Args:
            stock_code: 股票代码（如 600519.SH）
            
        Returns:
            Dict: 包含股票名称等基本信息
        """
        try:
            logger.debug(f"获取股票信息: {stock_code}")
            res = w.wss(stock_code, "sec_name", "")
            
            if res.ErrorCode != 0:
                error_msg = self._get_error_message(res.ErrorCode)
                logger.warning(f"⚠️  获取股票信息失败: {stock_code} - {error_msg}")
                return {"stock_code": stock_code, "name": None}
            
            name = res.Data[0][0] if res.Data and res.Data[0] else None
            logger.debug(f"✓ {stock_code}: {name}")
            
            return {
                "stock_code": stock_code,
                "name": name
            }
        except Exception as e:
            logger.error(f"✗ 获取股票信息异常: {stock_code} - {e}")
            return {"stock_code": stock_code, "name": None}
    
    def get_stock_data(
        self, 
        stock_code: str, 
        days: int = 90,
        fields: str = "close,volume,pe_ttm,turn"
    ) -> pd.DataFrame:
        """
        获取股票历史行情数据
        
        Args:
            stock_code: 股票代码
            days: 获取最近多少天的数据
            fields: 需要获取的字段（逗号分隔）
            
        Returns:
            pd.DataFrame: 历史行情数据
        """
        try:
            end_date = datetime.today().strftime("%Y-%m-%d")
            start_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            logger.debug(f"获取行情数据: {stock_code} ({start_date} ~ {end_date})")
            
            res = w.wsd(
                stock_code,
                fields,
                start_date,
                end_date,
                "PriceAdj=F"  # 不复权
            )
            
            if res.ErrorCode != 0:
                error_msg = self._get_error_message(res.ErrorCode)
                logger.warning(f"⚠️  获取行情数据失败: {stock_code} - {error_msg}")
                return pd.DataFrame()
            
            df = self.wind_to_df(res)
            logger.debug(f"✓ {stock_code}: 获取 {len(df)} 条行情数据")
            
            return df
        except Exception as e:
            logger.error(f"✗ 获取行情数据异常: {stock_code} - {e}")
            return pd.DataFrame()
    
    def get_latest_price(self, stock_code: str) -> Optional[float]:
        """
        获取股票最新价格
        
        Args:
            stock_code: 股票代码
            
        Returns:
            float: 最新价格，失败返回 None
        """
        try:
            logger.debug(f"获取最新价格: {stock_code}")
            
            res = w.wsq(stock_code, "rt_last")
            
            if res.ErrorCode != 0:
                error_msg = self._get_error_message(res.ErrorCode)
                logger.warning(f"⚠️  获取最新价格失败: {stock_code} - {error_msg}")
                return None
            
            price = res.Data[0][0] if res.Data and res.Data[0] else None
            logger.debug(f"✓ {stock_code}: ¥{price}")
            
            return price
        except Exception as e:
            logger.error(f"✗ 获取最新价格异常: {stock_code} - {e}")
            return None
    
    def get_technical_indicators(self, stock_code: str, days: int = 90) -> Dict:
        """
        获取技术指标（使用 Wind API 直接计算）
        
        Args:
            stock_code: 股票代码
            days: 获取最近多少天的数据
            
        Returns:
            Dict: 包含所有技术指标
        """
        try:
            end_date = datetime.today().strftime("%Y-%m-%d")
            start_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            logger.debug(f"获取技术指标: {stock_code}")
            
            indicators = {}
            
            # MA 指标 (5, 10, 20, 30, 250)
            for n in [5, 10, 20, 30, 250]:
                try:
                    r = w.wsd(stock_code, "MA", start_date, end_date, f"MA_N={n}")
                    if r.ErrorCode == 0 and r.Data and len(r.Data[0]) > 0:
                        indicators[f"MA{n}"] = r.Data[0][-1]  # 最新值
                    else:
                        indicators[f"MA{n}"] = None
                except:
                    indicators[f"MA{n}"] = None
            
            # RSI 指标 (6, 12, 24)
            for n in [6, 12, 24]:
                try:
                    r = w.wsd(stock_code, "RSI", start_date, end_date, f"RSI_N={n}")
                    if r.ErrorCode == 0 and r.Data and len(r.Data[0]) > 0:
                        indicators[f"RSI{n}"] = r.Data[0][-1]
                    else:
                        indicators[f"RSI{n}"] = None
                except:
                    indicators[f"RSI{n}"] = None
            
            # MACD 指标
            try:
                r = w.wsd(stock_code, "MACD", start_date, end_date, "MACD_L=26;MACD_S=12;MACD_N=9;MACD_IO=1")
                if r.ErrorCode == 0 and r.Data and len(r.Data) >= 3:
                    indicators["MACD_DIF"] = r.Data[0][-1] if len(r.Data[0]) > 0 else None  # DIF
                    indicators["MACD_DEA"] = r.Data[1][-1] if len(r.Data[1]) > 0 else None  # DEA
                    indicators["MACD"] = r.Data[2][-1] if len(r.Data[2]) > 0 else None      # MACD
                else:
                    indicators["MACD_DIF"] = None
                    indicators["MACD_DEA"] = None
                    indicators["MACD"] = None
            except:
                indicators["MACD_DIF"] = None
                indicators["MACD_DEA"] = None
                indicators["MACD"] = None
            
            # BOLL 指标
            try:
                r = w.wsd(stock_code, "BOLL", start_date, end_date, "BOLL_N=20;BOLL_Width=2;BOLL_IO=1")
                if r.ErrorCode == 0 and r.Data and len(r.Data) >= 3:
                    indicators["BOLL_upper"] = r.Data[0][-1] if len(r.Data[0]) > 0 else None  # 上轨
                    indicators["BOLL_mid"] = r.Data[1][-1] if len(r.Data[1]) > 0 else None    # 中轨
                    indicators["BOLL_lower"] = r.Data[2][-1] if len(r.Data[2]) > 0 else None  # 下轨
                else:
                    indicators["BOLL_upper"] = None
                    indicators["BOLL_mid"] = None
                    indicators["BOLL_lower"] = None
            except:
                indicators["BOLL_upper"] = None
                indicators["BOLL_mid"] = None
                indicators["BOLL_lower"] = None
            
            # 统计成功获取的指标数量
            valid_count = sum(1 for v in indicators.values() if v is not None)
            logger.debug(f"✓ {stock_code}: 技术指标获取完成 ({valid_count}/{len(indicators)} 有效)")
            return indicators
        
        except Exception as e:
            logger.error(f"✗ 获取技术指标失败: {stock_code} - {e}")
            return {}
    
    def get_stock_complete_data(self, stock_code: str, days: int = 90) -> Dict:
        """
        获取股票的完整数据（基本信息 + 历史行情 + 技术指标）
        
        Args:
            stock_code: 股票代码
            days: 获取最近多少天的数据
            
        Returns:
            Dict: 包含基本信息、历史行情和技术指标的完整数据
        """
        logger.info(f"📈 获取完整数据: {stock_code}")
        
        # 获取基本信息
        info = self.get_stock_info(stock_code)
        
        # 获取历史行情
        df = self.get_stock_data(stock_code, days)
        
        if df.empty:
            logger.warning(f"⚠️  {stock_code} 没有行情数据")
            return {
                "stock_code": stock_code,
                "name": info.get("name"),
                "data": None,
                "latest_price": None,
                "volume": None,
                "pe_ttm": None,
                "turnover": None,
                "indicators": {}
            }
        
        # 提取最新数据
        latest_price = df["CLOSE"].iloc[-1] if "CLOSE" in df else None
        volume = df["VOLUME"].iloc[-1] if "VOLUME" in df else None
        pe_ttm = df["PE_TTM"].iloc[-1] if "PE_TTM" in df else None
        turnover = df["TURN"].iloc[-1] if "TURN" in df else None
        
        # 获取技术指标
        indicators = self.get_technical_indicators(stock_code, days)
        
        result = {
            "stock_code": stock_code,
            "name": info.get("name"),
            "data": df,
            "latest_price": latest_price,
            "volume": volume,
            "pe_ttm": pe_ttm,
            "turnover": turnover,
            "indicators": indicators
        }
        
        logger.info(f"   ✓ {result['name'] or stock_code}: ¥{latest_price:.2f}, {len(df)}条数据, {len(indicators)}个指标")
        
        return result
    
    def close(self):
        """关闭 Wind 连接"""
        try:
            # wind-linker 不需要显式关闭
            logger.info("✓ Wind API 服务关闭")
        except Exception as e:
            logger.error(f"关闭 Wind API 服务失败: {e}")
