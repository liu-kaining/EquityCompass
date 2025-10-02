"""
更新金币套餐定价
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.coin import CoinPackage

def update_coin_pricing():
    """更新金币套餐定价"""
    app = create_app()
    
    with app.app_context():
        try:
            # 删除现有套餐
            CoinPackage.query.delete()
            db.session.commit()
            print("🗑️ 已删除现有套餐")
            
            # 创建新的合理定价套餐
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
                    'coins': 100,  # 每日100金币
                    'price': 19.9,  # 每月19.9元
                    'package_type': 'SUBSCRIPTION',
                    'sort_order': 6
                },
                {
                    'name': '年度订阅',
                    'description': '每日120金币，可分析12个报告/天',
                    'coins': 120,  # 每日120金币
                    'price': 199.0,  # 每年199元
                    'package_type': 'SUBSCRIPTION',
                    'sort_order': 7
                }
            ]
            
            for package_data in packages:
                package = CoinPackage(**package_data)
                db.session.add(package)
            
            db.session.commit()
            print("✅ 金币套餐定价更新成功")
            
            # 显示新的定价
            print("\n📊 新的定价策略：")
            print("=" * 50)
            for package in CoinPackage.query.order_by(CoinPackage.sort_order).all():
                if package.package_type == 'SUBSCRIPTION':
                    print(f"📦 {package.name}: ¥{package.price} ({package.coins}金币/天)")
                else:
                    print(f"📦 {package.name}: ¥{package.price} ({package.coins}金币)")
            
        except Exception as e:
            print(f"❌ 更新定价失败: {str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 开始更新金币套餐定价...")
    if update_coin_pricing():
        print("🎉 定价更新完成！")
    else:
        print("❌ 定价更新失败！")
