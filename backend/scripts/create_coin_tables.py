"""
创建金币系统相关数据表
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.coin import UserCoin, CoinTransaction, CoinPackage, CoinOrder, DailyBonus

def create_coin_tables():
    """创建金币系统相关表"""
    app = create_app()
    
    with app.app_context():
        try:
            # 创建所有金币相关表
            db.create_all()
            print("✅ 金币系统数据表创建成功")
            
            # 初始化默认金币套餐
            init_default_packages()
            
        except Exception as e:
            print(f"❌ 创建金币系统数据表失败: {str(e)}")
            return False
    
    return True

def init_default_packages():
    """初始化默认金币套餐"""
    try:
        # 检查是否已有套餐
        existing_packages = CoinPackage.query.count()
        if existing_packages > 0:
            print("📦 金币套餐已存在，跳过初始化")
            return
        
        # 创建默认套餐
        packages = [
            {
                'name': '每日免费',
                'description': '每日登录可获得20金币，可分析2个报告',
                'coins': 20,
                'price': 0.0,
                'package_type': 'FREE',
                'sort_order': 1
            },
            {
                'name': '小额包',
                'description': '100金币，可分析10个报告',
                'coins': 100,
                'price': 9.9,
                'original_price': 12.9,
                'package_type': 'SMALL',
                'sort_order': 2
            },
            {
                'name': '中额包',
                'description': '500金币，可分析50个报告',
                'coins': 500,
                'price': 39.9,
                'original_price': 49.9,
                'package_type': 'MEDIUM',
                'sort_order': 3
            },
            {
                'name': '大额包',
                'description': '1000金币，可分析100个报告',
                'coins': 1000,
                'price': 69.9,
                'original_price': 99.9,
                'package_type': 'LARGE',
                'sort_order': 4
            },
            {
                'name': '超大包',
                'description': '2000金币，可分析200个报告',
                'coins': 2000,
                'price': 119.9,
                'original_price': 199.9,
                'package_type': 'XLARGE',
                'sort_order': 5
            },
            {
                'name': '月度订阅',
                'description': '每日100金币，可分析10个报告/天',
                'coins': 100,  # 每日100金币，按月计算
                'price': 19.9,  # 每月19.9元，比一次性购买便宜
                'package_type': 'SUBSCRIPTION',
                'sort_order': 6
            },
            {
                'name': '年度订阅',
                'description': '每日120金币，可分析12个报告/天',
                'coins': 120,  # 每日120金币，按年计算
                'price': 199.0,  # 每年199元，比一次性购买便宜很多
                'package_type': 'SUBSCRIPTION',
                'sort_order': 7
            }
        ]
        
        for package_data in packages:
            package = CoinPackage(**package_data)
            db.session.add(package)
        
        db.session.commit()
        print("📦 默认金币套餐初始化成功")
        
    except Exception as e:
        print(f"❌ 初始化默认套餐失败: {str(e)}")
        db.session.rollback()

def init_existing_users():
    """为现有用户初始化金币账户"""
    app = create_app()
    
    with app.app_context():
        try:
            from app.models.user import User
            
            # 获取所有没有金币账户的用户
            users_without_coins = db.session.query(User).outerjoin(UserCoin).filter(UserCoin.id.is_(None)).all()
            
            if not users_without_coins:
                print("👥 所有用户已有金币账户")
                return
            
            print(f"👥 为 {len(users_without_coins)} 个现有用户初始化金币账户...")
            
            for user in users_without_coins:
                # 为新用户初始化20金币
                user_coin = UserCoin(
                    user_id=user.id,
                    total_coins=20,
                    available_coins=20
                )
                db.session.add(user_coin)
                db.session.flush()  # 获取user_coin.id
                
                # 记录初始金币交易
                transaction = CoinTransaction(
                    user_coin_id=user_coin.id,
                    user_id=user.id,
                    transaction_type='EARN',
                    amount=20,
                    balance_before=0,
                    balance_after=20,
                    description='新用户注册奖励',
                    related_type='REGISTRATION'
                )
                db.session.add(transaction)
            
            db.session.commit()
            print(f"✅ 为 {len(users_without_coins)} 个用户初始化金币账户成功")
            
        except Exception as e:
            print(f"❌ 初始化现有用户金币账户失败: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    print("🚀 开始创建金币系统...")
    
    # 创建数据表
    if create_coin_tables():
        # 为现有用户初始化金币账户
        init_existing_users()
        print("🎉 金币系统创建完成！")
    else:
        print("💥 金币系统创建失败！")
