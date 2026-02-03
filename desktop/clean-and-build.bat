@echo off
echo ========================================
echo 清理 Electron 打包进程和文件
echo ========================================
echo.

echo [1/4] 停止所有 Electron 进程...
taskkill /F /IM electron.exe 2>nul
taskkill /F /IM "Agent App.exe" 2>nul
echo 完成.
echo.

echo [2/4] 等待进程完全关闭...
timeout /t 2 /nobreak >nul
echo 完成.
echo.

echo [3/4] 清理 dist 目录...
if exist dist (
    rd /s /q dist
    echo dist 目录已删除.
) else (
    echo dist 目录不存在，跳过.
)
echo.

echo [4/4] 开始打包...
call npm run build:win

echo.
echo ========================================
echo 打包完成！
echo 安装包位置: dist\
echo ========================================
pause
