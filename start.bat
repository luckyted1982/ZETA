@echo off
chcp 65001 >nul
echo ============================================
echo  AI科创企业评测系统 - 一键启动脚本
echo ============================================
echo.

set BACKEND_DIR=D:\工作\AI Infra产业创新中心\嘉创\科技服务产品体系\ai-evaluation-platform\backend
set FRONTEND_DIR=D:\工作\AI Infra产业创新中心\嘉创\科技服务产品体系\ai-evaluation-platform\frontend
set NODE_DIR=C:\Users\22048\.stepfun\runtimes\node\install_1769614304588_3rd5p4s8i1d\node-v22.18.0-win-x64
set PORT=8001
set FRONTEND_PORT=3001

:: 检查后端端口是否被占用
netstat -ano | findstr :%PORT% >nul
if %errorlevel% == 0 (
    echo [WARN] 端口 %PORT% 已被占用，尝试停止现有进程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT%') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 >nul
)

echo [1/4] 正在启动后端服务...
echo        路径: %BACKEND_DIR%
echo        端口: %PORT%
start "AI评测后端" cmd /c "cd /d %BACKEND_DIR% && venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port %PORT% --reload && pause"

timeout /t 4 >nul

echo [2/4] 后端健康检查...
curl -s http://localhost:%PORT%/health >nul
if %errorlevel% == 0 (
    echo        [OK] 后端服务已就绪
) else (
    echo        [WARN] 后端可能仍在启动中，请稍候...
)

echo.
echo [3/4] 正在启动前端服务...
echo        路径: %FRONTEND_DIR%
echo        端口: %FRONTEND_PORT% (或自动分配的端口)
start "AI评测前端" cmd /c "cd /d %FRONTEND_DIR% && %NODE_DIR%\npx vite --host 0.0.0.0 --port %FRONTEND_PORT% && pause"

timeout /t 3 >nul

echo [4/4] 前端健康检查...
curl -s http://localhost:%FRONTEND_PORT% >nul
if %errorlevel% == 0 (
    echo        [OK] 前端服务已就绪
) else (
    echo        [WARN] 前端可能仍在启动中，请稍候...
)

echo.
echo ============================================
echo  启动完成！
echo ============================================
echo  前端访问: http://localhost:%FRONTEND_PORT%
echo  后端API:  http://localhost:%PORT%
echo  API文档:  http://localhost:%PORT%/docs
echo  健康检查: http://localhost:%PORT%/health
echo.
echo  按任意键关闭此窗口（服务将继续运行）
echo ============================================
pause >nul
