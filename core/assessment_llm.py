"""
测评专用 LLM — 入学诊断测试
"""

import json, os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def _client():
    return OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
    )

def _chat(system: str, user: str, temperature: float = 0.5) -> str:
    r = _client().chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        messages=[{"role": "system", "content": system},
                  {"role": "user",   "content": user}],
        temperature=temperature, max_tokens=3000,
    )
    return r.choices[0].message.content or ""


def generate_assessment_questions(subject: str, count: int = 10) -> list:
    """生成入学诊断题，覆盖该主题的各子领域"""
    system = (
        "你是一位专业的教育测评专家。请严格返回 JSON 数组，不要有多余文字。"
    )
    user = f"""为「{subject}」生成 {count} 道诊断题，覆盖该主题的多个子领域。
要求：
- 题型混合（选择题、简答题）
- 难度梯度：2道简单、5道中等、3道困难
- 每道题标注所属子领域
- JSON 格式：
[
  {{
    "id": 1,
    "type": "choice",
    "domain": "子领域名称",
    "question": "题目内容",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "answer": "A",
    "difficulty": "easy"
  }},
  {{
    "id": 2,
    "type": "open",
    "domain": "子领域名称",
    "question": "题目内容",
    "answer": "参考答案",
    "difficulty": "medium"
  }}
]"""
    raw = _chat(system, user)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
    if raw.endswith("```"):
        raw = "\n".join(raw.split("\n")[:-1])
    try:
        return json.loads(raw.strip())
    except:
        return []

def generate_assessment_questions_stream(subject: str, count: int = 10):
    """流式生成入学诊断题，实时 yield 状态和数据"""
    system = "你是一位专业的教育测评专家。请严格返回 JSON 数组，不要有多余文字。"
    user = f"""为「{subject}」生成 {count} 道诊断题，覆盖该主题的多个子领域。
要求：
- 题型混合（选择题、简答题）
- 难度梯度：2道简单、5道中等、3道困难
- 每道题标注所属子领域
- JSON 格式：
[
  {{
    "id": 1,
    "type": "choice",
    "domain": "子领域名称",
    "question": "题目内容",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "answer": "A",
    "difficulty": "easy"
  }},
  {{
    "id": 2,
    "type": "open",
    "domain": "子领域名称",
    "question": "题目内容",
    "answer": "参考答案",
    "difficulty": "medium"
  }}
]"""
    try:
        response = _client().chat.completions.create(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            messages=[{"role": "system", "content": system},
                      {"role": "user",   "content": user}],
            temperature=0.5, max_tokens=3000, stream=True
        )
        buffer = ""
        for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                buffer += delta
                yield {"status": "streaming", "chunk": delta}
                
        raw = buffer.strip()
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:])
        if raw.endswith("```"):
            raw = "\n".join(raw.split("\n")[:-1])
        questions = json.loads(raw.strip())
        yield {"status": "done", "questions": questions}
    except Exception as e:
        yield {"status": "error", "message": str(e)}


def evaluate_assessment(subject: str, questions: list, answers: list) -> tuple[dict, str]:
    """批改测评，返回 (熟练度字典, 分析报告文字)"""
    qa_text = ""
    for q, a in zip(questions, answers):
        qa_text += f"\n题{q['id']}（{q['domain']}）: {q['question']}\n学生答案: {a}\n参考答案: {q.get('answer','')}\n"

    system = "你是一位严谨的教育评估专家，请严格返回 JSON，不要有多余文字。"
    user = f"""根据以下测评答题情况，为「{subject}」的各子领域进行熟练度评分（0-100）。

{qa_text}

请返回格式：
{{
  "proficiency": {{
    "子领域1": 75,
    "子领域2": 40
  }},
  "report": "整体分析文字，指出强项和薄弱点，建议学习重点..."
}}"""
    raw = _chat(system, user, temperature=0.3)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
    if raw.endswith("```"):
        raw = "\n".join(raw.split("\n")[:-1])
    try:
        data = json.loads(raw.strip())
        return data.get("proficiency", {}), data.get("report", "")
    except:
        return {}, "评估完成"
