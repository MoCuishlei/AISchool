"""
直连 LLM 工具 - 绕过 crewAI 框架直接调用 DeepSeek API
用于需要快速响应的接口（quick-teach、practice、syllabus）
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def _get_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
    )

def _chat(system: str, user: str, temperature: float = 0.7, max_tokens: int = 3000) -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""


def direct_teach(topic: str, question: str | None = None) -> str:
    """直连 LLM 进行知识点讲解"""
    system = (
        "你是一位经验丰富的学科教师，擅长用清晰易懂的语言讲解知识点。"
        "请给出结构化的讲解，包含：概念定义、核心要点、具体示例、常见误区。"
        "使用 Markdown 格式，让内容层次分明。"
    )
    if question:
        user = f"请讲解「{topic}」，并特别解答这个问题：{question}"
    else:
        user = f"请详细讲解「{topic}」，让初学者能够快速理解和掌握。"
    return _chat(system, user)


def direct_practice(topic: str, difficulty: str = "medium", count: int = 5) -> str:
    """直连 LLM 生成练习题"""
    diff_map = {"easy": "简单", "medium": "中等", "hard": "困难"}
    diff_cn = diff_map.get(difficulty, "中等")
    system = (
        "你是一位专业的题目设计师，能设计高质量的练习题。"
        "每道题包含：题目、选项（如适合）、参考答案、简要解析。"
        "使用 Markdown 格式，标注题号。"
    )
    user = f"请为「{topic}」生成 {count} 道{diff_cn}难度的练习题，覆盖核心知识点。"
    return _chat(system, user)


def generate_syllabus(topic: str) -> dict:
    """直连 LLM 生成结构化学习大纲（返回 JSON）"""
    system = (
        "你是一位课程设计专家，能为任意学习主题生成系统化的学习大纲。"
        "请严格返回 JSON 格式，不要有多余文字。"
    )
    user = f"""请为「{topic}」生成一个系统化的学习大纲。
要求：
- 分为 4-6 个主要章节
- 每个章节有 3-5 个子知识点
- JSON 格式如下：
{{
  "topic": "{topic}",
  "description": "简短描述这个主题",
  "sections": [
    {{
      "id": "1",
      "title": "章节名称",
      "description": "章节简述",
      "items": [
        {{"id": "1.1", "title": "知识点名称", "description": "简短说明"}},
        {{"id": "1.2", "title": "知识点名称", "description": "简短说明"}}
      ]
    }}
  ]
}}"""
    raw = _chat(system, user, temperature=0.3)
    # 提取 JSON
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        # fallback：返回基础结构
        return {
            "topic": topic,
            "description": f"{topic} 学习大纲",
            "sections": [
                {
                    "id": "1",
                    "title": "基础入门",
                    "description": "掌握基本概念",
                    "items": [
                        {"id": "1.1", "title": f"{topic} 基础概念", "description": "了解核心定义"},
                        {"id": "1.2", "title": "环境搭建", "description": "配置学习环境"},
                    ]
                }
            ]
        }
