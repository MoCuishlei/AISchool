<template>
  <div class="api-docs">
    <div class="header">
      <h1>AI School 开发者 API 文档</h1>
      <p>本套 API 旨在帮助开发者快速将 AI School 的核心能力对接到小程序、移动端或其他第三方应用。</p>
    </div>

    <div class="api-section">
      <h3>1. 核心教学接口 (Core Learning)</h3>
      <div class="endpoint">
        <div class="ep-header">
          <el-tag type="success" effect="dark">POST</el-tag>
          <span class="url">/learning/syllabus</span>
        </div>
        <p class="desc">功能：根据输入的主题生成结构化的教学大纲 (JSON)。</p>
        <pre class="payload">
// 请求示例
{
  "topic": "操作系统"
}

// 返回示例
{
  "topic": "操作系统",
  "sections": [
    { "id": "1", "title": "进程管理", "items": [...] }
  ]
}
        </pre>
      </div>

      <div class="endpoint">
        <div class="ep-header">
          <el-tag type="success" effect="dark">POST</el-tag>
          <span class="url">/learning/quick-teach</span>
        </div>
        <p class="desc">功能：针对特定知识点生成详细的 Markdown 教学讲义。</p>
      </div>
    </div>

    <div class="api-section">
      <h3>2. 学情分析接口 (Analytics)</h3>
      <div class="endpoint">
        <div class="ep-header">
          <el-tag type="warning" effect="dark">GET</el-tag>
          <span class="url">/analytics/dashboard/{session_id}</span>
        </div>
        <p class="desc">功能：获取指定学习会话的图表分析数据、掌握度分布和考分预测。</p>
      </div>
    </div>

    <el-alert 
      title="对接提示" 
      type="info" 
      :closable="false" 
      show-icon
      style="margin-top: 40px;"
    >
      <p>小程序对接时，请在小程序后台配置域名白名单。模型 Key 等敏感信息请务必在“系统模型配置”页面完成设置，不要硬编码在代码中。</p>
    </el-alert>
  </div>
</template>

<style scoped lang="scss">
.api-docs {
  max-width: 900px;
  margin: 0 auto;
  padding-bottom: 60px;
}

.header {
  margin-bottom: 40px;
  h1 { font-size: 32px; font-weight: 800; color: #1e293b; margin-bottom: 12px; }
  p { color: #64748b; font-size: 16px; line-height: 1.6; }
}

.api-section {
  margin-bottom: 48px;
  h3 { font-size: 18px; font-weight: 700; color: #334155; margin-bottom: 24px; border-left: 4px solid #6366f1; padding-left: 12px; }
}

.endpoint {
  background: white;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  margin-bottom: 24px;
  
  .ep-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
    .url { font-family: 'Fira Code', monospace; font-weight: 700; color: #1e293b; }
  }
  
  .desc { font-size: 14px; color: #64748b; margin-bottom: 16px; }
  
  .payload {
    background: #0f172a;
    color: #cbd5e1;
    padding: 16px;
    border-radius: 8px;
    font-size: 13px;
    overflow-x: auto;
  }
}
</style>
