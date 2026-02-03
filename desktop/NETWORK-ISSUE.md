# 网络连接问题解决方案

## 问题描述

执行 `npm run build:win` 时出现网络连接错误：

```
dial tcp 20.205.243.166:443: connectex: A connection attempt failed
Get "https://github.com/electron-userland/electron-builder-binaries/releases/download/winCodeSign-2.6.0/winCodeSign-2.6.0.7z"
```

## 原因分析

electron-builder 在打包 Windows 应用时，会尝试下载 `winCodeSign` 工具用于代码签名。由于网络原因（防火墙、代理、GitHub 访问受限等），导致无法下载该工具。

## 解决方案

### 方案 1：禁用代码签名（推荐，已应用）

已在 `package.json` 中添加以下配置：

```json
"win": {
  "target": ["nsis", "portable"],
  "icon": "build/icon.ico",
  "sign": null,                    // 禁用代码签名
  "signAndEditExecutable": false     // 禁用可执行文件签名
}
```

**优点**：
- ✅ 不需要网络连接
- ✅ 打包速度快
- ✅ 适合开发和测试

**缺点**：
- ⚠️ 安装时可能显示"未知发布者"警告
- ⚠️ Windows Defender 可能误报

### 方案 2：配置代理（如果需要代码签名）

如果需要代码签名，可以配置代理：

#### 方法 A：设置环境变量

```powershell
# HTTP 代理
$env:HTTP_PROXY="http://your-proxy:port"
$env:HTTPS_PROXY="http://your-proxy:port"

# 然后运行打包
npm run build:win
```

#### 方法 B：使用 .npmrc 文件

在 `desktop` 目录下创建 `.npmrc` 文件：

```ini
proxy=http://your-proxy:port
https-proxy=http://your-proxy:port
```

### 方案 3：手动下载工具

如果 GitHub 无法访问，可以手动下载：

1. **下载 winCodeSign 工具**
   - 访问：https://github.com/electron-userland/electron-builder-binaries/releases
   - 下载：winCodeSign-2.6.0.7z
   - 解压到：`%LOCALAPPDATA%\electron-builder\Cache\winCodeSign\2.6.0\`

2. **设置缓存目录**
   ```powershell
   # 创建缓存目录
   mkdir "$env:LOCALAPPDATA\electron-builder\Cache\winCodeSign\2.6.0" -Force

   # 将下载的文件复制到该目录
   ```

### 方案 4：使用镜像源

如果在中国大陆，可以使用镜像：

```powershell
# 设置 GitHub 镜像
$env:ELECTRON_MIRROR="https://npmmirror.com/mirrors/electron/"
$env:ELECTRON_BUILDER_BINARIES_MIRROR="https://npmmirror.com/mirrors/electron-builder-binaries/"

# 运行打包
npm run build:win
```

## 立即解决

### 步骤 1：重新运行打包

由于已经修改了 `package.json`，直接运行：

```powershell
cd desktop
npm run build:win
```

### 步骤 2：验证结果

打包成功后，应该看到：

```
  • building        target=nsis file=dist\Agent App Setup 1.0.0.exe
  • building        target=portable file=dist\Agent App 1.0.0.exe
```

### 步骤 3：测试安装包

1. 双击 `dist\Agent App Setup 1.0.0.exe`
2. 如果提示"未知发布者"，点击"更多信息" -> "仍要运行"
3. 完成安装

## 关于代码签名的说明

### 什么是代码签名？

代码签名是 Windows 的一项安全功能，用于验证软件的发布者身份。

### 为什么需要代码签名？

- ✅ 避免安装时的安全警告
- ✅ 提高用户信任度
- ✅ 防止恶意软件冒充

### 什么时候需要代码签名？

- **开发阶段**：不需要
- **内部测试**：不需要
- **公开发布**：建议使用

### 如何获取代码签名证书？

1. **购买证书**
   - DigiCert: https://www.digicert.com/
   - GlobalSign: https://www.globalsign.com/
   - Sectigo: https://sectigo.com/

2. **证书类型**
   - OV (Organization Validation): 适合企业
   - EV (Extended Validation): 最高级别

3. **配置证书**

在 `package.json` 中添加：

```json
"win": {
  "certificateFile": "path/to/certificate.pfx",
  "certificatePassword": "your-password"
}
```

## 常见问题

### Q1: 禁用代码签名后，安装时显示警告怎么办？

**A**: 这是正常的。用户可以：
1. 点击"更多信息"
2. 点击"仍要运行"
3. 完成安装

### Q2: 如何永久解决网络问题？

**A**: 可以：
1. 配置系统代理
2. 使用镜像源
3. 购买代码签名证书

### Q3: 打包后的应用会被杀毒软件误报吗？

**A**: 可能会。解决方案：
1. 将应用添加到白名单
2. 获取代码签名证书
3. 上传到杀毒软件厂商进行扫描

### Q4: 如何验证打包是否成功？

**A**: 检查以下几点：
1. `dist` 目录中是否有 `.exe` 文件
2. 文件大小是否正常（100-200MB）
3. 双击 `.exe` 文件是否能正常安装

## 下一步

1. **重新运行打包**
   ```powershell
   npm run build:win
   ```

2. **测试安装包**
   - 双击 `dist\Agent App Setup 1.0.0.exe`
   - 完成安装流程

3. **测试应用**
   - 启动应用
   - 测试所有功能

## 总结

**快速解决方案**：
- ✅ 已禁用代码签名
- ✅ 直接运行 `npm run build:win` 即可

**长期解决方案**：
- 📋 配置网络代理或镜像源
- 📋 购买代码签名证书

**如果仍有问题**：
- 🔍 检查防火墙设置
- 🔍 尝试使用代理
- 🔍 联系技术支持
