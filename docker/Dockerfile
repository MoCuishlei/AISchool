FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY backend/requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 仅复制后端代码
COPY backend/ ./backend/

# 创建数据目录
RUN mkdir -p chroma_db

# 设置 PYTHONPATH 确保导入正常
ENV PYTHONPATH=/app/backend:/app

# 暴露端口
EXPOSE 8000

# 运行应用 (注意模块路径)
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]