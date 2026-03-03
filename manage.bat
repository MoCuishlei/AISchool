@echo off
chcp 65001 >nul
setlocal

set PROJECT_NAME=AISchool
set COMPOSE_FILE=docker-compose.yml
set FRONTEND_DIR=frontend

:: ========== 帮助信息 ==========
if "%1"=="" goto :usage
if "%1"=="help" goto :usage
if "%1"=="-h" goto :usage

:: ========== 检查 Docker ==========
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未安装或未运行，请先启动 Docker Desktop
    exit /b 1
)

docker compose version >nul 2>&1
if errorlevel 1 (
    docker-compose --version >nul 2>&1
    if errorlevel 1 (
        echo [错误] docker compose 不可用，请升级 Docker 或安装 docker-compose
        exit /b 1
    )
    set COMPOSE_CMD=docker-compose
) else (
    set COMPOSE_CMD=docker compose
)

:: ========== 路由命令 ==========
if "%1"=="start"    goto :start
if "%1"=="stop"     goto :stop
if "%1"=="restart"  goto :restart
if "%1"=="status"   goto :status
if "%1"=="logs"     goto :logs
if "%1"=="build"    goto :build
if "%1"=="frontend" goto :frontend
goto :usage

:: ========== start ==========
:start
echo 🚀 启动所有服务 (%PROJECT_NAME%)...

:: 检查 .env
if not exist ".env" (
    if exist ".env.example" (
        echo ⚠️  未检测到 .env 文件，正在从 .env.example 复制...
        copy .env.example .env >nul
        echo ⚠️  请编辑 .env 文件配置 API 密钥后重新运行
        exit /b 0
    ) else (
        echo [错误] 缺少 .env 文件，无法启动
        exit /b 1
    )
)

:: 启动后端 Docker 服务
echo 🐳 启动后端服务 (db + redis + backend)...
%COMPOSE_CMD% -f %COMPOSE_FILE% up --build -d
if errorlevel 1 (
    echo [错误] 后端服务启动失败，请检查上方日志
    exit /b 1
)

:: 启动前端
call :frontend_start

echo.
echo ✅ 所有服务已启动！
echo    前端界面 : http://localhost:3000
echo    后端 API : http://localhost:8000
echo    API 文档 : http://localhost:8000/docs
echo    PostgreSQL: localhost:5432
echo    Redis     : localhost:6379
echo.
echo 提示: 前端已在新终端窗口中运行
echo 提示: 使用 manage.bat logs backend 查看后端日志
goto :end

:: ========== stop ==========
:stop
echo 🛑 停止所有服务...

:: 停止后端
%COMPOSE_CMD% -f %COMPOSE_FILE% down

:: 停止前端（杀掉占用 3000 端口的进程）
echo 停止前端开发服务器 (端口 3000)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000 " ^| find "LISTENING" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo ✅ 所有服务已停止
goto :end

:: ========== restart ==========
:restart
echo 🔄 重启所有服务...
%COMPOSE_CMD% -f %COMPOSE_FILE% down
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000 " ^| find "LISTENING" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
%COMPOSE_CMD% -f %COMPOSE_FILE% up --build -d
call :frontend_start
echo ✅ 所有服务已重启
goto :end

:: ========== status ==========
:status
echo 📊 当前服务状态：
echo.
echo [后端 Docker 服务]
%COMPOSE_CMD% -f %COMPOSE_FILE% ps
echo.
echo [前端开发服务器 (端口 3000)]
netstat -aon | find ":3000 " | find "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo   ❌ 前端未运行
) else (
    echo   ✅ 前端运行中 ^(http://localhost:3000^)
)
goto :end

:: ========== logs ==========
:logs
if "%2"=="" (
    echo 📋 显示所有后端服务日志 (Ctrl+C 退出)...
    %COMPOSE_CMD% -f %COMPOSE_FILE% logs -f
) else (
    echo 📋 显示 %2 日志 (Ctrl+C 退出)...
    %COMPOSE_CMD% -f %COMPOSE_FILE% logs -f %2
)
goto :end

:: ========== build ==========
:build
echo 🔨 重新构建后端镜像...
%COMPOSE_CMD% -f %COMPOSE_FILE% build --no-cache
echo ✅ 构建完成
goto :end

:: ========== frontend（单独启动前端）==========
:frontend
call :frontend_start
goto :end

:: ========== 内部子程序：启动前端 ==========
:frontend_start
echo 🌐 启动前端开发服务器...
if not exist "%FRONTEND_DIR%\node_modules" (
    echo   📦 首次运行，安装前端依赖（请稍候）...
    pushd %FRONTEND_DIR%
    call npm install
    call npm install -D sass-embedded
    popd
) else if not exist "%FRONTEND_DIR%\node_modules\sass-embedded" (
    echo   📦 安装 sass-embedded...
    pushd %FRONTEND_DIR%
    call npm install -D sass-embedded
    popd
)
start "AISchool Frontend" cmd /k "cd /d %~dp0%FRONTEND_DIR% && npm run dev"
echo   ✅ 前端已在新窗口启动 (http://localhost:3000)
exit /b 0

:: ========== 帮助 ==========
:usage
echo.
echo 🎓 %PROJECT_NAME% - 统一管理脚本
echo ============================================
echo 用法: manage.bat [命令] [选项]
echo.
echo 命令:
echo   start            启动所有服务（后端 Docker + 前端开发服务器）
echo   stop             停止所有服务
echo   restart          重启所有服务
echo   status           查看服务运行状态
echo   logs [service]   查看后端日志（可选：backend / db / redis）
echo   frontend         单独启动前端开发服务器
echo   build            重新构建后端镜像（不启动）
echo   help             显示此帮助信息
echo.
echo 示例:
echo   manage.bat start
echo   manage.bat logs backend
echo   manage.bat status
echo   manage.bat stop
echo.

:end
endlocal
