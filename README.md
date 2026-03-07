# AI School - 智能学习辅导系统 (Multi-Agent)

基于 CrewAI 的智能学习系统，具备多端适配、自定义 LLM 配置及自动化部署能力。

## 🎯 核心特性
- **多端适配**: 完美支持手机、平板、PC 访问。
- **自定义模型**: 界面化配置 OpenAI 兼容接口（如 DeepSeek, GPT-4）。
- **全栈 Docker 化**: 支持一键启动及单镜像极简部署。
- **自动化发布**: 集成 GitHub Actions 流水线。

---

## 🚀 部署指南

### 1. 克隆仓库
```bash
git clone https://github.com/MoCuishlei/AISchool.git
cd AISchool
```

### 2. 方式一：Docker Compose 全栈部署 (推荐)
适合开发和生产环境，包含数据库和 Redis 缓存。
```bash
# 1. 复制环境变量
cp .env.example .env

# 2. 一键启动 (包含前端、后端、DB、Redis)
docker-compose up -d --build
```
启动后访问：`http://localhost:3000`

### 3. 方式二：Standalone 一体化镜像部署
如果你希望“只拉取一个镜像就能运行”，直接使用我们预构建的镜像（无需 Nginx）：
```bash
# 从 GHCR 直接拉取 (需替换为你的镜像地址)
docker pull ghcr.io/mocuishlei/aischool-standalone:latest

# 运行 (自带 SQLite，零配置)
docker run -d -p 8000:8000 --name aischool-app ghcr.io/mocuishlei/aischool-standalone:latest
```
访问地址：`http://localhost:8000`

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