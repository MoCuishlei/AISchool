"""
考试专用 LLM — 期中/期末考试出题和批改
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


def generate_exam(subject: str, covered_items: list, exam_type: str) -> list:
    """生成期中/期末试卷"""
    count = 15 if exam_type == "midterm" else 20
    scope = "已学习的章节" if exam_type == "midterm" else "全部章节"
    items_text = "、".join(covered_items[:20])

    system = "你是一位资深命题教师，请严格返回 JSON 数组，不要有多余文字。"
    user = f"""为「{subject}」出一份{"期中" if exam_type == "midterm" else "期末"}考试试卷。
考察范围：{scope}，具体知识点：{items_text}

要求：
- 共 {count} 道题
- 题型：选择题{count//2}道 + 简答题{count//4}道 + 综合应用{count//4}道
- 难度分布：30%简单、50%中等、20%困难
- 题目新颖，考察理解和应用，不要死记硬背能答出的题
- 综合题要求综合运用多个知识点
- JSON 格式与小测验相同，增加 "score_weight": 分值

[
  {{
    "id": 1,
    "type": "choice",
    "domain": "知识点",
    "question": "...",
    "options": ["A...", "B...", "C...", "D..."],
    "answer": "B",
    "explanation": "...",
    "score_weight": 3,
    "difficulty": "easy"
  }}
]"""

    try:
        r = _client().chat.completions.create(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            messages=[{"role": "system", "content": system},
                      {"role": "user",   "content": user}],
            temperature=0.7, max_tokens=4000,
        )
        raw = r.choices[0].message.content or ""
        raw = raw.strip()
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:])
        if raw.endswith("```"):
            raw = "\n".join(raw.split("\n")[:-1])
        return json.loads(raw)
    except:
        return []

def generate_exam_stream(subject: str, covered_items: list, exam_type: str):
    """流式生成期中/期末试卷，实时 yield 状态和数据"""
    count = 15 if exam_type == "midterm" else 20
    scope = "已学习的章节" if exam_type == "midterm" else "全部章节"
    items_text = "、".join(covered_items[:20])

    system = "你是一位资深命题教师，请严格返回 JSON 数组，不要有多余文字。"
    user = f"""为「{subject}」出一份{"期中" if exam_type == "midterm" else "期末"}考试试卷。
考察范围：{scope}，具体知识点：{items_text}

要求：
- 共 {count} 道题
- 题型：选择题{count//2}道 + 简答题{count//4}道 + 综合应用{count//4}道
- 难度分布：30%简单、50%中等、20%困难
- 题目新颖，考察理解和应用，不要死记硬背能答出的题
- 综合题要求综合运用多个知识点
- JSON 格式与小测验相同，增加 "score_weight": 分值

[
  {{
    "id": 1,
    "type": "choice",
    "domain": "知识点",
    "question": "...",
    "options": ["A...", "B...", "C...", "D..."],
    "answer": "B",
    "explanation": "...",
    "score_weight": 3,
    "difficulty": "easy"
  }}
]"""

    try:
        r = _client().chat.completions.create(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            messages=[{"role": "system", "content": system},
                      {"role": "user",   "content": user}],
            temperature=0.7, max_tokens=4000, stream=True
        )
        buffer = ""
        for chunk in r:
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


def evaluate_exam(subject: str, exam_type: str, questions: list, answers: list) -> tuple[float, str]:
    """批改考试，返回 (score 0-100, report)"""
    qa_text = ""
    for q, a in zip(questions, answers):
        qa_text += f"\n题{q['id']}（{q.get('domain','')}）[{q.get('score_weight',5)}分]：{q['question']}\n学生：{a}\n参考：{q.get('answer','')}\n"

    exam_name = "期中考试" if exam_type == "midterm" else "期末考试"
    r = _client().chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        messages=[
            {"role": "system", "content": "你是严格的阅卷教师，按百分制评分，返回 JSON 不要多余文字。"},
            {"role": "user", "content": (
                f"批改「{subject}」{exam_name}：\n{qa_text}\n\n"
                "返回JSON格式：\n"
                "{\"score\": 82, \"grade\": \"B\", \"report\": \"整体评价...\", "
                "\"strengths\": [\"...\"], \"weaknesses\": [\"...\"], "
                "\"suggestions\": \"下一步建议...\"}"
            )}
        ],
        temperature=0.3, max_tokens=2000,
    )
    raw = r.choices[0].message.content or ""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
    if raw.endswith("```"):
        raw = "\n".join(raw.split("\n")[:-1])
    try:
        data = json.loads(raw.strip())
        score = float(data.get("score", 0))
        parts = [f"## 成绩：{score}分（{data.get('grade','')}\n\n{data.get('report','')}"]
        if data.get("strengths"):
            parts.append("\n\n**✅ 优势**\n" + "\n".join(f"- {s}" for s in data["strengths"]))
        if data.get("weaknesses"):
            parts.append("\n\n**❌ 薄弱点**\n" + "\n".join(f"- {w}" for w in data["weaknesses"]))
        if data.get("suggestions"):
            parts.append(f"\n\n**💡 建议**\n{data['suggestions']}")
        return score, "".join(parts)
    except:
        return 0.0, "批改完成"
