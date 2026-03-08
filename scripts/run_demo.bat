@echo off
chcp 65001 >nul
echo 🎓 AI School - 多Agent学习辅导系统
echo ========================================
for %%i in ("%~dp0..") do set "BASE_DIR=%%~fi"
set "BACKEND_DIR=%BASE_DIR%\backend"

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python3
    pause
    exit /b 1
)

REM 检查依赖
echo 📦 检查Python依赖...
python -c "import crewai" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r "%BACKEND_DIR%\requirements.txt"
)

REM 检查.env文件
if not exist "%BACKEND_DIR%\.env" (
    echo 📝 创建.env文件...
    copy "%BACKEND_DIR%\.env.example" "%BACKEND_DIR%\.env" >nul
    echo ⚠️  请编辑 backend\.env 文件设置你的API密钥
    echo     然后重新运行此脚本
    pause
    exit /b 0
)

REM 选择运行模式
echo.
echo 请选择运行模式:
echo 1. 命令行交互模式
echo 2. Web API模式
echo 3. Docker模式
echo 4. 演示模式（无需API密钥）
echo.

set /p choice=请输入选择 (1-4): 

if "%choice%"=="1" goto :run_cli
if "%choice%"=="2" goto :run_api
if "%choice%"=="3" goto :run_docker
if "%choice%"=="4" goto :run_demo_mode
echo ❌ 无效选择
pause
exit /b 1

:run_cli
echo 🚀 启动命令行交互模式...
set "PYTHONPATH=%BACKEND_DIR%"
python "%BACKEND_DIR%\cli.py"
goto :end

:run_api
echo 🌐 启动Web API模式...
echo API将在 http://localhost:8000 运行
echo 文档: http://localhost:8000/docs
set "PYTHONPATH=%BACKEND_DIR%"
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
goto :end

:run_docker
echo 🐳 启动Docker模式...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Docker，请先安装Docker
    pause
    exit /b 1
)
echo 构建和启动容器...
docker compose -f "%BASE_DIR%\docker-compose.yml" up --build
goto :end

:run_demo_mode
echo 🎭 启动演示模式...
pushd "%~dp0"
python run_local.py
popd
goto :end

:end

pause