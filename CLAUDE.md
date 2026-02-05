# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 提供在此代码库中工作的指导。

## 项目概述

这是一个带桌面界面的全栈 AI Agent 应用。后端使用 FastAPI 构建，前端是 Electron + Vue 3 桌面应用。系统采用三层架构：决策层 (LLM) → 编排层 (Agent) → 执行层 (工具)，支持内置工具和外部 MCP (Model Context Protocol) 服务。

**仓库地址**: https://github.com/CHENGHUIKANG/agent-written-with-claude

## 常用命令

### 后端 (FastAPI)

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
mysql -u root -p < sql/01-init.sql

# 开发服务器（自动重载）
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产服务器
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# API 文档：http://localhost:8000/docs (Swagger UI) 或 /redoc (ReDoc)
```

### 桌面端 (Electron + Vue 3)

```bash
cd desktop

# 安装依赖（根目录和 vue-app）
npm install
cd src/renderer/vue-app && npm install && cd ../../..

# 开发模式（启动 Vue 开发服务器和 Electron）
npm run dev

# 仅构建 Vue 应用
npm run build

# 打包桌面应用
npm run build:win      # Windows (NSIS 安装包 + 便携版)
npm run build:mac      # macOS (DMG)
npm run build:linux    # Linux (AppImage + deb)

# 单独命令
npm run dev:vue        # 仅 Vue 开发服务器 (http://localhost:5173)
npm run dev:electron   # 仅 Electron
```

## 架构设计

### 三层架构

```
决策层 (LLM)     -> 分析意图，决策工具使用
编排层 (Agent)    -> 路由到工具，管理执行
执行层            -> fastmcp 内置工具 + 外部 MCP 客户端
```

### 核心组件

- **`backend/app/core/agent_executor.py`**: Agent 编排器，每次请求最多 10 次迭代，从 LLM 响应中提取推理内容（支持 `<thought>`、`<reasoning>`、"思考："、"Reasoning:"、"Thought:" 等格式）
- **`backend/app/core/llm_client.py`**: OpenAI SDK 兼容，支持自定义 base_url（vLLM、Ollama），异步带 3 次重试
- **`backend/app/core/tool_manager.py`**: 加载内置 fastmcp 工具，管理外部 MCP 连接（stdio/sse）
- **`backend/app/tools/builtin/`**: 使用 `@mcp.tool()` 装饰器的内置工具：
  - `file_save` - 保存内容到文件
  - `file_read` - 读取文件内容
  - `file_search` - 按模式搜索文件
  - `web_search` - DuckDuckGo 网络搜索

### 数据库结构 (MySQL)

- `users` - 用户账户（bcrypt 密码加密）
- `mcp_servers` - MCP 服务器配置（stdio/sse 类型）
- `llm_configs` - LLM API 配置（含默认选择）

## 项目规则

语言和通信标准定义在 `.trae/` 目录中：

- **代码任务**: 遵循 `@/documents/FASTAPI_PYTHON_RULES.MD`
  - 优先使用函数式、声明式编程
  - 所有函数签名使用类型注解
  - 使用 Pydantic 模型进行输入验证
  - 使用早期返回处理错误
  - I/O 操作使用异步函数
  - 优先使用 lifespan 上下文管理器而非 `@app.on_event`

- **UI/UX 任务**: 参考 `@/documents/UX_RULES.MD`

- **通信**: 根据项目规则，注释、文档字符串和用户交互使用中文

## 重要文件路径

### 入口文件
- `backend/app/main.py` - FastAPI 应用入口
- `desktop/src/main/index.js` - Electron 主进程
- `desktop/src/renderer/vue-app/src/main.js` - Vue 应用入口

### 核心逻辑
- `backend/app/core/agent_executor.py` - Agent 编排器（解释架构时从这里开始）
- `backend/app/core/llm_client.py` - LLM 客户端（支持流式响应）
- `backend/app/core/tool_manager.py` - 工具注册和执行路由

### API 端点
- `backend/app/api/v1/endpoints/agent.py` - 聊天端点（`/chat`、`/chat/stream`）
- `backend/app/api/v1/endpoints/auth.py` - JWT 认证
- `backend/app/api/v1/endpoints/mcp.py` - MCP 服务器配置
- `backend/app/api/v1/endpoints/llm.py` - LLM 配置管理

### 配置文件
- `backend/.env` - 环境变量（数据库、Redis、JWT 密钥）
- `backend/app/core/config.py` - 设置类
- `desktop/package.json` - Electron 构建配置

### 文档
- `.trae/documents/FASTAPI_PYTHON_RULES.MD` - 后端编码规范
- `.trae/documents/UX_RULES.MD` - 前端 UX 指南
- `backend/docs/01-architecture.md` - 架构图
- `backend/docs/02-agent-flow.md` - 执行流程详解
- `backend/API使用文档.md` - 完整 API 参考文档（中文）

## 技术栈

### 后端
- FastAPI 0.109.0, Uvicorn 0.27.0
- SQLAlchemy 2.0.25, aiomysql 0.2.0
- Pydantic 2.5.3 数据验证
- MCP (mcp 1.0.0, fastmcp 0.4.0) 工具协议
- OpenAI SDK 1.10.0 LLM 集成
- python-jose 3.3.0 (JWT), passlib 1.7.4 (bcrypt)
- loguru 0.7.2（日志 - 已配置但未主动使用）

### 前端
- Electron 28.0.0, Vue 3.4.0
- Vite 5.0.11 构建工具
- Vue Router 4.2.5, Pinia 2.1.7
- Element Plus 2.5.4 UI 组件库
- Axios 1.6.5 HTTP 客户端
- electron-store 8.1.0 本地存储

## 开发工作流

1. 启动后端：`cd backend && python -m uvicorn app.main:app --reload`
2. 启动前端：`cd desktop && npm run dev`
3. 访问 API 文档：http://localhost:8000/docs
4. 桌面应用通过 Electron 自动打开

## 已知限制

- **Redis**: 已配置但未实现（0% - JWT 黑名单、会话、缓存功能计划中）
- **对话历史**: 无持久化 - `conversation_history` 参数存在但未使用
- **WebSocket**: 未实现 - 流式响应使用 SSE
- **测试**: 无测试基础设施（无 pytest、无 vitest、无 CI/CD）
- **日志**: loguru 已安装但未统一使用
- **流式与非流式**: 聊天实现结构不一致

## 添加新功能

### 新建内置工具
1. 在 `backend/app/tools/builtin/` 创建文件
2. 使用 fastmcp 的 `@mcp.tool()` 装饰器
3. 启动时工具自动注册到 tool_manager

### 新建 API 端点
1. 在 `backend/app/api/v1/endpoints/` 创建端点文件
2. 在 `backend/app/api/v1/__init__.py` 注册路由（如需要）
3. 在 `backend/app/schemas/` 添加 Pydantic 模型

### 新建前端视图
1. 在 `desktop/src/renderer/vue-app/src/views/` 创建组件
2. 在 `desktop/src/renderer/vue-app/src/router/index.js` 添加路由
3. 使用 Element Plus 组件构建 UI
