# Agent Application API 使用文档

## 目录

- [概述](#概述)
- [认证说明](#认证说明)
- [用户模块](#用户模块)
- [MCP 配置管理](#mcp-配置管理)
- [LLM 配置管理](#llm-配置管理)
- [Agent 核心功能](#agent-核心功能)
- [错误码说明](#错误码说明)

---

## 概述

Agent Application 是一个基于 FastAPI 的后端服务，提供用户管理、MCP 配置、LLM 配置和 Agent 对话功能。

**基础 URL**: `http://localhost:8000`
**API 版本**: `v1`
**完整路径**: `http://localhost:8000/api/v1`

---

## 认证说明

所有需要认证的接口都需要在请求头中携带 JWT Token：

```http
Authorization: Bearer <your_token>
```

获取 Token 的方式：
1. 调用登录接口获取 `access_token`
2. 在后续请求的 `Authorization` 头中携带该 Token

---

## 用户模块

### 1. 用户注册

创建新用户账户。

**接口**: `POST /api/v1/auth/register`

**请求参数**:

```json
{
  "username": "string (3-50字符)",
  "email": "string (可选, 邮箱格式)",
  "password": "string (6-100字符)"
}
```

**响应示例**:

```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "is_active": true,
  "created_at": "2026-01-28T16:24:41",
  "updated_at": "2026-01-28T16:24:41"
}
```

**错误示例**:

```json
{
  "detail": "用户名已存在"
}
```

---

### 2. 用户登录

使用用户名和密码登录，获取 JWT Token。

**接口**: `POST /api/v1/auth/login`

**请求参数**:

```json
{
  "username": "string",
  "password": "string"
}
```

**响应示例**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**错误示例**:

```json
{
  "detail": "用户名或密码错误"
}
```

---

### 3. 获取当前用户信息

获取当前登录用户的详细信息。

**接口**: `GET /api/v1/auth/me`

**认证**: 需要

**响应示例**:

```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "is_active": true,
  "created_at": "2026-01-28T16:24:41",
  "updated_at": "2026-01-28T16:24:41"
}
```

---

### 4. 更新当前用户信息

更新当前登录用户的信息。

**接口**: `PUT /api/v1/auth/me`

**认证**: 需要

**请求参数**:

```json
{
  "email": "string (可选)",
  "password": "string (可选, 6-100字符)"
}
```

**响应示例**:

```json
{
  "id": 1,
  "username": "testuser",
  "email": "newemail@example.com",
  "is_active": true,
  "created_at": "2026-01-28T16:24:41",
  "updated_at": "2026-01-28T16:26:43"
}
```

---

### 5. 删除当前用户

删除当前登录用户的账户。

**接口**: `DELETE /api/v1/auth/me`

**认证**: 需要

**响应示例**:

```json
{
  "message": "用户已删除",
  "success": true
}
```

---

### 6. 获取用户信息（users 路由）

获取当前用户信息的另一个接口（功能与 `/auth/me` 相同）。

**接口**: `GET /api/v1/users/me`

**认证**: 需要

**响应示例**: 同 `/api/v1/auth/me`

---

## MCP 配置管理

### 1. 创建 MCP 服务器

添加新的 MCP 服务器配置。

**接口**: `POST /api/v1/mcp/servers`

**认证**: 需要

**请求参数**:

```json
{
  "name": "string (1-100字符)",
  "description": "string (可选)",
  "server_type": "string (stdio 或 sse)",
  "connection_params": {
    "url": "string (sse 类型)",
    "command": ["string"] (stdio 类型),
    "env": {
      "key": "value"
    }
  }
}
```

**connection_params 示例**:

SSE 类型:
```json
{
  "url": "https://mcp.amap.com/sse?key=your_api_key"
}
```

STDIO 类型:
```json
{
  "command": ["python", "path/to/server.py"],
  "env": {
    "API_KEY": "your_api_key"
  }
}
```

**响应示例**:

```json
{
  "id": 1,
  "user_id": 1,
  "name": "高德地图MCP",
  "description": "高德地图MCP服务器",
  "server_type": "sse",
  "connection_params": {
    "url": "https://mcp.amap.com/sse?key=8b76c70c33ddb1196a486b5919589c36"
  },
  "status": "active",
  "created_at": "2026-01-28T17:26:49",
  "updated_at": "2026-01-28T17:26:49"
}
```

---

### 2. 获取 MCP 服务器列表

获取当前用户的所有 MCP 服务器配置。

**接口**: `GET /api/v1/mcp/servers`

**认证**: 需要

**响应示例**:

```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "高德地图MCP",
    "description": "高德地图MCP服务器",
    "server_type": "sse",
    "connection_params": {
      "url": "https://mcp.amap.com/sse?key=..."
    },
    "status": "active",
    "created_at": "2026-01-28T17:26:49",
    "updated_at": "2026-01-28T17:26:49"
  }
]
```

---

### 3. 获取指定 MCP 服务器

获取指定 ID 的 MCP 服务器配置。

**接口**: `GET /api/v1/mcp/servers/{server_id}`

**认证**: 需要

**路径参数**:
- `server_id`: MCP 服务器 ID

**响应示例**: 同创建接口的响应

---

### 4. 更新 MCP 服务器

更新指定的 MCP 服务器配置。

**接口**: `PUT /api/v1/mcp/servers/{server_id}`

**认证**: 需要

**路径参数**:
- `server_id`: MCP 服务器 ID

**请求参数**:

```json
{
  "name": "string (可选)",
  "description": "string (可选)",
  "connection_params": "object (可选)",
  "status": "string (可选, active 或 inactive)"
}
```

**响应示例**: 同创建接口的响应

---

### 5. 删除 MCP 服务器

删除指定的 MCP 服务器配置。

**接口**: `DELETE /api/v1/mcp/servers/{server_id}`

**认证**: 需要

**路径参数**:
- `server_id`: MCP 服务器 ID

**响应示例**:

```json
{
  "message": "MCP服务器已删除",
  "success": true
}
```

---

### 6. 测试 MCP 服务器连接

测试 MCP 服务器连接是否正常。

**接口**: `POST /api/v1/mcp/servers/{server_id}/test`

**认证**: 需要

**路径参数**:
- `server_id`: MCP 服务器 ID

**响应示例**:

```json
{
  "success": true,
  "message": "MCP连接测试暂未实现",
  "tools_found": 0
}
```

---

## LLM 配置管理

### 1. 创建 LLM 配置

添加新的 LLM 配置。

**接口**: `POST /api/v1/llm/configs`

**认证**: 需要

**请求参数**:

```json
{
  "provider": "string (openai, anthropic, custom)",
  "model_name": "string (1-100字符)",
  "api_key": "string (可选)",
  "base_url": "string (可选, 自定义端点)",
  "max_tokens": "integer (1-32768, 默认4096)",
  "temperature": "number (0.0-2.0, 默认0.7)",
  "top_p": "number (0.0-1.0, 默认1.0)",
  "is_default": "boolean (是否为默认配置)"
}
```

**provider 说明**:
- `openai`: OpenAI 官方 API
- `anthropic`: Anthropic Claude API
- `custom`: 自定义端点（如本地部署的 vLLM、Ollama 等）

**base_url 示例**:
- OpenAI: `https://api.openai.com/v1`
- 本地 vLLM: `http://192.168.20.68:3000/v1/`
- 本地 Ollama: `http://localhost:11434/v1`

**响应示例**:

```json
{
  "id": 1,
  "user_id": 1,
  "provider": "custom",
  "model_name": "QwQ-32B",
  "api_key": "dummy",
  "base_url": "http://192.168.20.68:3000/v1/",
  "max_tokens": 8192,
  "temperature": 0.7,
  "top_p": 1.0,
  "is_default": true,
  "created_at": "2026-01-28T18:03:18",
  "updated_at": "2026-01-28T18:03:18"
}
```

**注意**: 当设置 `is_default: true` 时，会将该用户的其他配置设为非默认。

---

### 2. 获取 LLM 配置列表

获取当前用户的所有 LLM 配置。

**接口**: `GET /api/v1/llm/configs`

**认证**: 需要

**响应示例**:

```json
[
  {
    "id": 1,
    "user_id": 1,
    "provider": "custom",
    "model_name": "QwQ-32B",
    "api_key": "dummy",
    "base_url": "http://192.168.20.68:3000/v1/",
    "max_tokens": 8192,
    "temperature": 0.7,
    "top_p": 1.0,
    "is_default": true,
    "created_at": "2026-01-28T18:03:18",
    "updated_at": "2026-01-28T18:03:18"
  },
  {
    "id": 2,
    "user_id": 1,
    "provider": "openai",
    "model_name": "gpt-4-turbo",
    "api_key": "sk-test",
    "base_url": null,
    "max_tokens": 4096,
    "temperature": 0.5,
    "top_p": 0.9,
    "is_default": false,
    "created_at": "2026-01-28T17:51:05",
    "updated_at": "2026-01-28T17:51:05"
  }
]
```

**排序规则**: 默认配置优先，然后按创建时间倒序。

---

### 3. 获取默认 LLM 配置

获取当前用户的默认 LLM 配置。

**接口**: `GET /api/v1/llm/configs/default`

**认证**: 需要

**响应示例**: 同创建接口的响应

**错误示例**:

```json
{
  "detail": "默认LLM配置不存在"
}
```

---

### 4. 获取指定 LLM 配置

获取指定 ID 的 LLM 配置。

**接口**: `GET /api/v1/llm/configs/{config_id}`

**认证**: 需要

**路径参数**:
- `config_id`: LLM 配置 ID

**响应示例**: 同创建接口的响应

---

### 5. 更新 LLM 配置

更新指定的 LLM 配置。

**接口**: `PUT /api/v1/llm/configs/{config_id}`

**认证**: 需要

**路径参数**:
- `config_id`: LLM 配置 ID

**请求参数**:

```json
{
  "provider": "string (可选)",
  "model_name": "string (可选)",
  "api_key": "string (可选)",
  "base_url": "string (可选)",
  "max_tokens": "integer (可选)",
  "temperature": "number (可选)",
  "top_p": "number (可选)",
  "is_default": "boolean (可选)"
}
```

**响应示例**: 同创建接口的响应

**注意**: 当设置 `is_default: true` 时，会将该用户的其他配置设为非默认。

---

### 6. 删除 LLM 配置

删除指定的 LLM 配置。

**接口**: `DELETE /api/v1/llm/configs/{config_id}`

**认证**: 需要

**路径参数**:
- `config_id`: LLM 配置 ID

**响应示例**:

```json
{
  "message": "LLM配置已删除",
  "success": true
}
```

---

## Agent 核心功能

### 1. Agent 聊天

发送消息给 Agent，获取 AI 响应。

**接口**: `POST /api/v1/agent/chat`

**认证**: 需要

**请求参数**:

```json
{
  "message": "string (用户消息)",
  "stream": "boolean (是否流式响应, 默认false)",
  "conversation_id": "integer (可选, 对话ID)"
}
```

**响应示例**:

```json
{
  "content": "你好！有什么我可以帮你的吗？",
  "tool_calls": null,
  "finish_reason": "stop",
  "usage": {
    "prompt_tokens": 92,
    "completion_tokens": 45,
    "total_tokens": 137
  }
}
```

**tool_calls 示例**:

```json
{
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "web_search",
        "arguments": "{\"query\": \"人工智能 最新新闻\"}"
      }
    }
  ]
}
```

**finish_reason 说明**:
- `stop`: 正常完成
- `length`: 达到最大 token 限制
- `tool_calls`: 需要调用工具

---

### 2. Agent 流式聊天

发送消息给 Agent，流式返回 AI 响应。

**接口**: `POST /api/v1/agent/chat/stream`

**认证**: 需要

**请求参数**: 同聊天接口

**响应**: 流式文本响应

**响应头**:
```
Content-Type: text/event-stream
Cache-Control: no-cache
X-Accel-Buffering: no
```

**使用示例**:

JavaScript (fetch):
```javascript
const response = await fetch('http://localhost:8000/api/v1/agent/chat/stream', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: '你好',
    stream: true
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const chunk = decoder.decode(value);
  console.log(chunk);
}
```

Python (httpx):
```python
import httpx
import asyncio

async def stream_chat():
    async with httpx.AsyncClient() as client:
        async with client.stream(
            'POST',
            'http://localhost:8000/api/v1/agent/chat/stream',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json={
                'message': '你好',
                'stream': True
            }
        ) as response:
            async for chunk in response.aiter_bytes():
                print(chunk.decode())
```

---

### 3. Agent 状态

检查 Agent 是否就绪（是否配置了默认 LLM）。

**接口**: `GET /api/v1/agent/status`

**认证**: 需要

**响应示例** (就绪):

```json
{
  "message": "Agent 就绪，使用模型: QwQ-32B",
  "success": true
}
```

**响应示例** (未就绪):

```json
{
  "message": "Agent 未就绪，请先配置默认 LLM",
  "success": false
}
```

---

## 错误码说明

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或 Token 无效 |
| 403 | 权限不足或用户被禁用 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 常见错误信息

| 错误信息 | 说明 | 解决方案 |
|----------|------|----------|
| 用户名已存在 | 注册时用户名已被使用 | 更换用户名 |
| 邮箱已被使用 | 注册时邮箱已被使用 | 更换邮箱 |
| 用户名或密码错误 | 登录凭证错误 | 检查用户名和密码 |
| 无法验证凭据 | Token 无效或过期 | 重新登录获取新 Token |
| 用户已被禁用 | 账户被禁用 | 联系管理员 |
| 请先配置默认 LLM | Agent 功能需要 LLM 配置 | 先创建默认 LLM 配置 |
| MCP服务器不存在 | 指定的 MCP 服务器不存在 | 检查服务器 ID |
| LLM配置不存在 | 指定的 LLM 配置不存在 | 检查配置 ID |

---

## 完整使用示例

### PowerShell 示例

```powershell
# 1. 用户登录
$loginBody = @{username="testuser";password="password123"} | ConvertTo-Json
$loginResponse = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/auth/login" -ContentType "application/json" -Body $loginBody
$token = $loginResponse.access_token

# 2. 创建 LLM 配置
$headers = @{Authorization = "Bearer $token"}
$llmBody = @{
    provider="custom"
    model_name="QwQ-32B"
    base_url="http://192.168.20.68:3000/v1/"
    api_key="dummy"
    max_tokens=8192
    temperature=0.7
    top_p=1.0
    is_default=$true
} | ConvertTo-Json
$llmResponse = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/llm/configs" -Headers $headers -ContentType "application/json" -Body $llmBody

# 3. Agent 聊天
$chatBody = @{message="你好，请介绍一下你自己"} | ConvertTo-Json
$chatResponse = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/agent/chat" -Headers $headers -ContentType "application/json" -Body $chatBody
$chatResponse.content
```

### cURL 示例

```bash
# 1. 用户登录
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# 2. 创建 LLM 配置
curl -X POST "http://localhost:8000/api/v1/llm/configs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider":"custom",
    "model_name":"QwQ-32B",
    "base_url":"http://192.168.20.68:3000/v1/",
    "api_key":"dummy",
    "max_tokens":8192,
    "temperature":0.7,
    "top_p":1.0,
    "is_default":true
  }'

# 3. Agent 聊天
curl -X POST "http://localhost:8000/api/v1/agent/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"你好，请介绍一下你自己"}'
```

### JavaScript/Fetch 示例

```javascript
// 1. 用户登录
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'testuser',
    password: 'password123'
  })
});
const { access_token } = await loginResponse.json();

// 2. 创建 LLM 配置
const llmResponse = await fetch('http://localhost:8000/api/v1/llm/configs', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    provider: 'custom',
    model_name: 'QwQ-32B',
    base_url: 'http://192.168.20.68:3000/v1/',
    api_key: 'dummy',
    max_tokens: 8192,
    temperature: 0.7,
    top_p: 1.0,
    is_default: true
  })
});

// 3. Agent 聊天
const chatResponse = await fetch('http://localhost:8000/api/v1/agent/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: '你好，请介绍一下你自己'
  })
});
const { content, usage } = await chatResponse.json();
console.log(content);
```

---

## 附录

### A. 交互式 API 文档

启动服务后，可以通过以下地址访问交互式 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### B. 数据库表结构

- `users`: 用户表
- `mcp_servers`: MCP 服务器配置表
- `llm_configs`: LLM 配置表

### C. 技术栈

- **Web 框架**: FastAPI
- **ORM**: SQLAlchemy
- **数据库**: MySQL
- **认证**: JWT
- **LLM 客户端**: OpenAI SDK (支持自定义端点)

---

## 更新日志

- **v1.0.0** (2026-01-28)
  - 初始版本
  - 实现用户模块（注册、登录、CRUD）
  - 实现 MCP 配置管理（CRUD）
  - 实现 LLM 配置管理（CRUD）
  - 实现 Agent 核心功能（聊天、流式聊天、状态）
