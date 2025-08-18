
# 🧭 EquityCompass

**AI驱动的智能投研罗盘，每日深度解析港美股，指引您的投资方向。**

EquityCompass 是一个利用先进大语言模型（LLM）能力，为个人投资者提供自动化、深度股票分析的Web平台。它旨在将繁琐的每日投研工作自动化，通过AI生成的技术面和基本面分析报告，帮助用户在瞬息万变的金融市场中做出更明智的决策。

## ✨ 核心功能 (Core Features)

  * **🤖 AI 驱动分析**: 每日自动调用大语言模型 (如 Gemini, ChatGPT, Qwen)，对您关注的股票进行深入的技术面和基本面分析。
  * **📈 覆盖港美市场**: 内置港股与美股市值TOP 100股票池，并支持用户添加自定义股票。
  * **❤️ 个性化关注列表**: 每位用户可建立一个包含最多20支股票的个性化投资组合，作为每日分析的目标。
  * **📄 报告管理与导出**: 所有分析报告均可按日期、公司、行业进行查询和筛选，并支持Markdown或PDF格式的批量导出。
  * **📬 邮件订阅**: 用户可选择邮件订阅，每日清晨将分析报告摘要发送至邮箱，并附带原文链接。
  * **🔑 无密码登录**: 采用安全的邮箱验证码登录方式，免去用户记忆密码的烦恼。
  * **🔌 可扩展模型架构**: 系统设计支持轻松集成和切换不同的大语言模型，保持技术前沿。
  * **💰 商业模式规划**: 内置试用、按月订阅和按次付费的商业逻辑，为未来运营提供支持。

## 🛠️ 技术栈 (Technology Stack)

  * **后端 (Backend):** Python, Flask, Celery
  * **前端 (Frontend):** React (Next.js) / Vue (Nuxt.js) (前后端分离)
  * **数据库 (Database):** PostgreSQL (生产环境), SQLite (开发环境)
  * **异步任务队列 (Task Queue):** Redis / RabbitMQ 作为 Celery 的消息代理
  * **大语言模型 (LLMs):** Google Gemini, OpenAI GPT series, Qwen 等

## 🚀 快速开始 (Getting Started)

### 环境要求 (Prerequisites)

  * Git
  * Python 3.9+
  * Node.js and npm/yarn (用于前端)
  * Redis (或其他 Celery Broker)


## 📄 许可证 (License)

本项目采用 [MIT License](https://www.google.com/search?q=LICENSE) 开源许可证。
