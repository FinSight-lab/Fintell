"""Import initial portfolio data from stock_position.json"""

import sys
import json
from pathlib import Path
from decimal import Decimal

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models import Portfolio, Position


def import_data():
    """从 stock_position.json 导入初始持仓数据"""
    
    # 读取 JSON 文件
    json_path = Path(__file__).parent.parent / "stock_position.json"
    
    if not json_path.exists():
        print(f"❌ 文件不存在: {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✓ 读取持仓数据: {len(data['stocks'])} 只股票")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing_portfolio = db.query(Portfolio).first()
        if existing_portfolio:
            print(f"\n⚠️  数据库中已存在持仓数据")
            response = input("是否覆盖现有数据？(y/N): ")
            if response.lower() != 'y':
                print("取消导入")
                return
            
            # 删除现有数据
            db.query(Position).delete()
            db.query(Portfolio).delete()
            db.commit()
            print("✓ 已删除现有数据")
        
        # 创建新的持仓组合
        portfolio = Portfolio(
            name="默认组合",
            total_assets=Decimal(str(data['total_assets'])),
            description="从 stock_position.json 导入的初始持仓"
        )
        db.add(portfolio)
        db.flush()  # 获取 portfolio.id
        
        print(f"\n✓ 创建持仓组合: {portfolio.name} (ID: {portfolio.id})")
        print(f"  总资产: ¥{portfolio.total_assets:,.2f}")
        
        # 创建持仓记录
        positions_created = 0
        for stock_code in data['stocks']:
            # 标准化股票代码（转大写）
            stock_code_upper = stock_code.upper()
            
            quantity = data['positions'].get(stock_code, 0)
            cost_price = data['cost_prices'].get(stock_code, 0)
            
            if quantity > 0 and cost_price > 0:
                position = Position(
                    portfolio_id=portfolio.id,
                    stock_code=stock_code_upper,
                    quantity=quantity,
                    cost_price=Decimal(str(cost_price))
                )
                db.add(position)
                positions_created += 1
                print(f"  + {stock_code_upper}: {quantity} 股 @ ¥{cost_price}")
        
        # 提交事务
        db.commit()
        
        print(f"\n✓ 成功导入 {positions_created} 条持仓记录")
        print(f"\n数据库信息:")
        print(f"  - 持仓组合 ID: {portfolio.id}")
        print(f"  - 持仓数量: {positions_created}")
        print(f"  - 总资产: ¥{portfolio.total_assets:,.2f}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 导入失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("导入初始持仓数据")
    print("=" * 60)
    import_data()
    print("\n✓ 导入完成！")
