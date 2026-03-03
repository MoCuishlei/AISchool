# 部署指南

## 本地开发环境

### 1. 环境准备
```bash
# 克隆项目（如果适用）
git clone <repository-url>
cd AISchool

# 创建虚拟环境（推荐）
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，设置你的API密钥
# 需要设置 OPENAI_API_KEY
```

### 3. 运行系统

#### 方式一：命令行交互
```bash
python main.py
```

#### 方式二：Web API
```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
访问：http://localhost:8000/docs

#### 方式三：演示模式（无需API密钥）
```bash
python run_local.py
```

#### 方式四：使用脚本
```bash
# Linux/Mac
./run_demo.sh

# Windows
run_demo.bat
```

## Docker部署

### 1. 单容器部署
```bash
# 构建镜像
docker build -t aischool .

# 运行容器（需要提前设置.env文件）
docker run -p 8000:8000 --env-file .env aischool
```

### 2. 使用Docker Compose（推荐）
```bash
# 启动所有服务（数据库、Redis、应用）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 生产环境配置
创建 `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db/${DB_NAME}
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEBUG=False
    volumes:
      - ./chroma_db:/app/chroma_db
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: always

volumes:
  postgres_data:
  redis_data:
```

创建 `.env.prod` 文件：
```env
# 数据库配置
DB_NAME=aischool_prod
DB_USER=admin
DB_PASSWORD=secure_password_here

# OpenAI配置
OPENAI_API_KEY=your_production_api_key

# 应用配置
DEBUG=False
```

启动生产环境：
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 云平台部署

### Vercel / Railway (Python应用)
1. 连接Git仓库
2. 设置环境变量
3. 部署

### AWS / GCP / Azure
1. 使用ECS/EKS (AWS) 或 GKE (GCP) 或 AKS (Azure)
2. 配置数据库服务（RDS, Cloud SQL等）
3. 配置Redis服务
4. 部署应用容器

## 监控和维护

### 日志查看
```bash
# Docker Compose
docker-compose logs -f app

# 单个容器
docker logs -f aischool_app
```

### 数据库备份
```bash
# PostgreSQL备份
docker exec aischool_db pg_dump -U postgres aischool > backup_$(date +%Y%m%d).sql

# Redis备份
docker exec aischool_redis redis-cli save
```

### 性能监控
建议集成：
- **Prometheus + Grafana** - 系统监控
- **Sentry** - 错误追踪
- **LangSmith** - Agent调用追踪

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   Error: Invalid API key
   ```
   解决方案：检查.env文件中的OPENAI_API_KEY

2. **数据库连接失败**
   ```
   Connection refused to database
   ```
   解决方案：确保数据库服务正在运行，检查连接字符串

3. **内存不足**
   ```
   Out of memory error
   ```
   解决方案：增加Docker内存限制或优化Agent配置

4. **Agent响应慢**
   解决方案：
   - 使用更快的模型（如gpt-3.5-turbo）
   - 减少Agent数量
   - 启用缓存

### 获取帮助
- 查看日志：`docker-compose logs`
- 测试连接：`curl http://localhost:8000/health`
- 检查依赖：`pip list | grep crewai`