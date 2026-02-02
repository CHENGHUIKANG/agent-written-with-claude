# Electron + Vue 桌面应用打包说明

## 准备工作

### 1. 安装依赖

在 `desktop` 目录下运行：

```bash
npm install
cd src/renderer/vue-app
npm install
cd ../../..
```

### 2. 准备图标文件

在 `desktop/build` 目录下放置以下图标文件：

- `icon.ico` - Windows 图标 (256x256)
- `icon.icns` - macOS 图标
- `icon.png` - Linux 图标 (512x512)

如果没有图标文件，可以使用在线工具生成：
- https://icoconvert.com/
- https://cloudconvert.com/png-to-ico

## 开发模式

### 启动开发服务器

```bash
npm run dev
```

这将同时启动：
- Vue 开发服务器 (http://localhost:5173)
- Electron 应用窗口

### 单独启动

```bash
# 启动 Vue 开发服务器
npm run dev:vue

# 启动 Electron
npm run dev:electron
```

## 打包发布

### 1. 构建 Vue 应用

```bash
npm run build
```

这将在 `src/renderer/vue-app/dist` 目录生成构建产物。

### 2. 打包 Electron 应用

#### Windows

```bash
npm run build:win
```

生成的安装包位置：
- `dist/Agent App Setup 1.0.0.exe` - NSIS 安装程序
- `dist/Agent App 1.0.0.exe` - 便携版

#### macOS

```bash
npm run build:mac
```

生成的安装包位置：
- `dist/Agent App-1.0.0.dmg`

#### Linux

```bash
npm run build:linux
```

生成的安装包位置：
- `dist/Agent App-1.0.0.AppImage`
- `dist/agent-desktop-app_1.0.0_amd64.deb`

### 3. 一键打包

```bash
npm run build:electron
```

根据当前操作系统自动打包对应平台。

## 配置说明

### electron-builder 配置

配置文件位于 `desktop/package.json` 的 `build` 字段：

```json
{
  "build": {
    "appId": "com.yourcompany.agentapp",
    "productName": "Agent App",
    "directories": {
      "output": "dist",
      "buildResources": "build"
    },
    "files": [
      "src/main/**/*",
      "src/renderer/vue-app/dist/**/*",
      "package.json"
    ],
    "win": {
      "target": ["nsis", "portable"],
      "icon": "build/icon.ico"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  }
}
```

### 修改配置

1. **应用信息**
   - `appId`: 应用唯一标识符
   - `productName`: 应用显示名称

2. **输出目录**
   - `directories.output`: 安装包输出目录
   - `directories.buildResources`: 资源文件目录（图标等）

3. **打包文件**
   - `files`: 需要打包的文件列表

4. **Windows 配置**
   - `target`: 打包目标（nsis 安装程序、portable 便携版）
   - `icon`: 应用图标

5. **NSIS 安装程序配置**
   - `oneClick`: 是否一键安装
   - `allowToChangeInstallationDirectory`: 允许修改安装目录
   - `createDesktopShortcut`: 创建桌面快捷方式
   - `createStartMenuShortcut`: 创建开始菜单快捷方式

## 常见问题

### 1. 打包后应用无法启动

检查以下几点：
- 确保 Vue 应用已构建：`npm run build`
- 检查 `package.json` 中的 `files` 配置是否正确
- 查看打包日志中的错误信息

### 2. 图标未显示

确保图标文件：
- 位于 `build` 目录
- 文件名正确（icon.ico / icon.icns / icon.png）
- 尺寸符合要求

### 3. 应用体积过大

可以尝试：
- 使用 `electron-builder` 的压缩选项
- 移除不必要的依赖
- 使用 `asar` 压缩（默认启用）

### 4. 开发模式下白屏

检查：
- Vue 开发服务器是否正常运行
- 浏览器控制台是否有错误
- `main.js` 中的 `loadURL` 是否正确

## 发布流程

1. 更新版本号
   ```bash
   # 修改 package.json 中的 version
   "version": "1.0.1"
   ```

2. 构建 Vue 应用
   ```bash
   npm run build
   ```

3. 打包 Electron 应用
   ```bash
   npm run build:win
   ```

4. 测试安装包
   - 在干净的 Windows 系统上测试安装
   - 验证所有功能是否正常

5. 发布
   - 上传安装包到发布平台
   - 更新版本说明

## 自动化部署

可以使用 GitHub Actions 实现自动化构建和发布：

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm install
      - run: npm run build
      - run: npm run build:win
      - uses: softprops/action-gh-release@v1
        with:
          files: dist/*.exe
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 参考资源

- [Electron 官方文档](https://www.electronjs.org/docs)
- [electron-builder 文档](https://www.electron.build/)
- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
