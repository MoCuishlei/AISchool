"""
课堂专用 LLM — 知识点讲解、对话、小测验
"""

import json, os, base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def _client():
    return OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
    )


def _chat_messages(messages: list, temperature: float = 0.7) -> str:
    r = _client().chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        messages=messages,
        temperature=temperature,
        max_tokens=3000,
    )
    return r.choices[0].message.content or ""


def start_lesson(subject: str, item_title: str, attempt: int = 1) -> str:
    """开始上课：提供知识点定义 + 例题"""
    prompt_extra = ""
    if attempt > 1:
        prompt_extra = f"\n（这是第{attempt}次讲解，请换一种方式、增加新的例子来解释）"

    messages = [
        {
            "role": "system",
            "content": (
                "你是一位耐心的学科教师，用清晰易懂的方式教学。"
                "所有数学公式必须使用 LaTeX 格式：行内公式使用 $公式$，独占一行的公式使用 $$公式$$。"
                "请按以下结构讲解：\n"
                "## 📖 定义\n"
                "## 💡 例题\n（给出2-3个从简单到复杂的例子）\n"
                "## ⚠️ 常见误区\n"
                "## 💬 欢迎提问"
            )
        },
        {
            "role": "user",
            "content": f"请讲解「{subject}」课程中的知识点：「{item_title}」{prompt_extra}"
        }
    ]
    return _chat_messages(messages)


def ask_question(subject: str, item_title: str, lesson_content: str,
                 history: list, student_question: str) -> str:
    """学生自由提问，AI 即时解答"""
    messages = [
        {
            "role": "system",
            "content": (
                f"你是「{subject}」的学科教师，正在讲解「{item_title}」。"
                "回答要简洁、有针对性，可以补充例子，不要重复已讲过的内容。"
                "所有数学公式必须使用 LaTeX 格式：行内公式用 $公式$，独立公式用 $$公式$$，不要直接输出裸式LaTeX。"
            )
        },
        {
            "role": "assistant",
            "content": lesson_content
        }
    ]
    # 加入历史对话
    for msg in history[-6:]:  # 最多保留最近6条
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": student_question})
    return _chat_messages(messages)


def generate_mini_quiz(subject: str, item_title: str, count: int = 4) -> list:
    """生成小测验题目（联网+变形题，保证新颖性）"""
    system = "你是一位出题专家，请严格返回 JSON 数组，不要有多余文字。"
    user = f"""请为「{subject} - {item_title}」出 {count} 道小测验题。
要求：
- 不要出教科书上的原题，要求是变形题或应用型题目
- 题型：选择题和简答题混合（2道选择+2道简答）
- 考察理解而非记忆，学生若只死记硬背就无法作答
- 简答题要求有一定思考量
- JSON 格式：
[
  {{
    "id": 1,
    "type": "choice",
    "question": "题目（变形或应用场景）",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "answer": "B",
    "explanation": "解析说明"
  }},
  {{
    "id": 2,
    "type": "open",
    "question": "简答题目（需要理解才能作答）",
    "answer": "参考答案要点",
    "explanation": "评分要点"
  }}
]"""
    raw = _client().chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        messages=[{"role": "system", "content": system},
                  {"role": "user",   "content": user}],
        temperature=0.8,  # 稍高温度增加多样性
        max_tokens=2000,
    ).choices[0].message.content or ""

    raw = raw.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
    if raw.endswith("```"):
        raw = "\n".join(raw.split("\n")[:-1])
    try:
        return json.loads(raw.strip())
    except:
        return []

def generate_mini_quiz_stream(subject: str, item_title: str, count: int = 4):
    """流式生成小测验题目，实时 yield 状态和数据"""
    system = "你是一位出题专家，请严格返回 JSON 数组，不要有多余文字。"
    user = f"""请为「{subject} - {item_title}」出 {count} 道小测验题。
要求：
- 不要出教科书上的原题，要求是变形题或应用型题目
- 题型：选择题和简答题混合（2道选择+2道简答）
- 考察理解而非记忆，学生若只死记硬背就无法作答
- 简答题要求有一定思考量
- JSON 格式：
[
  {{
    "id": 1,
    "type": "choice",
    "question": "题目（变形或应用场景）",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "answer": "B",
    "explanation": "解析说明"
  }},
  {{
    "id": 2,
    "type": "open",
    "question": "简答题目（需要理解才能作答）",
    "answer": "参考答案要点",
    "explanation": "评分要点"
  }}
]"""
    try:
        response = _client().chat.completions.create(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            messages=[{"role": "system", "content": system},
                      {"role": "user",   "content": user}],
            temperature=0.8, max_tokens=2000, stream=True
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


def evaluate_quiz(subject: str, item_title: str, questions: list,
                  answers: list, images: list = None) -> tuple[float, bool, str]:
    """批改小测验 (score 0-100, passed, feedback)"""
    qa_text = ""
    for q, a in zip(questions, answers):
        qa_text += f"\n题{q['id']}：{q['question']}\n学生答案：{a}\n参考答案：{q.get('answer','')}\n"

    # 如果有图片（base64），追加到内容
    content_parts = []
    if images:
        for img_b64 in images:
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
            })
    content_parts.append({
        "type": "text",
        "text": f"请批改「{subject} - {item_title}」的小测验：\n{qa_text}\n\n请返回JSON：{{\"score\": 85, \"passed\": true, \"feedback\": \"...\", \"weak_points\": [\"...\"]}}",
    })

    try:
        r = _client().chat.completions.create(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            messages=[
                {"role": "system", "content": "你是严格公正的评分老师，请返回 JSON 不要有多余文字。"},
                {"role": "user", "content": content_parts if images else content_parts[0]["text"]}
            ],
            temperature=0.3, max_tokens=1500,
        )
        raw = r.choices[0].message.content or ""
    except Exception as e:
        # Vision 不支持时回退到纯文字
        raw = _chat_messages([
            {"role": "system", "content": "你是严格公正的评分老师，请返回 JSON 不要有多余文字。"},
            {"role": "user", "content": f"批改「{subject} - {item_title}」小测验：\n{qa_text}\n返回JSON：{{\"score\": 85, \"passed\": true, \"feedback\": \"...\", \"weak_points\": []}}"}
        ], temperature=0.3)

    raw = raw.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
    if raw.endswith("```"):
        raw = "\n".join(raw.split("\n")[:-1])
    try:
        data = json.loads(raw.strip())
        score = float(data.get("score", 0))
        passed = bool(data.get("passed", score >= 70))
        feedback = data.get("feedback", "")
        weak = data.get("weak_points", [])
        if weak:
            feedback += "\n\n**薄弱点：**\n" + "\n".join(f"- {w}" for w in weak)
        return score, passed, feedback
    except:
        return 0.0, False, "批改出现问题，请重试"
