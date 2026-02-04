# Backend

基于 FastAPI 的 Agent 应用后端服务，提供用户管理、MCP 配置、LLM 配置和 Agent 对话功能。

## 项目概述

本项目是一个智能 Agent 应用的后端服务，支持：

- 用户认证与管理（JWT）
- MCP（Model Context Protocol）服务器配置管理
- LLM（大语言模型）配置管理
- Agent 对话功能（支持流式响应）
- 内置工具（文件操作、网络搜索）
- 外部 MCP 工具集成

## 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| Web 框架 | FastAPI | 0.109.0 |
| ASGI 服务器 | Uvicorn | 0.27.0 |
| 数据验证 | Pydantic | 2.5.3 |
| ORM | SQLAlchemy | 2.0.25 |
| 数据库 | MySQL | - |
| 数据库驱动 | aiomysql | 0.2.0 |
| 缓存 | Redis | 5.0.1 |
| 认证 | JWT (python-jose) | 3.3.0 |
| 密码加密 | Passlib + Bcrypt | 1.7.4 |
| MCP | mcp + fastmcp | 1.0.0 / 0.4.0 |
| LLM 客户端 | OpenAI SDK | 1.10.0 |
| HTTP 客户端 | httpx | 0.26.0 |
| 日志 | loguru | 0.7.2 |

## 项目结构

```
backend/
├── app/                          # 应用主目录
│   ├── api/                      # API 路由
│   │   └── v1/
│   │       └── endpoints/        # API 端点
│   │           ├── agent.py      # Agent 对话接口
│   │           ├── auth.py       # 认证接口
│   │           ├── llm.py        # LLM 配置接口
│   │           ├── mcp.py        # MCP 配置接口
│   │           └── users.py      # 用户接口
│   ├── core/                     # 核心模块
│   │   ├── agent_executor.py     # Agent 执行器
│   │   ├── config.py             # 配置管理
│   │   ├── database.py           # 数据库连接
│   │   ├── deps.py               # 依赖注入
│   │   ├── llm_client.py         # LLM 客户端
│   │   ├── security.py           # 安全相关
│   │   └── tool_manager.py       # 工具管理器
│   ├── models/                   # 数据库模型
│   │   ├── llm_config.py         # LLM 配置模型
│   │   ├── mcp_server.py         # MCP 服务器模型
│   │   └── user.py               # 用户模型
│   ├── schemas/                  # Pydantic 模式
│   │   ├── agent.py              # Agent 模式
│   │   ├── llm.py                # LLM 模式
│   │   ├── mcp.py                # MCP 模式
│   │   └── user.py               # 用户模式
│   ├── services/                 # 业务逻辑层
│   │   ├── llm_service.py        # LLM 服务
│   │   ├── mcp_service.py        # MCP 服务
│   │   └── test.py               # 测试服务
│   ├── tools/                    # 工具层
│   │   └── builtin/              # 内置工具
│   │       ├── file_read.py      # 文件读取
│   │       ├── file_save.py      # 文件保存
│   │       ├── file_search.py    # 文件搜索
│   │       └── web_search.py     # 网络搜索
│   ├── main.py                   # 应用入口
│   └── __init__.py
├── docs/                         # 文档目录
│   ├── 01-architecture.md        # 架构设计文档
│   ├── 02-agent-flow.md          # Agent 执行流程
│   └── backend-status.md         # 后端状态
├── sql/                          # SQL 脚本
│   └── 01-init.sql               # 数据库初始化脚本
├── output/                       # 输出目录
├── .env                          # 环境变量配置
├── requirements.txt              # Python 依赖
└── API使用文档.md                # API 使用文档
```

## 快速开始

### 环境要求

- Python 3.12+
- MySQL 8.0+
- Redis 6.0+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

编辑 `.env` 文件，配置以下参数：

```env
# 应用配置
APP_NAME=Agent Application
APP_VERSION=1.0.0
DEBUG=True

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=agent_app

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# JWT 配置
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS 配置
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 初始化数据库

```bash
# 执行初始化脚本
mysql -u root -p < sql/01-init.sql
```

### 启动服务

```bash
# 开发模式
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 访问文档

服务启动后，可以通过以下地址访问交互式 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 核心功能

### 1. 用户模块

- 用户注册
- 用户登录（JWT 认证）
- 获取/更新用户信息
- 删除用户

### 2. MCP 配置管理

- 创建 MCP 服务器配置（支持 stdio 和 sse 两种类型）
- 获取 MCP 服务器列表
- 更新/删除 MCP 服务器配置
- 测试 MCP 服务器连接

### 3. LLM 配置管理

- 创建 LLM 配置（支持 OpenAI、Anthropic、自定义端点）
- 获取 LLM 配置列表
- 设置默认 LLM 配置
- 更新/删除 LLM 配置

### 4. Agent 核心功能

- Agent 聊天（支持普通响应和流式响应）
- 工具调用（内置工具 + 外部 MCP 工具）
- Agent 状态检查

## 内置工具

| 工具名称 | 功能描述 |
|---------|---------|
| file_save | 保存内容到指定文件 |
| file_read | 读取指定文件内容 |
| file_search | 在文件中搜索匹配的内容 |
| web_search | 搜索网络信息 |

## API 文档

详细的 API 使用文档请参考 [API使用文档.md](./API使用文档.md)

### 主要 API 端点

| 端点 | 方法 | 描述 |
|-----|------|-----|
| `/api/v1/auth/register` | POST | 用户注册 |
| `/api/v1/auth/login` | POST | 用户登录 |
| `/api/v1/auth/me` | GET/PUT/DELETE | 获取/更新/删除当前用户 |
| `/api/v1/mcp/servers` | GET/POST | 获取/创建 MCP 服务器 |
| `/api/v1/llm/configs` | GET/POST | 获取/创建 LLM 配置 |
| `/api/v1/agent/chat` | POST | Agent 聊天 |
| `/api/v1/agent/chat/stream` | POST | Agent 流式聊天 |

## 开发指南

### 代码规范

- 使用 Python 3.12+ 类型注解
- 遵循 PEP 8 代码风格
- 添加函数级注释
- 使用 Pydantic 进行数据验证

### 添加新工具

1. 在 `app/tools/builtin/` 目录下创建新的工具文件
2. 使用 fastmcp 装饰器定义工具函数
3. 在 `app/core/tool_manager.py` 中注册新工具

### 添加新 API 端点

1. 在 `app/api/v1/endpoints/` 目录下创建新的端点文件
2. 定义路由和处理函数
3. 在 `app/api/v1/__init__.py` 中注册路由

## 架构设计

详细的架构设计文档请参考：

- [架构设计文档](./docs/01-architecture.md)
- [Agent 执行流程](./docs/02-agent-flow.md)

### 三层架构

1. **决策层 (LLM)**: 分析任务意图，决策是否调用工具
2. **编排层 (Agent)**: 接收 LLM 决策，路由到对应工具
3. **执行层 (工具)**: 执行具体工具调用（内置工具 + 外部 MCP 工具）

## 数据库表结构

- `users`: 用户表
- `mcp_servers`: MCP 服务器配置表
- `llm_configs`: LLM 配置表

## 常见问题

### 1. 数据库连接失败

检查 MySQL 服务是否启动，以及 `.env` 文件中的数据库配置是否正确。

### 2. Redis 连接失败

检查 Redis 服务是否启动，以及 `.env` 文件中的 Redis 配置是否正确。

### 3. Agent 未就绪

请先配置默认 LLM 配置，Agent 才能正常工作。

## 许可证

MIT License
