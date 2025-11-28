"""Create database if it doesn't exist"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pymysql
from app.core.config import settings

def create_database():
    """创建数据库"""
    # 连接到 MySQL（不指定数据库）
    connection = pymysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        charset='utf8mb4'
    )
    
    try:
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✓ Database '{settings.DB_NAME}' created or already exists")
            
            # 显示数据库
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print(f"\n可用的数据库:")
            for db in databases:
                print(f"  - {db[0]}")
        
        connection.commit()
    finally:
        connection.close()

if __name__ == "__main__":
    print("正在创建数据库...")
    create_database()
    print("\n✓ 数据库创建完成！")
