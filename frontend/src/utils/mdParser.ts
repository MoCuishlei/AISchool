/**
 * Markdown 块解析器
 * 将教案文本拆分为可识别的组件块，以便在 Vue 中使用专业组件渲染
 */

export interface ContentBlock {
    id: string;
    type: 'markdown' | 'code' | 'tree' | 'math';
    content: string;
    language?: string; // 针对 code 类型
    metadata?: any;    // 针对特殊标记如 # 危险代码
    treeNodes?: any;   // 针对树形结构
    treeConfig?: any;  // 针对树形结构
}

/**
 * 解析 Markdown 文本为块数组
 */
export function parseBlocks(text: string): ContentBlock[] {
    if (!text) return [];

    const blocks: ContentBlock[] = [];
    const lines = text.split('\n');
    let currentMarkdown = '';
    let i = 0;

    const flushMarkdown = () => {
        if (currentMarkdown.trim()) {
            blocks.push({
                id: Math.random().toString(36).substr(2, 9),
                type: 'markdown',
                content: currentMarkdown.trim()
            });
            currentMarkdown = '';
        }
    };

    while (i < lines.length) {
        const line = lines[i];

        // 1. 识别代码块 ```
        if (line.trim().startsWith('```')) {
            flushMarkdown();
            const lang = line.trim().slice(3).trim();
            let codeContent = '';
            let j = i + 1;
            while (j < lines.length && !lines[j].trim().startsWith('```')) {
                codeContent += lines[j] + '\n';
                j++;
            }

            // 提取代码中的特殊元数据 (如第一行是注释 # 危险代码)
            let metadata = null;
            if (codeContent.includes('# 危险代码') || codeContent.includes('// 危险代码')) {
                metadata = { warning: true, title: '危险代码' };
            } else if (codeContent.includes('# 安全代码') || codeContent.includes('// 安全代码')) {
                metadata = { success: true, title: '安全代码' };
            }

            blocks.push({
                id: Math.random().toString(36).substr(2, 9),
                type: 'code',
                content: codeContent.trim(),
                language: lang || 'text',
                metadata
            });
            i = j + 1;
            continue;
        }

        // 2. 识别块级数学公式 $$
        if (line.trim().startsWith('$$')) {
            flushMarkdown();
            let mathContent = '';
            let j = i + 1;
            // 如果是一行写完的 $$...$$
            if (line.trim().endsWith('$$') && line.trim().length > 2) {
                mathContent = line.trim().slice(2, -2);
                i = j;
            } else {
                while (j < lines.length && !lines[j].trim().startsWith('$$')) {
                    mathContent += lines[j] + '\n';
                    j++;
                }
                i = j + 1;
            }
            blocks.push({
                id: Math.random().toString(36).substr(2, 9),
                type: 'math',
                content: mathContent.trim()
            });
            continue;
        }

        // 3. 识别树形结构 ├── 或 └──
        if (line.includes('├──') || line.includes('└──')) {
            flushMarkdown();
            const treeLines = [];
            let j = i;

            while (j < lines.length && (lines[j].includes('├──') || lines[j].includes('└──') || lines[j].includes('│') || lines[j].trim() === '')) {
                if (lines[j].trim()) treeLines.push(lines[j]);
                j++;
            }

            // 将文本树转为 JSON 结构 (vue3-treeview 格式)
            const treeData = parseTextToTreeJson(treeLines);

            blocks.push({
                id: Math.random().toString(36).substr(2, 9),
                type: 'tree',
                content: JSON.stringify(treeData)
            });
            i = j;
            continue;
        }

        // 4. 普通 Markdown 行
        currentMarkdown += line + '\n';
        i++;
    }

    flushMarkdown();
    return blocks;
}

/**
 * 将 ├── 格式的文本解析为 vue3-treeview 需要的节点对象
 */
function parseTextToTreeJson(lines: string[]): any {
    const nodes: any = {};
    const rootId = 'root-0';
    nodes[rootId] = { id: rootId, text: '知识地图', children: [], state: { opened: true } };

    const stack: string[] = [rootId];

    lines.forEach((line, idx) => {
        // 计算深度：根据 │ 和 ├── 前面的空格或符号
        const depth = (line.match(/│/g) || []).length + 1;
        const text = line.replace(/[│├└]──/g, '').replace(/│/g, '').trim();
        const id = `node-${idx + 1}`;

        nodes[id] = { id, text, children: [], state: { opened: true } };

        // 维护层级堆栈
        while (stack.length > depth) {
            stack.pop();
        }

        const parentId = stack[stack.length - 1];
        if (nodes[parentId]) {
            nodes[parentId].children.push(id);
        }
        stack.push(id);
    });

    return {
        config: {
            roots: [rootId]
        },
        nodes: nodes
    };
}
