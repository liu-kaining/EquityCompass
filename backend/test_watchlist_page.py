#!/usr/bin/env python3
"""
测试关注列表页面功能
"""
from flask import Flask, render_template_string, session
from app import create_app, db
from app.models.user import User
from app.services.data.stock_service import StockDataService

def create_test_app():
    app = create_app()
    
    @app.route('/test/watchlist')
    def test_watchlist():
        # 模拟用户登录
        user = User.query.filter_by(email='liqian_macmini@qxmy.tech').first()
        if user:
            session['user_id'] = user.id
            print(f"模拟用户登录: {user.email} (ID: {user.id})")
        
        # 获取关注列表
        service = StockDataService(db.session)
        watchlist_data = service.get_user_watchlist(user.id if user else 1)
        
        # 简单的HTML模板
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>关注列表测试</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .stock-item { border: 1px solid #ddd; padding: 10px; margin: 5px 0; border-radius: 5px; }
                .stock-code { font-weight: bold; color: #007bff; }
                .stock-name { color: #333; }
                .stock-time { color: #666; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <h1>关注列表测试</h1>
            <p>用户ID: {{ user_id }}</p>
            <p>关注数量: {{ watchlist.count }}</p>
            <p>最大关注数: {{ watchlist.max_count }}</p>
            <p>剩余额度: {{ watchlist.remaining_slots }}</p>
            
            <h2>关注的股票:</h2>
            {% if watchlist.watchlist %}
                {% for item in watchlist.watchlist %}
                <div class="stock-item">
                    <div class="stock-code">{{ item.stock.code }}</div>
                    <div class="stock-name">{{ item.stock.name }}</div>
                    <div class="stock-time">添加时间: {{ item.added_at }}</div>
                </div>
                {% endfor %}
            {% else %}
                <p>没有关注任何股票</p>
            {% endif %}
            
            <h2>原始数据:</h2>
            <pre>{{ watchlist_data }}</pre>
        </body>
        </html>
        """
        
        return render_template_string(html, 
                                    user_id=user.id if user else 'Unknown',
                                    watchlist=watchlist_data,
                                    watchlist_data=str(watchlist_data))
    
    return app

if __name__ == "__main__":
    app = create_test_app()
    app.run(debug=True, port=5002)
