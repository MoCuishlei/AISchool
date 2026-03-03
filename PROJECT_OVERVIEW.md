# AI School - 项目概览

## 📁 项目结构
```
AISchool/
├── README.md                    # 项目说明
├── requirements.txt             # Python依赖
├── .env.example                 # 环境变量模板
├── Dockerfile                   # Docker构建文件
├── docker-compose.yml           # Docker Compose配置
├── DEPLOYMENT.md               # 部署指南
├── PROJECT_OVERVIEW.md         # 本项目文件
│
├── config/                     # 配置目录
│   ├── agents.py              # Agent定义
│   └── tasks.py               # 任务定义
│
├── core/                       # 核心逻辑
│   └── learning_crew.py       # 多Agent协作系统
│
├── api/                        # Web API
│   └── main.py                # FastAPI应用
│
├── tests/                      # 测试目录
│   └── test_agents.py         # Agent测试
│
└── scripts/                    # 脚本目录
    ├── run_demo.sh            # Linux/Mac启动脚本
    └── run_demo.bat           # Windows启动脚本
```

## 🎯 核心功能

### 1. 多Agent架构
- **总控Agent** - 学习流程协调
- **教学Agent** - 知识点讲解
- **出题Agent** - 练习题生成
- **测验Agent** - 学习评估
- **记忆Agent** - 进度管理

### 2. 学习流程
```
学生评估 → 教学讲解 → 练习生成 → 学习评估 → 进度记录
```

### 3. 支持模式
- **完整学习会话** - 完整的5步学习流程
- **快速教学** - 只进行知识点讲解
- **练习生成** - 只生成练习题
- **Web API** - RESTful API接口

## 🚀 快速开始

### 方法1：演示模式（立即体验）
```bash
cd AISchool
python run_local.py
```

### 方法2：完整运行（需要API密钥）
1. 复制环境变量模板：
   ```bash
   cp .env.example .env
   ```

2. 编辑`.env`文件，设置你的OpenAI API密钥

3. 运行系统：
   ```bash
   python main.py
   ```

### 方法3：Docker运行
```bash
# 使用Docker Compose（包含数据库）
docker-compose up -d

# 或单容器运行
docker build -t aischool .
docker run -p 8000:8000 --env-file .env aischool
```

## 🔧 自定义配置

### 1. 修改Agent行为
编辑 `config/agents.py`：
- 调整Agent的role、goal、backstory
- 添加或修改工具函数
- 调整verbose级别

### 2. 修改学习流程
编辑 `config/tasks.py`：
- 调整任务描述和期望输出
- 修改任务顺序和依赖关系

### 3. 集成外部服务
- **向量数据库**：修改`search_knowledge_base`工具
- **数据库**：修改`save_learning_progress`工具
- **其他API**：在tools中添加新的工具函数

## 📊 扩展方向

### 短期扩展
1. **学科扩展**：添加数学、英语、编程等特定学科Agent
2. **难度分级**：实现自适应难度调整算法
3. **多媒体支持**：集成图片、音频、视频教学内容

### 中期扩展
1. **学生画像**：基于学习数据构建学生能力模型
2. **个性化推荐**：根据学习历史推荐学习内容
3. **协作学习**：支持多学生同时学习，互相讨论

### 长期扩展
1. **情感识别**：通过文本分析学生情绪状态
2. **游戏化学习**：添加积分、徽章、排行榜等元素
3. **家长报告**：自动生成学习进度报告给家长

## 🐛 调试与测试

### 测试Agent创建
```bash
python test_agents.py
```

### 测试API
```bash
# 启动API
python -m uvicorn api.main:app --reload

# 测试端点
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

### 查看日志
```bash
# Docker Compose
docker-compose logs -f

# 单个容器
docker logs -f <container_id>
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支：`git checkout -b feature/新功能`
3. 提交更改：`git commit -am '添加新功能'`
4. 推送到分支：`git push origin feature/新功能`
5. 创建Pull Request

## 📞 支持与反馈

遇到问题？
1. 查看 `DEPLOYMENT.md` 中的故障排除部分
2. 检查日志文件
3. 提交Issue到项目仓库

## 📚 学习资源

- [CrewAI官方文档](https://docs.crewai.com/)
- [LangChain文档](https://python.langchain.com/)
- [OpenAI API文档](https://platform.openai.com/docs/)
- [FastAPI文档](https://fastapi.tiangolo.com/)

---

**🎉 现在就开始你的多Agent学习辅导系统开发吧！**