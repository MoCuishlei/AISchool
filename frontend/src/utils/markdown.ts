import MarkdownIt from 'markdown-it'
import mk from 'markdown-it-katex'
import hljs from 'highlight.js'

const md = new MarkdownIt({
    html: true,
    breaks: true,
    linkify: true,
    highlight: (code: string, lang: string) => {
        // 语法高亮：优先用指定语言，否则自动检测
        if (lang && hljs.getLanguage(lang)) {
            try {
                const highlighted = hljs.highlight(code, { language: lang, ignoreIllegals: true }).value
                return `<pre class="hljs-block"><code class="hljs language-${lang}">${highlighted}</code></pre>`
            } catch { }
        }
        // 自动检测语言
        try {
            const result = hljs.highlightAuto(code)
            return `<pre class="hljs-block"><code class="hljs">${result.value}</code></pre>`
        } catch { }
        // 降级纯文本
        return `<pre class="hljs-block"><code class="hljs">${md.utils.escapeHtml(code)}</code></pre>`
    }
})

md.use(mk)

/**
 * 将层级列表文本转换为 Mermaid 思维导图
 */
function convertHierarchyToMermaid(text: string): string {
    // 检查是否包含层级符号
    if (!text.includes('├──') && !text.includes('└──')) return text

    const lines = text.split('\n')
    let root = '板书总结'
    const nodes: string[] = []

    // 简单提取根节点
    const firstLine = lines.find(l => l.trim().length > 0 && !l.includes('├') && !l.includes('└'))
    if (firstLine) root = firstLine.replace(/[📝]/g, '').trim()

    nodes.push(`mindmap\n  root((${root}))`)

    lines.forEach(line => {
        if (line.includes('├──') || line.includes('└──')) {
            // 提取内容
            const content = line.replace(/[├└]──/g, '').trim()
            if (content) {
                // 根据缩进或符号简单处理层级
                const indentCount = (line.match(/│/g) || []).length + 1
                nodes.push(`${'  '.repeat(indentCount + 1)}${content}`)
            }
        }
    })

    if (nodes.length <= 1) return text // 转换失败回退

    return `\n\n\`\`\`mermaid\n${nodes.join('\n')}\n\`\`\`\n\n`
}

export function renderMd(text: string | null | undefined): string {
    if (!text) return ''

    try {
        let p = text

        // 0. 特殊处理：层级板书转图形 (Mermaid)
        // 匹配包含层级符号的段落
        const boardPattern = /(?:📝\s*)?板书总结[\s\S]*?(?:\n\n|\n$)/g
        p = p.replace(boardPattern, (match) => {
            return convertHierarchyToMermaid(match)
        })

        // 1. 处理 \[ ... \] 和 \begin{...} ... \end{...} 为块级公式 $$
        p = p.replace(/\\\[([\s\S]*?)\\\]/g, (_, p1) => `\n\n$$\n${p1.trim()}\n$$\n\n`)
            .replace(/\\begin\{([a-z*]+)\}([\s\S]*?)\\end\{\1\}/gi, (_, env, content) => {
                return `\n\n$$\n\\begin{${env}}${content}\\end{${env}}\n$$\n\n`
            })
            // 2. 将 \( ... \) 转换为行内公式 $
            .replace(/\\\(([\s\S]*?)\\\)/g, (_, p1) => `$${p1.trim()}$`)

        // 3. 增强对 $ ... $ 的识别
        p = p.replace(/(^|[^$])\$((?:\\\$|[^$]){1,500}?)\$([^$]|$)/g, (_, pre, content, post) => {
            return `${pre}$${content.trim()}$${post}`
        })

        return md.render(p)
    } catch (e) {
        console.error('Markdown Render Error:', e)
        return String(text)
    }
}
