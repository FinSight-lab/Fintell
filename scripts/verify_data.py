"""Verify database data"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models import Portfolio, Position


def verify_data():
    """验证数据库数据"""
    db = SessionLocal()
    
    try:
        # 查询持仓组合
        portfolios = db.query(Portfolio).all()
        print(f"持仓组合数量: {len(portfolios)}\n")
        
        for portfolio in portfolios:
            print(f"组合 ID: {portfolio.id}")
            print(f"组合名称: {portfolio.name}")
            print(f"总资产: ¥{portfolio.total_assets:,.2f}")
            print(f"创建时间: {portfolio.created_at}")
            
            # 查询该组合的持仓
            positions = db.query(Position).filter(Position.portfolio_id == portfolio.id).all()
            print(f"\n持仓明细 ({len(positions)} 只股票):")
            print("-" * 80)
            print(f"{'股票代码':<15} {'数量':>10} {'成本价':>12} {'成本市值':>15}")
            print("-" * 80)
            
            total_cost = 0
            for pos in positions:
                cost_value = pos.quantity * float(pos.cost_price)
                total_cost += cost_value
                print(f"{pos.stock_code:<15} {pos.quantity:>10} {float(pos.cost_price):>12.3f} {cost_value:>15,.2f}")
            
            print("-" * 80)
            print(f"{'总计':<15} {'':<10} {'':<12} {total_cost:>15,.2f}")
            print()
        
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 80)
    print("数据库数据验证")
    print("=" * 80)
    print()
    verify_data()
