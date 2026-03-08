<template>
  <div class="premium-content-renderer">
    <div v-for="block in processedBlocks" :key="block.id" class="content-block">
      <!-- 1. 普通 Markdown 文本 -->
      <div v-if="block.type === 'markdown'" class="markdown-body" v-html="renderMd(block.content)" />
      
      <!-- 2. 专业代码块 -->
      <div v-else-if="block.type === 'code'" class="block-wrapper code-wrapper">
        <el-alert
          v-if="block.metadata?.warning || block.metadata?.success"
          :title="block.metadata.title"
          :type="block.metadata.warning ? 'error' : 'success'"
          :closable="false"
          show-icon
          class="code-alert"
        />
        <v-code-block
          :code="block.content"
          :lang="block.language"
          theme="neon-bunny"
          :highlightjs="true"
          :copy-button="true"
          label="代码示例"
          browser-window
        />
      </div>

      <!-- 3. 图形化树形结构 -->
      <div v-else-if="block.type === 'tree'" class="block-wrapper tree-wrapper">
        <div class="tree-header">🌿 知识地图</div>
        <tree-view :nodes="block.treeNodes" :config="block.treeConfig" />
      </div>

      <!-- 4. 数学公式 Spotlight -->
      <div v-else-if="block.type === 'math'" class="block-wrapper math-wrapper">
        <el-card shadow="hover" class="math-card" v-katex="block.content" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { renderMd } from '@/utils/markdown'
import { parseBlocks } from '@/utils/mdParser'
import { VCodeBlock } from '@wdns/vue-code-block'
import TreeView from 'vue3-treeview'
import 'vue3-treeview/dist/style.css'

const props = defineProps<{
  content: string
}>()

const processedBlocks = computed(() => {
  const rawBlocks = parseBlocks(props.content);
  return rawBlocks.map(b => {
    if (b.type === 'tree') {
      try {
        const data = JSON.parse(b.content);
        return { ...b, treeNodes: data.nodes, treeConfig: data.config };
      } catch (e) {
        console.error('Tree Parse Error:', e);
        return { ...b, type: 'markdown' as const };
      }
    }
    return b;
  });
});
</script>

<style scoped lang="scss">
.content-block {
  margin-bottom: 24px;
  &:last-child { margin-bottom: 0; }
}

.block-wrapper {
  margin: 20px 0;
  border-radius: 12px;
  overflow: hidden;
}

.code-wrapper {
  .code-alert {
    margin-bottom: 8px;
    border-radius: 8px;
  }
}

.tree-wrapper {
  background: white;
  border: 1px solid #e2e8f0;
  padding: 16px;
  .tree-header { 
    font-size: 14px; font-weight: 700; color: #64748b; 
    margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f1f5f9;
  }
}

.math-wrapper {
  .math-card {
    border-radius: 16px;
    :deep(.el-card__body) {
      display: flex; justify-content: center; padding: 32px;
      background: linear-gradient(to bottom, #ffffff, #f8fafc);
    }
    :deep(.katex-display) { margin: 0; }
  }
}

.markdown-body {
  line-height: 1.8;
  word-break: break-word;
}
</style>
