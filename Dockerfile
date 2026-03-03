FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（gcc 用于编译 Python 扩展，curl 用于健康检查）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p chroma_db

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]