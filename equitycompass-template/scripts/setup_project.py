#!/usr/bin/env python3
"""
项目设置脚本 - 帮助快速配置新项目
"""

import os
import re
import shutil
import argparse
from pathlib import Path


def replace_in_file(file_path, old_text, new_text):
    """在文件中替换文本"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace(old_text, new_text)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已更新文件: {file_path}")
    except Exception as e:
        print(f"❌ 更新文件失败 {file_path}: {e}")


def update_project_name(project_name, project_dir):
    """更新项目名称"""
    print(f"🔄 正在更新项目名称为: {project_name}")
    
    # 需要更新的文件列表
    files_to_update = [
        "README.md",
        "setup.py",
        "requirements.txt",
        "backend/app/__init__.py",
        "backend/app/config.py",
        "backend/run.py",
        "docker-compose.yml",
        "Dockerfile"
    ]
    
    # 需要更新的目录列表
    dirs_to_rename = [
        ("equitycompass_template", f"{project_name}_template"),
        ("backend/app", f"backend/{project_name}"),
    ]
    
    # 更新文件内容
    for file_path in files_to_update:
        full_path = Path(project_dir) / file_path
        if full_path.exists():
            replace_in_file(full_path, "equitycompass", project_name)
            replace_in_file(full_path, "EquityCompass", project_name.title())
            replace_in_file(full_path, "EQUITYCOMPASS", project_name.upper())
    
    # 重命名目录
    for old_dir, new_dir in dirs_to_rename:
        old_path = Path(project_dir) / old_dir
        new_path = Path(project_dir) / new_dir
        if old_path.exists():
            shutil.move(str(old_path), str(new_path))
            print(f"✅ 已重命名目录: {old_dir} -> {new_dir}")


def create_env_file(project_dir):
    """创建环境变量文件"""
    env_content = """# 项目配置
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# 数据库配置
DATABASE_URL=sqlite:///app.db
# DATABASE_URL=postgresql://user:password@localhost/dbname

# AI 服务配置
QWEN_API_KEY=your-qwen-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
OPENAI_API_KEY=your-openai-api-key

# 邮件配置
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# 开发环境配置
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    env_file = Path(project_dir) / ".env"
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ 已创建 .env 文件")


def create_gitignore(project_dir):
    """创建 .gitignore 文件"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# Environment Variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Flask
instance/
.webassets-cache

# Celery
celerybeat-schedule
celerybeat.pid

# Redis
dump.rdb

# Docker
.dockerignore

# Coverage
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# mypy
.mypy_cache/
.dmypy.json
dmypy.json
"""
    
    gitignore_file = Path(project_dir) / ".gitignore"
    with open(gitignore_file, 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print("✅ 已创建 .gitignore 文件")


def create_requirements(project_dir):
    """创建 requirements.txt 文件"""
    requirements_content = """# 核心依赖
Flask>=2.0.0
PyJWT>=2.0.0
requests>=2.25.0
markdown>=3.3.0
python-dotenv>=0.19.0

# 数据库相关
SQLAlchemy>=1.4.0
Flask-SQLAlchemy>=3.0.0
alembic>=1.7.0

# AI 相关
openai>=1.0.0
anthropic>=0.3.0

# 异步任务
celery>=5.2.0
redis>=4.0.0

# 工具库
python-dateutil>=2.8.0
pytz>=2021.1
cryptography>=3.4.0

# 前端相关
Jinja2>=3.0.0
MarkupSafe>=2.0.0

# 开发工具
pytest>=6.0.0
pytest-cov>=2.12.0
black>=21.0.0
flake8>=3.9.0
mypy>=0.910
"""
    
    requirements_file = Path(project_dir) / "requirements.txt"
    with open(requirements_file, 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    print("✅ 已创建 requirements.txt 文件")


def create_docker_files(project_dir):
    """创建 Docker 相关文件"""
    # Dockerfile
    dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "run.py"]
"""
    
    dockerfile = Path(project_dir) / "Dockerfile"
    with open(dockerfile, 'w', encoding='utf-8') as f:
        f.write(dockerfile_content)
    
    # docker-compose.yml
    compose_content = """version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:password@db:5432/appdb
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
    command: python run.py

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=appdb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
"""
    
    compose_file = Path(project_dir) / "docker-compose.yml"
    with open(compose_file, 'w', encoding='utf-8') as f:
        f.write(compose_content)
    
    print("✅ 已创建 Docker 相关文件")


def main():
    parser = argparse.ArgumentParser(description='设置新项目')
    parser.add_argument('project_name', help='项目名称')
    parser.add_argument('--dir', default='.', help='项目目录（默认当前目录）')
    
    args = parser.parse_args()
    
    project_name = args.project_name.lower().replace('-', '_').replace(' ', '_')
    project_dir = Path(args.dir).resolve()
    
    print(f"🚀 开始设置项目: {project_name}")
    print(f"📁 项目目录: {project_dir}")
    
    # 检查项目目录是否存在
    if not project_dir.exists():
        print(f"❌ 项目目录不存在: {project_dir}")
        return
    
    try:
        # 更新项目名称
        update_project_name(project_name, project_dir)
        
        # 创建配置文件
        create_env_file(project_dir)
        create_gitignore(project_dir)
        create_requirements(project_dir)
        create_docker_files(project_dir)
        
        print("\n🎉 项目设置完成！")
        print("\n📋 下一步操作：")
        print("1. 编辑 .env 文件，配置你的 API 密钥和数据库连接")
        print("2. 运行: pip install -r requirements.txt")
        print("3. 运行: python scripts/init_db.py")
        print("4. 运行: python run.py")
        print("\n🔧 开发工具：")
        print("- 代码格式化: black .")
        print("- 代码检查: flake8 .")
        print("- 类型检查: mypy .")
        print("- 运行测试: pytest")
        
    except Exception as e:
        print(f"❌ 设置失败: {e}")


if __name__ == "__main__":
    main()
