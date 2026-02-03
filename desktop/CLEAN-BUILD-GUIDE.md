# Electron 打包清理和构建脚本

## 使用方法

### 方法 1: 使用批处理脚本（Windows）

直接双击运行：
```
desktop\clean-and-build.bat
```

或者在命令行中：
```cmd
cd desktop
clean-and-build.bat
```

### 方法 2: 使用 PowerShell 脚本

在 PowerShell 中运行：
```powershell
cd desktop
.\clean-and-build.ps1
```

如果提示执行策略错误，先运行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 方法 3: 手动执行（推荐）

如果脚本无法运行，可以手动执行以下命令：

#### 步骤 1: 停止 Electron 进程

```powershell
# 查找所有 Electron 相关进程
Get-Process | Where-Object {$_.ProcessName -like "*electron*"} | Format-Table Id, ProcessName, Path

# 强制结束进程
Get-Process -Name "electron" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "Agent App" -ErrorAction SilentlyContinue | Stop-Process -Force
```

#### 步骤 2: 等待进程完全关闭

```powershell
Start-Sleep -Seconds 3
```

#### 步骤 3: 清理 dist 目录

```powershell
if (Test-Path "dist") {
    Remove-Item -Recurse -Force dist
    Write-Host "dist 目录已清理" -ForegroundColor Green
} else {
    Write-Host "dist 目录不存在" -ForegroundColor Yellow
}
```

#### 步骤 4: 重新打包

```powershell
npm run build:win
```

## 常见问题

### 问题 1: 进程无法结束

如果进程无法结束，可以尝试：

```powershell
# 使用管理员权限运行
# 以管理员身份打开 PowerShell，然后运行：
Get-Process -Name "electron" -ErrorAction SilentlyContinue | Stop-Process -Force
```

或者使用 `taskkill` 命令：
```cmd
taskkill /F /IM electron.exe /T
```

### 问题 2: 文件仍被占用

如果文件仍被占用，可以：

1. **重启计算机**
   - 最简单的方法，确保所有进程完全关闭

2. **使用工具解锁文件**
   - 使用 Unlocker 等工具强制解锁文件
   - 下载地址: http://www.emptyloop.com/unlocker/

3. **检查是否有其他程序占用**
   - 使用 Process Explorer 查看
   - 下载地址: https://learn.microsoft.com/sysinternals/downloads/process-explorer

### 问题 3: 打包失败

如果打包仍然失败，检查：

1. **Vue 应用是否已构建**
   ```powershell
   cd src\renderer\vue-app
   npm run build
   ```

2. **检查 dist 目录结构**
   ```powershell
   Get-ChildItem -Recurse dist | Format-Table Name, Length, LastWriteTime
   ```

3. **检查 package.json 配置**
   - 确保 `files` 字段包含正确的路径
   - 确保 `main` 字段指向正确的主进程文件

## 验证打包结果

打包成功后，检查以下内容：

### 1. 检查输出文件

```powershell
Get-ChildItem dist -Filter "*.exe" | Format-Table Name, Length, LastWriteTime
```

应该看到：
- `Agent App Setup 1.0.0.exe` (NSIS 安装程序)
- `Agent App 1.0.0.exe` (便携版)

### 2. 检查文件大小

安装程序通常在 100MB - 200MB 之间。

### 3. 测试安装包

双击 `Agent App Setup 1.0.0.exe` 进行测试安装。

## 自动化清理脚本

如果需要更自动化的清理，可以创建以下脚本：

### PowerShell 版本 (clean-and-build.ps1)

```powershell
# 设置错误处理
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "清理 Electron 打包进程和文件" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 步骤 1: 停止 Electron 进程
Write-Host "[1/4] 停止所有 Electron 进程..." -ForegroundColor Yellow
try {
    Get-Process -Name "electron" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "Agent App" -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "完成." -ForegroundColor Green
} catch {
    Write-Host "没有找到运行中的进程." -ForegroundColor Yellow
}
Write-Host ""

# 步骤 2: 等待进程完全关闭
Write-Host "[2/4] 等待进程完全关闭..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Write-Host "完成." -ForegroundColor Green
Write-Host ""

# 步骤 3: 清理 dist 目录
Write-Host "[3/4] 清理 dist 目录..." -ForegroundColor Yellow
if (Test-Path "dist") {
    Remove-Item -Recurse -Force dist
    Write-Host "dist 目录已删除." -ForegroundColor Green
} else {
    Write-Host "dist 目录不存在，跳过." -ForegroundColor Yellow
}
Write-Host ""

# 步骤 4: 开始打包
Write-Host "[4/4] 开始打包..." -ForegroundColor Yellow
npm run build:win

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "打包完成！" -ForegroundColor Green
Write-Host "安装包位置: dist\" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
```

将此脚本保存为 `clean-and-build.ps1`，然后运行。

## 总结

**快速解决方案**：
1. 关闭所有 Electron 窗口
2. 运行 `taskkill /F /IM electron.exe`
3. 删除 `dist` 目录
4. 重新运行 `npm run build:win`

**如果仍然失败**：
- 重启计算机
- 使用提供的清理脚本
- 检查是否有其他程序占用文件
