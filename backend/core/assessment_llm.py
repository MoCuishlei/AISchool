"""
测评专用 LLM — 入学诊断测试
"""

import json, os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

from core.config_utils import get_openai_client

def _chat(system: str, user: str, temperature: float = 1.0) -> str:
    client, model = get_openai_client()
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system},
                  {"role": "user",   "content": user}],
        temperature=temperature, max_tokens=3000,
    )
    return r.choices[0].message.content or ""


def generate_assessment_questions(subject: str, count: int = 10) -> list:
    """生成入学诊断题，覆盖该主题的各子领域"""
    system = (
        "你是一位专业的中国高级教研员和测评专家。请严格返回 JSON 数组，不要有多余文字。\n"
        "【重要约束】严禁在题目中出现“如图所示”、“见图”、“下方图表”等对外部图片的引用，因为目前系统无法显示图片。请确保所有题目都是文字自洽的。"
    )
    user = f"""为「{subject}」生成 {count} 道【入学摸底诊断题】，覆盖该主题的多个核心考点与子领域。
要求：
- 题型混合（单选题、简答题/分析题）
- 难度梯度：2道基础送分题、5道中档拉分题、3道压轴选拔题
- 每道题精准标注所属“核心考点/模块”
- JSON 格式：
[
  {{
    "id": 1,
    "type": "choice",
    "domain": "核心考点/模块",
    "question": "题目内容",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "answer": "A",
    "difficulty": "easy"
  }},
  {{
    "id": 2,
    "type": "open",
    "domain": "核心考点/模块",
    "question": "题目内容",
    "answer": "参考答案",
    "difficulty": "medium"
  }}
]"""
    raw = _chat(system, user, temperature=1.0)
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
    system = (
        "你是一位专业的中国高级教研员和测评专家。请严格返回 JSON 数组，不要有多余文字。\n"
        "【重要约束】严禁在题目中出现“如图所示”、“见图”、“下方图表”等对外部图片的引用，因为目前系统无法显示图片。请确保所有题目都是文字自洽的。"
    )
    user = f"""为「{subject}」生成 {count} 道【入学摸底诊断题】，覆盖该主题的多个核心考点与子领域。
要求：
- 题型混合（单选题、简答题/分析题）
- 难度梯度：2道基础送分题、5道中档拉分题、3道压轴选拔题
- 每道题精准标注所属“核心考点/模块”
- JSON 格式：
[
  {{
    "id": 1,
    "type": "choice",
    "domain": "核心考点/模块",
    "question": "题目内容",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "answer": "A",
    "difficulty": "easy"
  }},
  {{
    "id": 2,
    "type": "open",
    "domain": "核心考点/模块",
    "question": "题目内容",
    "answer": "参考答案",
    "difficulty": "medium"
  }}
]"""
    try:
        client, model = get_openai_client()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system},
                      {"role": "user",   "content": user}],
            temperature=1.0, max_tokens=3000, stream=True
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


def evaluate_assessment(subject: str, questions: list, answers: list) -> tuple[dict, str, float]:
    """批改测评，返回 (熟练度字典, 分析报告文字, 总体评分)"""
    qa_text = ""
    for q, a in zip(questions, answers):
        qa_text += f"\n题{q['id']}（{q['domain']}）: {q['question']}\n学生答案: {a}\n参考答案: {q.get('answer','')}\n"

    system = "你是一位严谨的中国教育评估专家，请严格返回 JSON，不要有多余文字。"
    user = f"""根据以下测评答题情况，为这段【摸底诊断】生成一份专业评估报告，并为各个“考点/模块”进行熟练度评分（0-100）。
同时，请基于整体答题质量给出一个“总体评分”（0-100）。

{qa_text}

请返回格式：
{{
  "proficiency": {{
    "考点1": 75,
    "考点2": 40
  }},
  "overall_score": 65.0,
  "report": "学情诊断报告文字，包含学霸雷达图分析（指出各考点掌握率）和专属提分规划..."
}}"""
    raw = _chat(system, user, temperature=0.0)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
    if raw.endswith("```"):
        raw = "\n".join(raw.split("\n")[:-1])
    try:
        data = json.loads(raw.strip())
        return data.get("proficiency", {}), data.get("report", ""), float(data.get("overall_score", 0))
    except:
        return {}, "评估完成", 0.0
