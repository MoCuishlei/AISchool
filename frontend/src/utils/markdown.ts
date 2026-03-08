import MarkdownIt from 'markdown-it'
import mk from 'markdown-it-katex'
import hljs from 'highlight.js'

const md = new MarkdownIt({
    html: true,
    breaks: true,
    linkify: true,
    highlight: (code: string, lang: string) => {
        const h = lang && hljs.getLanguage(lang)
            ? hljs.highlight(code, { language: lang, ignoreIllegals: true }).value
            : hljs.highlightAuto(code).value;

        return `<div class="premium-code-block">
            <div class="code-header">
                <div class="controls"><span class="close"></span><span class="minimize"></span><span class="maximize"></span></div>
                <div class="lang-badge">${lang || 'code'}</div>
            </div>
            <pre class="hljs-block"><code class="hljs ${lang ? 'language-' + lang : ''}">${h}</code></pre>
        </div>`
    }
})

md.use(mk)

/**
 * 将层级列表文本转换为 Premium UI 树形组件
 */
function convertHierarchyToPremiumTree(text: string): string {
    const lines = text.split('\n').filter(l => l.trim())
    if (!lines.some(l => l.includes('├──') || l.includes('└──'))) return text

    let html = '<div class="tree-container">'

    // 识别标题/根节点
    const rootLine = lines[0]
    if (!rootLine.includes('├') && !rootLine.includes('└')) {
        html += `<div class="tree-root"><span class="node-icon">🎯</span>${rootLine.trim()}</div>`
        lines.shift()
    }

    html += '<div class="tree-content">'
    lines.forEach(line => {
        const depth = (line.match(/│/g) || []).length + (line.includes('├──') || line.includes('└──') ? 1 : 0)
        const content = line.replace(/[│├└]──/g, '').replace(/│/g, '').trim()
        if (content) {
            html += `
                <div class="tree-node" style="margin-left: ${(depth - 1) * 20}px">
                    <div class="node-content">
                        <span class="node-icon">${content.includes('环境') || content.includes('系统') ? '💻' : '🔗'}</span>
                        ${content}
                    </div>
                </div>`
        }
    })

    html += '</div></div>'
    return html
}

export function renderMd(text: string | null | undefined): string {
    if (!text) return ''

    try {
        let p = text

        // 0. 特殊处理：层级板书转 Premium Tree
        // 匹配包含层级符号的段落
        const treePattern = /((?:^|\n).*[Python|语法|变量|运算|模块].*(?:\n(?:[│├└]──|│).*)+)/g
        p = p.replace(treePattern, (match) => {
            return convertHierarchyToPremiumTree(match)
        })

        // 1. 处理 \[ ... \] 和 \begin{...} ... \end{...} 为块级公式 $$ 并包裹在 Spotlight 容器中
        p = p.replace(/\\\[([\s\S]*?)\\\]/g, (_, p1) => `\n\n<div class="formula-spotlight">\n\n$$\n${p1.trim()}\n$$\n\n</div>\n\n`)
            .replace(/\\begin\{([a-z*]+)\}([\s\S]*?)\\end\{\1\}/gi, (_, env, content) => {
                return `\n\n<div class="formula-spotlight">\n\n$$\n\\begin{${env}}${content}\\end{${env}}\n$$\n\n</div>\n\n`
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
