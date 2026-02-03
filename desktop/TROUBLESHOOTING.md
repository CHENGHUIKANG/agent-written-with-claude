# Electron 开发环境故障排除

## 问题：Electron 启动但页面空白

### 现象
- Vue 开发服务器正常运行（http://localhost:5173 可以访问）
- Electron 窗口启动成功
- 但 Electron 窗口中显示空白页面

### 可能的原因

1. **Vue 开发服务器未完全启动**
   - Electron 在 Vue 服务器准备好之前就尝试加载页面

2. **开发环境变量未设置**
   - `process.env.NODE_ENV` 未正确设置
   - Electron 无法判断是否为开发模式

3. **端口配置不匹配**
   - Vue 服务器端口不是 5173
   - Electron 加载了错误的 URL

4. **窗口加载时机过早**
   - 窗口在 Vue 服务器准备好之前就显示

### 解决方案

#### 方案一：使用修复后的代码（已应用）

已修复以下文件：

1. **src/main/index.js**
   - 添加了 `isDevelopment()` 函数，更准确地判断开发模式
   - 添加了加载失败的错误处理和重试机制
   - 添加了详细的控制台日志输出
   - 添加了 `did-fail-load` 事件监听

2. **package.json**
   - 添加了 `wait-on` 工具，等待 Vue 服务器启动
   - 添加了 `cross-env` 工具，跨平台设置环境变量
   - 修改了 `dev` 脚本，确保 Vue 服务器先启动

#### 方案二：重新安装依赖

```bash
cd desktop
npm install
```

确保安装了以下依赖：
- `cross-env`: 跨平台环境变量设置
- `wait-on`: 等待服务启动

#### 方案三：手动启动调试

如果 `npm run dev` 仍然有问题，可以手动分步启动：

**步骤 1: 启动 Vue 开发服务器**

```bash
cd desktop/src/renderer/vue-app
npm run dev
```

等待看到以下输出：
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**步骤 2: 在浏览器中测试**

打开浏览器访问 `http://localhost:5173`，确保 Vue 页面正常显示。

**步骤 3: 启动 Electron**

在新的终端窗口中运行：

```bash
cd desktop
set ELECTRON_IS_DEV=true
electron .
```

或者在 PowerShell 中：

```powershell
cd desktop
$env:ELECTRON_IS_DEV="true"
electron .
```

**步骤 4: 查看控制台输出**

Electron 窗口会自动打开开发者工具，查看控制台输出：

- 应该看到 `Development mode: true`
- 应该看到 `Loading from: http://localhost:5173`
- 如果有错误，查看错误信息

#### 方案四：检查端口占用

确保 5173 端口没有被其他程序占用：

**Windows:**
```powershell
netstat -ano | findstr :5173
```

如果端口被占用，可以：
1. 杀死占用端口的进程
2. 或修改 Vite 配置使用其他端口

修改 `src/renderer/vue-app/vite.config.js`：
```javascript
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5174,  // 改为其他端口
    host: '0.0.0.0'
  }
});
```

同时修改 `src/main/index.js`：
```javascript
if (isDev) {
  mainWindow.loadURL('http://localhost:5174');  // 改为对应端口
}
```

#### 方案五：检查防火墙

确保防火墙允许：
- Node.js 访问网络
- Electron 访问 localhost

### 调试技巧

#### 1. 查看详细日志

修改 `src/main/index.js`，添加更多日志：

```javascript
console.log('App path:', app.getAppPath());
console.log('User data:', app.getPath('userData'));
console.log('Is packaged:', app.isPackaged);
console.log('NODE_ENV:', process.env.NODE_ENV);
console.log('ELECTRON_IS_DEV:', process.env.ELECTRON_IS_DEV);
```

#### 2. 检查网络请求

在 Electron 开发者工具的 Network 标签中：
- 查看是否有失败的请求
- 检查请求的 URL 是否正确
- 查看响应状态码

#### 3. 检查控制台错误

在 Electron 开发者工具的 Console 标签中：
- 查看是否有 JavaScript 错误
- 查看是否有资源加载失败
- 查看是否有 CORS 错误

### 常见错误及解决方法

#### 错误 1: `ERR_CONNECTION_REFUSED`

**原因**: Vue 开发服务器未启动或端口错误

**解决**:
1. 确保 Vue 开发服务器正在运行
2. 检查端口配置是否正确
3. 检查防火墙设置

#### 错误 2: `ERR_FILE_NOT_FOUND`

**原因**: 生产环境文件路径错误

**解决**:
1. 确保 `npm run build` 已执行
2. 检查 `dist/index.html` 文件是否存在
3. 检查 `main.js` 中的文件路径是否正确

#### 错误 3: 页面空白但无错误

**原因**: Vue 应用未正确挂载

**解决**:
1. 检查 `src/renderer/vue-app/src/main.js` 中的 `app.mount('#app')`
2. 检查 `index.html` 中是否有 `<div id="app"></div>`
3. 检查浏览器控制台是否有 Vue 相关错误

### 验证修复

修复后，按以下步骤验证：

1. **停止所有进程**
   - 关闭 Electron 窗口
   - 停止 Vue 开发服务器（Ctrl+C）

2. **重新启动**
   ```bash
   cd desktop
   npm run dev
   ```

3. **检查输出**
   - 应该看到 Vue 服务器启动成功
   - 应该看到 Electron 窗口打开
   - 应该看到页面正常显示

4. **测试功能**
   - 尝试登录
   - 尝试发送消息
   - 检查所有功能是否正常

### 如果问题仍然存在

请提供以下信息以便进一步诊断：

1. **控制台输出**
   - Vue 开发服务器的完整输出
   - Electron 窗口的控制台输出

2. **网络请求**
   - Electron 开发者工具 Network 标签中的请求列表

3. **系统信息**
   - 操作系统版本
   - Node.js 版本 (`node -v`)
   - npm 版本 (`npm -v`)
   - Electron 版本

### 联系支持

如果以上方法都无法解决问题，请：
1. 记录详细的错误信息
2. 截图控制台输出
3. 提供系统环境信息
4. 提交 Issue 或联系技术支持
