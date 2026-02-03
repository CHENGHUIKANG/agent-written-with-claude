@echo off
echo ========================================
echo 重新构建和打包
echo ========================================
echo.

echo [1/3] 重新构建 Vue 应用...
cd src\renderer\vue-app
call npm run build
if %errorlevel% neq 0 (
    echo [错误] Vue 应用构建失败
    pause
    exit /b 1
)
echo.
echo 构建完成！
echo.

echo [2/3] 清理 dist 目录...
cd ..\..\..
if exist dist (
    rd /s /q dist
    echo dist 目录已清理
) else (
    echo dist 目录不存在，跳过
)
echo.

echo [3/3] 重新打包...
call npm run build:win
if %errorlevel% neq 0 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 重新构建和打包完成！
echo 安装包位置: dist\
echo ========================================
pause
