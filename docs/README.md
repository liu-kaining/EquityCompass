# 智策股析 - 技术文档总览

## 项目简介

**智策股析** 是一个面向个人投资者的多用户Web应用，通过集成先进的大语言模型（LLM）能力，为用户提供每日、深入、自动化的港股及美股分析报告。

## 文档结构

### 📋 [项目需求文档 (PRD)](../prd.md)
完整的产品需求文档，包含项目概述、功能需求、技术栈选择等。

### 🏗️ 架构设计文档

#### [系统架构总览](./architecture/01-system-overview.md)
- 项目概述与核心特性
- 整体架构层次设计
- 关键设计原则
- 技术栈选择
- 开发里程碑规划

#### [子系统设计详解](./architecture/02-subsystems-design.md)
- 用户认证系统
- 股票池管理系统
- AI分析引擎系统
- 报告管理系统
- 订阅付费系统
- 邮件订阅系统
- 管理员后台系统

### 🗄️ [数据库设计](./database/database-design.md)
- 数据库表结构设计
- 文件存储结构
- Redis缓存设计
- 数据库优化策略
- 备份恢复策略

### 🔌 [API接口设计](./api/api-design.md)
- RESTful API设计规范
- 认证与用户管理API
- 股票池与关注列表API
- 分析任务与报告API
- 订阅付费API
- 管理员API
- 系统监控API

### 🚀 [部署架构设计](./deployment/deployment-architecture.md)
- 开发环境配置
- 生产环境架构
- 负载均衡与服务配置
- 监控告警系统
- CI/CD流水线
- 容灾恢复方案

### 🔄 [核心业务流程](./business-flows/core-business-flows.md)
- 用户注册登录流程
- 每日分析任务执行流程
- 用户订阅付费流程
- 报告查询与导出流程
- 系统监控与告警流程
- 故障处理与恢复流程

## 核心特性概览

### 🔐 无密码认证
- 邮箱验证码登录
- 自动用户注册
- JWT Token会话管理

### 📊 个性化AI分析
- 用户自定义关注列表（最多20支股票）
- 多LLM模型支持（Gemini、Qwen、ChatGPT）
- 每日自动分析任务
- 详细的技术面和基本面分析

### ⚡ 异步架构
- Celery任务队列
- Redis消息中间件
- 任务状态跟踪
- 失败重试机制

### 💰 灵活付费模式
- 试用计划（1次免费分析）
- 订阅计划（月付/年付）
- 按次付费（购买分析次数包）
- Stripe/Paddle支付集成

### 📧 邮件订阅服务
- 每日报告摘要推送
- 个性化邮件内容
- 一键取消订阅

### 📈 全面监控
- Prometheus指标收集
- Grafana可视化面板
- AlertManager告警管理
- ELK日志聚合

## 技术栈

### 后端技术
- **Framework**: Flask (Python)
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL / SQLite
- **Cache**: Redis
- **Authentication**: JWT

### 前端技术
- **Framework**: React / Vue.js
- **Build Tool**: Next.js / Nuxt.js
- **UI Library**: 现代化组件库
- **State Management**: Redux / Vuex

### 基础设施
- **Containerization**: Docker
- **Orchestration**: Docker Compose / Kubernetes
- **Load Balancer**: Nginx
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

### 外部服务
- **Email**: SendGrid / Mailgun
- **Payment**: Stripe / Paddle
- **LLM**: OpenAI / Google Gemini / Qwen
- **Finance Data**: Alpha Vantage / Finnhub

## 开发阶段规划

### 🎯 第一阶段：MVP核心功能
- ✅ 无密码邮箱验证码登录系统
- ✅ 股票池和用户关注列表功能  
- ✅ 单次试用逻辑
- ✅ 异步分析任务基础架构
- ✅ 基本报告渲染页面

### 💳 第二阶段：付费模式与后台
- 支付网关集成
- 订阅和按次付费逻辑
- 完整管理员后台
- 任务状态跟踪和失败重试

### ✨ 第三阶段：体验优化与扩展
- 邮件订阅系统
- 报告导出功能
- 多LLM模型集成
- UI/UX优化

### 🚀 第四阶段：部署与迭代
- 生产环境部署
- 压力测试
- 用户反馈迭代

## 文档维护

### 更新原则
- 所有重大架构变更必须更新相关文档
- 新功能开发前须先更新设计文档
- 定期Review文档与实现的一致性

### 文档版本管理
- 使用Git管理文档版本
- 重要变更需要PR Review
- 保持文档与代码仓库同步

### 贡献指南
1. 创建功能分支
2. 更新相关文档
3. 提交PR并请求Review
4. 合并到主分支

---

## 联系方式

- **项目负责人**: [项目负责人]
- **技术负责人**: [技术负责人] 
- **产品负责人**: [产品负责人]

---

*此文档体系为智策股析项目提供完整的技术指导，确保团队对项目架构和实现细节有统一的理解。*
