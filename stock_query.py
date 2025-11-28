from wind_linker import w
import pandas as pd
from datetime import datetime, timedelta

# 技术指标计算 ------------------------------------------------------------------

def wind_to_df(res):
    return pd.DataFrame(
        {res.Fields[i]: res.Data[i] for i in range(len(res.Fields))},
        index=pd.to_datetime(res.Times)
    )

def calc_ma(series):
    windows = [5, 10, 20, 30, 250]
    return {f"MA{w}": series.rolling(w).mean().iloc[-1] for w in windows}


def calc_rsi(close):
    periods = [6, 12, 24]
    close = close.dropna()
    if len(close) < max(periods):
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
        rsi_values[f"RSI{p}"] = rsi.iloc[-1]

    return rsi_values


def calc_macd(close, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast).mean()
    ema_slow = close.ewm(span=slow).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal).mean()
    macd = (dif - dea) * 2

    return {
        "MACD_DIF": dif.iloc[-1],
        "MACD_DEA": dea.iloc[-1],
        "MACD": macd.iloc[-1]
    }


def calc_boll(close, n=20, k=2):
    mid = close.rolling(n).mean().iloc[-1]
    std = close.rolling(n).std().iloc[-1]
    upper = mid + k * std
    lower = mid - k * std
    return {"BOLL_mid": mid, "BOLL_upper": upper, "BOLL_lower": lower}

def get_stock_recent_info(stocks):
    """
    输入：股票代码 或 股票代码列表
    输出：每只股票最近三个月的指标
    """

    if isinstance(stocks, str):
        stocks = [stocks]

    end_date = datetime.today().strftime("%Y-%m-%d")
    start_date = (datetime.today() - timedelta(days=90)).strftime("%Y-%m-%d")

    results = []

    for stock in stocks:
        # -------- 获取行情（收盘价 + 成交量） --------
        res = w.wsd(
            stock,
            "close,volume,pe_ttm,turn",
            start_date,
            end_date,
            "PriceAdj=F"
        )
        df = wind_to_df(res)
        close = df["CLOSE"]
        volume = df["VOLUME"]
        pe = df["PE_TTM"].iloc[-1] if "PE_TTM" in df else None
        turnover = df["TURN"].iloc[-1] if "TURN" in df else None

        # -------- 获取股票名称 --------
        name_res = w.wss(stock, "sec_name", "")
        name = name_res.Data[0][0]

        # 当前股价
        latest_price = close.iloc[-1]

        # 计算技术指标
        ma = calc_ma(close)
        rsi = calc_rsi(close)
        macd = calc_macd(close)
        boll = calc_boll(close)

        # 汇总
        row = {
            "stock": stock,
            "name": name,
            "current_price": latest_price,
            "volume": volume.iloc[-1],
            "pe_ttm": pe,
            "turnover": turnover,
        }
        row.update(ma)
        row.update(rsi)
        row.update(macd)
        row.update(boll)

        results.append(row)

    return pd.DataFrame(results)

if __name__ == '__main__':
    # 设置pandas显示选项
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.float_format', '{:.4f}'.format)  # 统一浮点数格式

    # 获取结果
    result_df = get_stock_recent_info(["000423.sz", "600519.SH","600887.sh"])

    print("=== 股票技术指标分析 ===")
    print(result_df)

    print("\n=== 详细字段说明 ===")
    print(f"总共计算了 {len(result_df.columns)} 个指标:")
    for i, col in enumerate(result_df.columns, 1):
        print(f"{i:2d}. {col}")