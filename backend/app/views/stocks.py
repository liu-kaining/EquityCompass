"""
股票页面视图
"""
from flask import Blueprint, render_template, session, redirect, url_for

stocks_bp = Blueprint('stocks', __name__)

def login_required(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@stocks_bp.route('/')
@login_required
def index():
    """股票池页面"""
    # TODO: 获取股票数据
    stocks_data = []
    return render_template('stocks/index.html', stocks=stocks_data)

@stocks_bp.route('/watchlist')
@login_required  
def watchlist():
    """关注列表页面"""
    # TODO: 获取用户关注列表
    watchlist_data = []
    return render_template('stocks/watchlist.html', watchlist=watchlist_data)
