@echo off
chcp 65001 >nul
echo ============================================
echo  AI科创企业评测系统 - 停止脚本
echo ============================================
echo.

:: 查找并停止后端 Python 进程（uvicorn）
echo [1/2] 正在查找后端进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    echo        发现进程 PID: %%a，正在停止...
    taskkill /F /PID %%a >nul 2>&1
)

:: 查找并停止前端 Node 进程（vite）
echo [2/2] 正在查找前端进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001') do (
    echo        发现进程 PID: %%a，正在停止...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ============================================
echo  已停止所有服务！
echo ============================================
timeout /t 3 >nul
