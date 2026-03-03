# AI School Frontend

基于Vue 3 + TypeScript + Vite的现代化学习平台前端。

## 🚀 功能特性

### 学生功能
- 📊 学习仪表盘
- 📚 交互式学习
- 📝 在线练习
- 📈 进度追踪
- 🏆 成就系统

### 教师功能
- 👨‍🏫 班级管理
- 📋 题目管理
- 📊 学情分析
- 📝 作业布置
- 💬 在线答疑

### 管理功能
- 👥 用户管理
- 📚 课程管理
- 🔧 系统设置
- 📊 数据统计

## 🛠️ 技术栈

### 核心框架
- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全的JavaScript
- **Vite** - 下一代前端构建工具

### UI组件库
- **Element Plus** - Vue 3组件库
- **Tailwind CSS** - 实用优先的CSS框架

### 状态管理
- **Pinia** - Vue状态管理
- **Vue Router** - 路由管理

### 数据可视化
- **ECharts** - 图表库
- **Vue-ECharts** - ECharts Vue组件

### 开发工具
- **ESLint** - 代码检查
- **Prettier** - 代码格式化
- **Husky** - Git钩子

## 📁 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── assets/            # 图片、字体等资源
│   ├── components/        # 公共组件
│   ├── composables/       # 组合式函数
│   ├── layouts/           # 布局组件
│   ├── router/            # 路由配置
│   ├── stores/            # 状态管理
│   ├── styles/            # 样式文件
│   ├── types/             # TypeScript类型定义
│   ├── utils/             # 工具函数
│   ├── views/             # 页面组件
│   ├── App.vue            # 根组件
│   └── main.ts            # 入口文件
├── index.html             # HTML模板
├── package.json           # 依赖配置
├── tsconfig.json          # TypeScript配置
├── vite.config.ts         # Vite配置
└── README.md              # 项目说明
```

## 🚦 快速开始

### 环境要求
- Node.js 18+ 
- npm 9+ 或 yarn 1.22+

### 安装依赖
```bash
npm install
# 或
yarn install
```

### 开发模式
```bash
npm run dev
# 或
yarn dev
```

### 构建生产版本
```bash
npm run build
# 或
yarn build
```

### 代码检查
```bash
npm run lint
# 或
yarn lint
```

## 🔧 配置说明

### 环境变量
创建 `.env` 文件：
```env
# API基础URL
VITE_API_BASE_URL=http://localhost:8000

# 应用配置
VITE_APP_TITLE=AI School
VITE_APP_DESCRIPTION=智能学习辅导平台

# 功能开关
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_WEBSOCKET=true
```

### 代理配置
在 `vite.config.ts` 中配置API代理：
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

## 📱 响应式设计

### 断点配置
```css
/* Tailwind默认断点 */
sm: 640px    /* 手机 */
md: 768px    /* 平板 */
lg: 1024px   /* 笔记本 */
xl: 1280px   /* 桌面 */
2xl: 1536px  /* 大屏 */
```

### 移动端优化
- 触摸友好的交互
- 离线支持
- 推送通知
- 添加到主屏幕

## 🔌 API集成

### 接口规范
```typescript
// 统一响应格式
interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
  timestamp: number;
}

// 错误处理
interface ApiError {
  code: number;
  message: string;
  details?: any;
}
```

### 请求封装
使用axios进行HTTP请求封装，包含：
- 请求拦截器（添加token）
- 响应拦截器（统一错误处理）
- 请求取消
- 请求重试

## 🎨 主题系统

### 主题配置
支持亮色/暗色主题切换：
```typescript
const themes = {
  light: {
    primary: '#409EFF',
    success: '#67C23A',
    warning: '#E6A23C',
    danger: '#F56C6C',
    info: '#909399'
  },
  dark: {
    primary: '#409EFF',
    success: '#67C23A',
    warning: '#E6A23C',
    danger: '#F56C6C',
    info: '#909399'
  }
}
```

### 自定义主题
用户可自定义：
- 主色调
- 字体大小
- 布局密度
- 动画速度

## 📊 性能优化

### 代码分割
- 路由懒加载
- 组件异步加载
- 第三方库CDN

### 缓存策略
- 本地存储缓存
- 内存缓存
- HTTP缓存

### 图片优化
- WebP格式
- 懒加载
- 响应式图片

## 🔒 安全考虑

### 前端安全
- XSS防护
- CSRF防护
- 内容安全策略
- 点击劫持防护

### 数据保护
- 敏感信息加密
- 本地存储安全
- 传输加密

## 📈 监控分析

### 性能监控
- 页面加载时间
- 首屏渲染时间
- 用户交互延迟

### 用户行为分析
- 页面访问统计
- 功能使用情况
- 错误追踪

## 🚀 部署

### 静态部署
```bash
# 构建
npm run build

# 部署到Nginx
cp -r dist/* /usr/share/nginx/html/
```

### Docker部署
```dockerfile
FROM nginx:alpine
COPY dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

### CI/CD
支持GitHub Actions、GitLab CI等持续集成部署。

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📞 支持

- 文档：查看本README和代码注释
- 问题：提交GitHub Issue
- 讨论：加入社区讨论

---

**🎉 开始你的AI School前端开发之旅吧！**