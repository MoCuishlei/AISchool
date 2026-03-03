# AI School - 多Agent学习辅导系统

基于CrewAI的多Agent学习辅导系统，支持多种LLM模型（DeepSeek、OpenAI、本地模型）。

## 🎯 核心Agent
1. **总控Agent** - 协调学习流程
2. **教学Agent** - 知识点讲解  
3. **出题Agent** - 生成练习题
4. **测验Agent** - 评估学习效果
5. **记忆Agent** - 管理学习历史

## 🚀 快速开始

### 方法1：使用OpenClaw配置（推荐）
```bash
# 自动使用当前OpenClaw会话的模型和API配置
python run_with_openclaw.py
```

### 方法2：标准运行
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置环境变量
cp .env.example .env
# 编辑.env文件，设置API密钥

# 3. 运行系统
python main.py
```

### 方法3：交互式启动
```bash
# 提供图形化菜单和配置检查
python start_project.py
```

### 方法4：Docker运行
```bash
# 构建镜像
docker build -t aischool .

# 运行容器
docker run -p 8000:8000 --env-file .env aischool
```

## 🔧 模型支持

### 默认配置（DeepSeek）
- 模型：`deepseek-chat`
- API：`https://api.deepseek.com/v1`
- 自动使用OpenClaw的API密钥

### 支持的其他模型
- **OpenAI**: GPT-4, GPT-3.5
- **本地模型**: Llama, Qwen (通过Ollama)
- **Anthropic**: Claude

### 配置切换
编辑 `.env` 文件：
```env
LLM_PROVIDER=deepseek  # deepseek, openai, local
DEEPSEEK_API_KEY=your_key
OPENAI_API_KEY=your_key
```

## 功能特性
- 🎯 个性化学习路径规划
- 📚 多学科支持（数学、编程、语言等）
- 🔄 自适应难度调整
- 💾 学习进度持久化存储
- 📊 学习效果可视化分析