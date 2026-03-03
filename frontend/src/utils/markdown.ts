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

export function renderMd(text: string | null | undefined): string {
    if (!text) return ''

    try {
        // 1. 将 \[ ... \] 转换为块级公式 $$
        let p = text
            .replace(/\\\[([\s\S]*?)\\\]/g, (_, p1) => `\n\n$$\n${p1.trim()}\n$$\n\n`)
            // 2. 将 \( ... \) 转换为行内公式 $
            .replace(/\\\(([\s\S]*?)\\\)/g, (_, p1) => `$${p1.trim()}$`)

        // 3. 修剪现有 $ ... $ 内部首尾空格
        p = p.replace(/(^|[^$])\$([^$\n]{1,200}?)\$([^$]|$)/g, (_, pre, content, post) => {
            return `${pre}$${content.trim()}$${post}`
        })

        return md.render(p)
    } catch (e) {
        console.error('Markdown Render Error:', e)
        return String(text)
    }
}
