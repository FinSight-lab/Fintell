"""快速测试技术指标"""
import sys
sys.path.insert(0, '.')

import pandas as pd
from app.services.indicators import calc_ma, calc_rsi, calc_macd, calc_boll

# 创建测试数据
s = pd.Series([i for i in range(1, 100)])

print("=" * 50)
print("技术指标计算测试")
print("=" * 50)

print("\nMA 指标:")
ma = calc_ma(s)
for k, v in ma.items():
    print(f"  {k}: {v}")

print("\nRSI 指标:")
rsi = calc_rsi(s)
for k, v in rsi.items():
    print(f"  {k}: {v}")

print("\nMACD 指标:")
macd = calc_macd(s)
for k, v in macd.items():
    print(f"  {k}: {v}")

print("\nBOLL 指标:")
boll = calc_boll(s)
for k, v in boll.items():
    print(f"  {k}: {v}")

print("\n" + "=" * 50)
print("测试完成")
