#!/usr/bin/env python3
"""
EquityCompass Core - 可复用的核心功能包
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="equitycompass-core",
    version="1.0.0",
    author="EquityCompass Team",
    author_email="team@equitycompass.com",
    description="可复用的核心功能模块：认证、AI代理、异步任务、UI组件",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/equitycompass-core",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "ai": [
            "openai>=1.0.0",
            "anthropic>=0.3.0",
        ],
        "web": [
            "flask>=2.0.0",
            "django>=3.2.0",
            "fastapi>=0.68.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "equitycompass-cli=equitycompass.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "equitycompass": [
            "ui/templates/*.html",
            "ui/static/css/*.css",
            "ui/static/js/*.js",
        ],
    },
    zip_safe=False,
)
