# AI School - 智能学习辅导系统 (Multi-Agent)

基于 CrewAI 的智能学习系统，具备多端适配、自定义 LLM 配置及自动化部署能力。

## 🎯 核心特性
- **多端适配**: 完美支持手机、平板、PC 访问。
- **自定义模型**: 界面化配置 OpenAI 兼容接口（如 DeepSeek, GPT-4）。
- **全栈 Docker 化**: 支持双镜像分离部署，性能更优。
- **自动化发布**: 集成 GitHub Actions 流水线，自动推送至 GHCR。

---

## 🚀 快速开始 (Linux Docker)

仅需两步即可在 Linux 服务器上部署：

```bash
# 1. 下载部署配置文件
mkdir aischool && cd aischool
wget https://raw.githubusercontent.com/MoCuishlei/AISchool/main/docker-compose.yml
wget https://raw.githubusercontent.com/MoCuishlei/AISchool/main/.env.example -O .env

# 2. 启动服务
# 请先编辑 .env 文件配置您的 API Key
docker compose up -d
```
访问地址：`http://服务器IP` (默认 80 端口)。

### 1. 极简部署 (Standalone - 仅需一个镜像)
如果您希望“秒级”启动，无需配置 Nginx 和多个容器，可以使用我们的一体化镜像：
```bash
docker run -d -p 8000:8000 \
  -e LLM_API_KEY=您的密钥 \
  --name aischool-app \
  ghcr.io/mocuishlei/aischool-standalone:latest
```
访问地址：`http://服务器IP:8000`

---

## 🏗️ 详细部署 (生产推荐)
如果您想修改代码或在本地运行：
```bash
git clone https://github.com/MoCuishlei/AISchool.git
cd AISchool
docker compose up -d --build
```

### 2. 镜像说明
我们现在采用 **双镜像分离架构** 以获得更好的生产性能：
- **前端镜像**: `ghcr.io/mocuishlei/aischool-frontend:latest` (Nginx)
- **后端镜像**: `ghcr.io/mocuishlei/aischool-backend:latest` (API)
- **一体化镜像**: `ghcr.io/mocuishlei/aischool-standalone:latest` (全功能内置)

---

## ⚙️ 模型配置
部署成功后，进入界面右侧菜单 **“模型配置”**：
- 设置 **Base URL** (例如 `https://api.deepseek.com/v1`)
- 设置 **API Key**
- 点击 **“测试连接”** 验证模型是否响应。

---

## 📄 开发者说明
如果你想基于后端二次开发（如开发小程序）：
- 请查阅界面中的 **“API 文档”**。
- 后端 API 默认运行在 `8000` 端口。

## 🔧 开发调试 (本地运行)
```bash
# 后端
pip install -r requirements.txt
python -m uvicorn api.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```