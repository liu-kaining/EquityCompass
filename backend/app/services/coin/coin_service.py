"""
金币系统服务层
"""
import uuid
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.coin import UserCoin, CoinTransaction, CoinPackage, CoinOrder, DailyBonus
from app.models.user import User
from app.repositories.coin_repository import CoinRepository
from app.utils.response import success_response, error_response


class CoinService:
    """金币服务"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.repository = CoinRepository(db_session)
    
    def initialize_user_coins(self, user_id: int, initial_coins: int = 20) -> Dict:
        """初始化用户金币账户"""
        try:
            # 检查是否已有金币账户
            existing_coin = self.repository.get_user_coin(user_id)
            if existing_coin:
                return {
                    'success': False,
                    'error': 'USER_COIN_EXISTS',
                    'message': '用户金币账户已存在'
                }
            
            # 创建金币账户
            user_coin = self.repository.create_user_coin(
                user_id=user_id,
                total_coins=initial_coins,
                available_coins=initial_coins
            )
            
            # 记录初始金币交易
            self._create_transaction(
                user_coin_id=user_coin.id,
                user_id=user_id,
                transaction_type='EARN',
                amount=initial_coins,
                balance_before=0,
                balance_after=initial_coins,
                description='新用户注册奖励',
                related_type='REGISTRATION'
            )
            
            return {
                'success': True,
                'data': {
                    'user_coin_id': user_coin.id,
                    'total_coins': user_coin.total_coins,
                    'available_coins': user_coin.available_coins
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'INITIALIZE_COINS_FAILED',
                'message': f"初始化用户金币失败: {str(e)}"
            }
    
    def get_user_coin_info(self, user_id: int) -> Dict:
        """获取用户金币信息"""
        try:
            user_coin = self.repository.get_user_coin(user_id)
            if not user_coin:
                return error_response("USER_COIN_NOT_FOUND", "用户金币账户不存在")
            
            # 获取最近交易记录
            recent_transactions = self.repository.get_user_transactions(
                user_id=user_id,
                limit=10
            )
            
            return {
                'success': True,
                'data': {
                    'user_coin_id': user_coin.id,
                    'total_coins': user_coin.total_coins,
                    'available_coins': user_coin.available_coins,
                    'frozen_coins': user_coin.frozen_coins,
                    'recent_transactions': [
                        {
                            'id': t.id,
                            'type': t.transaction_type,
                            'amount': t.amount,
                            'description': t.description,
                            'created_at': t.created_at.isoformat()
                        } for t in recent_transactions
                    ]
                }
            }
            
        except Exception as e:
            return error_response("GET_USER_COIN_INFO_FAILED", f"获取用户金币信息失败: {str(e)}")
    
    def spend_coins(self, user_id: int, amount: int, description: str, related_id: int = None, related_type: str = None) -> Dict:
        """消耗金币"""
        try:
            user_coin = self.repository.get_user_coin(user_id)
            if not user_coin:
                return error_response("USER_COIN_NOT_FOUND", "用户金币账户不存在")
            
            if user_coin.available_coins < amount:
                return error_response("INSUFFICIENT_COINS", f"金币不足，需要{amount}金币，当前可用{user_coin.available_coins}金币")
            
            # 更新金币余额
            balance_before = user_coin.available_coins
            user_coin.available_coins -= amount
            user_coin.total_coins -= amount
            
            # 记录交易
            transaction = self._create_transaction(
                user_coin_id=user_coin.id,
                user_id=user_id,
                transaction_type='SPEND',
                amount=-amount,
                balance_before=balance_before,
                balance_after=user_coin.available_coins,
                description=description,
                related_id=related_id,
                related_type=related_type
            )
            
            self.db.commit()
            
            return {
                'success': True,
                'data': {
                    'transaction_id': transaction.id,
                    'spent_coins': amount,
                    'remaining_coins': user_coin.available_coins
                }
            }
            
        except Exception as e:
            self.db.rollback()
            return error_response("SPEND_COINS_FAILED", f"消耗金币失败: {str(e)}")
    
    def earn_coins(self, user_id: int, amount: int, description: str, transaction_type: str = 'EARN', related_id: int = None, related_type: str = None) -> Dict:
        """获得金币"""
        try:
            user_coin = self.repository.get_user_coin(user_id)
            if not user_coin:
                return error_response("USER_COIN_NOT_FOUND", "用户金币账户不存在")
            
            # 更新金币余额
            balance_before = user_coin.available_coins
            user_coin.available_coins += amount
            user_coin.total_coins += amount
            
            # 记录交易
            transaction = self._create_transaction(
                user_coin_id=user_coin.id,
                user_id=user_id,
                transaction_type=transaction_type,
                amount=amount,
                balance_before=balance_before,
                balance_after=user_coin.available_coins,
                description=description,
                related_id=related_id,
                related_type=related_type
            )
            
            self.db.commit()
            
            return success_response({
                'transaction_id': transaction.id,
                'earned_coins': amount,
                'total_coins': user_coin.available_coins
            })
            
        except Exception as e:
            self.db.rollback()
            return error_response("EARN_COINS_FAILED", f"获得金币失败: {str(e)}")
    
    def check_daily_bonus_status(self, user_id: int) -> Dict:
        """检查每日签到状态"""
        try:
            today = date.today()
            
            # 检查今天是否已签到
            existing_bonus = self.repository.get_daily_bonus(user_id, today)
            checked_in_today = existing_bonus is not None
            
            # 计算连续签到天数
            streak_days = self._calculate_streak_days(user_id)
            
            return success_response({
                'checked_in_today': checked_in_today,
                'streak_days': streak_days,
                'last_checkin_date': existing_bonus.bonus_date.isoformat() if existing_bonus else None
            })
            
        except Exception as e:
            return error_response("CHECK_STATUS_FAILED", f"检查签到状态失败: {str(e)}")
    
    def get_bonus_stats(self, user_id: int) -> Dict:
        """获取签到统计"""
        try:
            stats = self.repository.get_user_bonus_stats(user_id)
            return success_response(stats)
            
        except Exception as e:
            return error_response("GET_BONUS_STATS_FAILED", f"获取签到统计失败: {str(e)}")
    
    def daily_bonus(self, user_id: int) -> Dict:
        """每日签到奖励"""
        try:
            from flask import current_app
            current_app.logger.info(f"每日签到开始 - user_id: {user_id}")
            
            today = date.today()
            current_app.logger.info(f"今日日期: {today}")
            
            # 检查今天是否已签到
            existing_bonus = self.repository.get_daily_bonus(user_id, today)
            current_app.logger.info(f"检查今日签到记录: {existing_bonus}")
            
            if existing_bonus:
                current_app.logger.info("今日已签到，返回错误")
                return error_response("ALREADY_CHECKED_IN", "今日已签到，请明天再来")
            
            # 计算连续签到天数
            streak_days = self._calculate_streak_days(user_id)
            current_app.logger.info(f"连续签到天数: {streak_days}")
            
            # 计算奖励金币（基础20金币 + 连续签到奖励）
            base_coins = 20
            streak_bonus = min(streak_days * 2, 50)  # 连续签到每天额外2金币，最多50金币
            total_coins = base_coins + streak_bonus
            current_app.logger.info(f"奖励计算 - 基础: {base_coins}, 连续奖励: {streak_bonus}, 总计: {total_coins}")
            
            # 发放奖励
            earn_result = self.earn_coins(
                user_id=user_id,
                amount=total_coins,
                description=f'每日签到奖励（连续{streak_days}天）',
                transaction_type='DAILY_BONUS'
            )
            
            current_app.logger.info(f"发放奖励结果: {earn_result}")
            
            # 检查earn_result是否是tuple（Flask Response对象）
            if isinstance(earn_result, tuple):
                # 如果是tuple，说明是Flask Response对象，需要检查响应内容
                response_obj, status_code = earn_result
                if status_code != 200:
                    current_app.logger.error(f"发放奖励失败，状态码: {status_code}")
                    return earn_result
            else:
                # 如果是字典，检查success字段
                if not earn_result.get('success', False):
                    current_app.logger.error(f"发放奖励失败: {earn_result}")
                    return earn_result
            
            # 记录签到记录
            self.repository.create_daily_bonus(
                user_id=user_id,
                bonus_date=today,
                coins_earned=total_coins,
                streak_days=streak_days
            )
            
            result = success_response({
                'earned_coins': total_coins,
                'streak_days': streak_days,
                'base_coins': base_coins,
                'streak_bonus': streak_bonus
            })
            
            current_app.logger.info(f"每日签到完成，返回结果: {result}")
            return result
            
        except Exception as e:
            from flask import current_app
            current_app.logger.error(f"每日签到异常: {str(e)}", exc_info=True)
            return error_response("DAILY_BONUS_FAILED", f"每日签到失败: {str(e)}")
    
    def get_coin_packages(self) -> Dict:
        """获取金币套餐列表"""
        try:
            packages = self.repository.get_active_packages()
            
            return success_response([
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'coins': p.coins,
                    'price': p.price,
                    'original_price': p.original_price,
                    'package_type': p.package_type,
                    'sort_order': p.sort_order
                } for p in packages
            ])
            
        except Exception as e:
            return error_response("GET_PACKAGES_FAILED", f"获取金币套餐失败: {str(e)}")
    
    def create_coin_order(self, user_id: int, package_id: int) -> Dict:
        """创建金币订单"""
        try:
            # 获取套餐信息
            package = self.repository.get_package(package_id)
            if not package or not package.is_active:
                return error_response("PACKAGE_NOT_FOUND", "套餐不存在或已下架")
            
            # 生成订单号
            order_no = f"COIN_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # 创建订单
            order = self.repository.create_coin_order(
                user_id=user_id,
                package_id=package_id,
                order_no=order_no,
                amount=package.price,
                coins=package.coins
            )
            
            return success_response({
                'order_id': order.id,
                'order_no': order.order_no,
                'amount': order.amount,
                'coins': order.coins,
                'package_name': package.name
            })
            
        except Exception as e:
            return error_response("CREATE_ORDER_FAILED", f"创建订单失败: {str(e)}")
    
    def complete_coin_order(self, order_id: int, payment_method: str, payment_id: str) -> Dict:
        """完成金币订单（支付成功）"""
        try:
            order = self.repository.get_coin_order(order_id)
            if not order:
                return error_response("ORDER_NOT_FOUND", "订单不存在")
            
            if order.status != 'PENDING':
                return error_response("INVALID_ORDER_STATUS", "订单状态不正确")
            
            # 更新订单状态
            order.status = 'PAID'
            order.payment_method = payment_method
            order.payment_id = payment_id
            order.paid_at = datetime.utcnow()
            
            # 发放金币
            earn_result = self.earn_coins(
                user_id=order.user_id,
                amount=order.coins,
                description=f'购买金币套餐：{order.package.name}',
                transaction_type='PURCHASE',
                related_id=order.id,
                related_type='ORDER'
            )
            
            if not earn_result['success']:
                return earn_result
            
            self.db.commit()
            
            return success_response({
                'order_id': order.id,
                'coins_added': order.coins,
                'total_coins': earn_result['data']['total_coins']
            })
            
        except Exception as e:
            self.db.rollback()
            return error_response("COMPLETE_ORDER_FAILED", f"完成订单失败: {str(e)}")
    
    def get_user_transactions(self, user_id: int, page: int = 1, per_page: int = 20) -> Dict:
        """获取用户交易记录"""
        try:
            transactions = self.repository.get_user_transactions_paginated(
                user_id=user_id,
                page=page,
                per_page=per_page
            )
            
            return success_response({
                'transactions': [
                    {
                        'id': t.id,
                        'type': t.transaction_type,
                        'amount': t.amount,
                        'balance_before': t.balance_before,
                        'balance_after': t.balance_after,
                        'description': t.description,
                        'related_type': t.related_type,
                        'created_at': t.created_at.isoformat()
                    } for t in transactions.items
                ],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': transactions.total,
                    'pages': transactions.pages
                }
            })
            
        except Exception as e:
            return error_response("GET_TRANSACTIONS_FAILED", f"获取交易记录失败: {str(e)}")
    
    def _create_transaction(self, user_coin_id: int, user_id: int, transaction_type: str, 
                          amount: int, balance_before: int, balance_after: int, 
                          description: str, related_id: int = None, related_type: str = None) -> CoinTransaction:
        """创建交易记录"""
        transaction = CoinTransaction(
            user_coin_id=user_coin_id,
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description,
            related_id=related_id,
            related_type=related_type
        )
        
        self.db.add(transaction)
        self.db.flush()
        return transaction
    
    def _calculate_streak_days(self, user_id: int) -> int:
        """计算连续签到天数"""
        today = date.today()
        streak_days = 1
        
        # 从昨天开始往前查找连续签到
        for i in range(1, 30):  # 最多查找30天
            check_date = today - timedelta(days=i)
            bonus = self.repository.get_daily_bonus(user_id, check_date)
            if bonus:
                streak_days += 1
            else:
                break
        
        return streak_days
