@echo off
echo ========================================
echo Electron 打包诊断工具
echo ========================================
echo.

echo [检查 1] Node.js 版本...
node -v
if %errorlevel% neq 0 (
    echo [错误] Node.js 未安装或未添加到 PATH
    pause
    exit /b 1
)
echo.

echo [检查 2] npm 版本...
npm -v
if %errorlevel% neq 0 (
    echo [错误] npm 未安装或未添加到 PATH
    pause
    exit /b 1
)
echo.

echo [检查 3] 当前目录...
cd
echo.

echo [检查 4] package.json 是否存在...
if exist package.json (
    echo [OK] package.json 存在
) else (
    echo [错误] package.json 不存在
    pause
    exit /b 1
)
echo.

echo [检查 5] 依赖是否已安装...
if exist node_modules (
    echo [OK] node_modules 目录存在
) else (
    echo [警告] node_modules 目录不存在，可能需要运行 npm install
)
echo.

echo [检查 6] 主进程文件是否存在...
if exist src\main\index.js (
    echo [OK] src\main\index.js 存在
) else (
    echo [错误] src\main\index.js 不存在
    pause
    exit /b 1
)
echo.

echo [检查 7] Vue 构建产物是否存在...
if exist src\renderer\vue-app\dist\index.html (
    echo [OK] src\renderer\vue-app\dist\index.html 存在
) else (
    echo [错误] Vue 应用未构建，请先运行: npm run build
    pause
    exit /b 1
)
echo.

echo [检查 8] 图标文件是否存在...
if exist build\icon.ico (
    echo [OK] build\icon.ico 存在
) else (
    echo [警告] build\icon.ico 不存在，打包可能失败
)
echo.

echo [检查 9] dist 目录是否存在...
if exist dist (
    echo [警告] dist 目录已存在，可能需要清理
    echo dist 目录内容:
    dir dist /b
    echo.
    echo 是否清理 dist 目录? (Y/N)
    set /p clean=
    if /i "%clean%"=="Y" (
        echo 正在清理 dist 目录...
        rd /s /q dist
        echo dist 目录已清理
    )
) else (
    echo [OK] dist 目录不存在
)
echo.

echo [检查 10] Electron 进程是否运行...
tasklist /FI "IMAGENAME eq electron.exe" 2>nul | find /I /N "electron.exe" >nul
if %errorlevel% equ 0 (
    echo [警告] 发现运行中的 Electron 进程
    echo 正在停止 Electron 进程...
    taskkill /F /IM electron.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo Electron 进程已停止
) else (
    echo [OK] 没有运行中的 Electron 进程
)
echo.

echo ========================================
echo 诊断完成！
echo ========================================
echo.
echo 如果所有检查都通过，可以尝试运行打包命令:
echo   npm run build:win
echo.
echo 如果有错误，请根据上述提示进行修复。
echo.
pause
