"""
分析页面视图
"""
from flask import Blueprint, render_template, session, redirect, url_for
from app.services.data.stock_service import StockDataService
from app import db

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/')
def index():
    """分析页面"""
    # 检查用户登录状态
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    # 获取用户关注列表
    service = StockDataService(db.session)
    watchlist_data = service.get_user_watchlist(user_id)
    
    return render_template('analysis/index.html', watchlist=watchlist_data['watchlist'])
