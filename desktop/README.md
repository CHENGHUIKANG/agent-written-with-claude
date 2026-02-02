# Agent Desktop Application

基于 Electron + Vue 3 的桌面应用程序，提供完整的 AI Agent 对话和管理功能。

## 功能特性

- ✅ 用户认证（注册/登录）
- ✅ AI 对话聊天
- ✅ MCP 服务器配置管理
- ✅ LLM 配置管理
- ✅ 跨平台支持（Windows/macOS/Linux）
- ✅ 本地数据存储
- ✅ 现代化 UI（Element Plus）

## 技术栈

### 后端
- **Electron 28**: 桌面应用框架
- **Node.js**: 运行时环境
- **electron-store**: 本地数据存储

### 前端
- **Vue 3**: 前端框架
- **Vite**: 构建工具
- **Vue Router**: 路由管理
- **Pinia**: 状态管理
- **Element Plus**: UI 组件库
- **Axios**: HTTP 客户端

### 打包工具
- **electron-builder**: 应用打包工具

## 项目结构

```
desktop/
├── src/
│   ├── main/                    # Electron 主进程
│   │   ├── index.js             # 主进程入口
│   │   └── preload.js           # 预加载脚本
│   └── renderer/                # 渲染进程
│       └── vue-app/             # Vue 应用
│           ├── src/
│           │   ├── api/         # API 接口
│           │   ├── layout/      # 布局组件
│           │   ├── router/      # 路由配置
│           │   ├── stores/      # 状态管理
│           │   ├── views/       # 页面组件
│           │   ├── App.vue      # 根组件
│           │   └── main.js      # 入口文件
│           ├── index.html       # HTML 模板
│           ├── package.json     # Vue 依赖
│           └── vite.config.js   # Vite 配置
├── build/                       # 构建资源（图标等）
├── dist/                        # 打包输出目录
├── package.json                 # Electron 依赖和配置
├── BUILD.md                     # 打包说明文档
└── README.md                    # 本文件
```

## 快速开始

### 环境要求

- Node.js 16+ 
- npm 或 yarn
- 后端服务运行在 `http://localhost:8000`

### 安装依赖

```bash
cd desktop
npm install
cd src/renderer/vue-app
npm install
cd ../../..
```

### 开发模式

```bash
npm run dev
```

这将启动：
- Vue 开发服务器 (http://localhost:5173)
- Electron 应用窗口

### 构建和打包

```bash
# 构建 Vue 应用
npm run build

# 打包 Windows 应用
npm run build:win

# 打包 macOS 应用
npm run build:mac

# 打包 Linux 应用
npm run build:linux
```

详细打包说明请参考 [BUILD.md](./BUILD.md)

## 功能说明

### 1. 用户认证

- **注册**: 创建新用户账号
- **登录**: 使用用户名和密码登录
- **Token 管理**: 自动处理 JWT token

### 2. AI 对话

- **实时对话**: 与 AI Agent 进行实时对话
- **工具调用**: 显示 AI 调用的工具和参数
- **历史记录**: 保存对话历史（本地存储）

### 3. MCP 配置

- **添加服务器**: 配置 MCP 服务器连接
- **编辑配置**: 修改 MCP 服务器参数
- **删除服务器**: 移除不需要的 MCP 服务器
- **测试连接**: 验证 MCP 服务器连接状态

支持的 MCP 类型：
- STDIO: 标准输入输出通信
- STREAMABLE_HTTP: HTTP 协议通信

### 4. LLM 配置

- **添加配置**: 配置 LLM API 连接
- **编辑配置**: 修改 LLM 参数
- **删除配置**: 移除不需要的 LLM 配置
- **默认配置**: 设置默认使用的 LLM

配置参数：
- Provider: Custom / Local
- Model Name: 模型名称
- API Key: API 密钥
- Base URL: API 地址
- Max Tokens: 最大令牌数
- Temperature: 温度参数
- Top P: Top P 参数

## 配置说明

### 后端 API 地址

默认配置为 `http://localhost:8000/api/v1`

如需修改，请编辑 `src/renderer/vue-app/src/api/index.js`：

```javascript
const api = axios.create({
  baseURL: 'http://your-api-server/api/v1',
  // ...
});
```

### Electron 配置

主要配置在 `src/main/index.js`：

```javascript
mainWindow = new BrowserWindow({
  width: 1200,
  height: 800,
  // ...
});
```

## 快捷键

- `Ctrl+N`: 新建对话
- `Ctrl+Q`: 退出应用
- `F11`: 全屏切换
- `Ctrl+Shift+I`: 打开开发者工具

## 开发说明

### 主进程 (Main Process)

位于 `src/main/`，负责：
- 应用窗口管理
- 菜单栏
- 系统托盘
- 本地数据存储
- 与渲染进程通信

### 渲染进程 (Renderer Process)

位于 `src/renderer/vue-app/`，负责：
- UI 渲染
- 用户交互
- API 调用
- 状态管理

### IPC 通信

使用 `contextBridge` 安全地暴露 API 给渲染进程：

```javascript
// preload.js
contextBridge.exposeInMainWorld('electronAPI', {
  store: {
    get: (key) => ipcRenderer.invoke('store-get', key),
    set: (key, value) => ipcRenderer.invoke('store-set', key, value)
  }
});

// Vue 组件中使用
await window.electronAPI.store.set('key', 'value');
```

## 常见问题

### 1. 应用无法连接后端

- 确保后端服务正在运行
- 检查 API 地址配置
- 查看浏览器控制台错误信息

### 2. 打包后应用白屏

- 确保 Vue 应用已构建
- 检查文件路径配置
- 查看开发者工具中的错误

### 3. Token 过期

应用会自动处理 token 过期，跳转到登录页面。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

- 项目地址: https://github.com/yourcompany/agent-app
- 问题反馈: https://github.com/yourcompany/agent-app/issues

---

**注意**: 本应用需要后端服务支持，请确保后端服务正常运行。
