"""
大纲生成 + 三色标记 + 推荐学习路径
"""
import json
import re
from typing import List, Dict
from config.llm_config import LLMConfig


# 颜色展示
COLOR_ICON = {"red": "🔴", "yellow": "🟡", "green": "🟢"}
COLOR_LABEL = {"red": "未掌握", "yellow": "部分掌握", "green": "已掌握"}


def _ask(task_description: str, expected: str = "JSON") -> str:
    from crewai import Agent, Task, Crew
    agent = Agent(
        role="课程规划专家",
        goal="生成结构化的学习大纲",
        backstory="你是一位资深课程设计师，擅长拆解知识体系并评估学生掌握情况。",
        verbose=False,
        llm=LLMConfig.get_llm(),
    )
    task = Task(description=task_description, agent=agent, expected_output=expected)
    crew = Crew(agents=[agent], tasks=[task], verbose=False, memory=False)
    return str(crew.kickoff())


def generate_outline(topic: str, level: str, diagnostic_result: str) -> List[Dict]:
    """
    根据话题、水平和诊断结果生成三色学习大纲。
    返回：[{"title": str, "description": str, "color": "red"|"yellow"|"green"}]
    """
    prompt = f"""
你是一位课程设计专家。请为主题「{topic}」（学生水平：{level}）生成学习大纲，
并根据以下诊断结果，标注每个知识点的初始掌握状态。

诊断结果：
{diagnostic_result}

掌握状态规则：
- green（已掌握）：诊断中表现良好的相关知识点
- yellow（部分掌握）：诊断中有偏差或不完整的相关知识点  
- red（未掌握）：诊断中答错、跳过，或未涉及但{level}水平必须学的知识点

请输出 6-10 个知识点，严格按以下 JSON 数组格式输出，不要包含任何其他文字：
[
  {{"title": "知识点名称", "description": "简短说明（一句话）", "color": "red/yellow/green"}},
  ...
]
"""
    raw = _ask(prompt, expected="JSON数组，包含title/description/color字段")

    # 提取 JSON
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        try:
            items = json.loads(match.group())
            # 校验并补全字段
            result = []
            for i, item in enumerate(items):
                result.append({
                    "title": item.get("title", f"知识点 {i+1}"),
                    "description": item.get("description", ""),
                    "color": item.get("color", "red") if item.get("color") in ("red","yellow","green") else "red",
                })
            return result
        except json.JSONDecodeError:
            pass

    # 解析失败时的降级方案：返回全红大纲
    print("⚠️  大纲解析失败，使用默认大纲")
    return [{"title": f"{topic} 基础概念 {i+1}", "description": "", "color": "red"} for i in range(5)]


def recommend_next(items: List[Dict]) -> str:
    """根据三色状态推荐下一步学习顺序"""
    reds    = [it for it in items if it.get("color") == "red"]
    yellows = [it for it in items if it.get("color") == "yellow"]
    greens  = [it for it in items if it.get("color") == "green"]

    lines = ["", "📌 **推荐学习顺序**："]

    if reds:
        lines.append(f"  🔴 优先学习（未掌握）：{', '.join(r['title'] for r in reds)}")
    if yellows:
        lines.append(f"  🟡 巩固提升（部分掌握）：{', '.join(y['title'] for y in yellows)}")
    if greens:
        lines.append(f"  🟢 复习回顾（已掌握）：{', '.join(g['title'] for g in greens)}")

    if not reds and not yellows:
        lines.append("  🎉 恭喜！所有知识点已掌握，可以挑战更高级内容！")

    return "\n".join(lines)


def display_outline(items: List[Dict], title: str = "学习大纲") -> str:
    """格式化显示大纲"""
    lines = [f"\n📚 **{title}**", "─" * 55]
    for i, item in enumerate(items, 1):
        icon = COLOR_ICON.get(item.get("color", "red"), "🔴")
        label = COLOR_LABEL.get(item.get("color", "red"), "")
        desc = f"  → {item['description']}" if item.get("description") else ""
        lines.append(f"  {i:2}. {icon} {item['title']}  [{label}]{desc}")
    lines.append("─" * 55)
    return "\n".join(lines)


def update_outline_from_quiz(items: List[Dict], quiz_result: str) -> List[Dict]:
    """
    根据测验批改结果更新大纲颜色。
    quiz_result: 测验反馈文本
    返回更新后的 items（含 id 字段，可直接用于 storage.update_item_color）
    """
    # 让 AI 判断哪些知识点有进步
    titles = [it["title"] for it in items]
    prompt = f"""
根据以下测验反馈，判断这些知识点各应更新为什么颜色。

知识点列表：{titles}

测验反馈：
{quiz_result}

颜色规则：
- green：学生回答正确、完整
- yellow：回答有偏差或不完整  
- red：明显答错或未掌握

请严格按以下 JSON 格式输出，不包含其他文字：
{{"知识点名称": "green/yellow/red", ...}}
"""
    raw = _ask(prompt, expected="JSON对象，知识点名称到颜色的映射")

    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        try:
            mapping = json.loads(match.group())
            for item in items:
                new_color = mapping.get(item["title"])
                if new_color in ("red", "yellow", "green"):
                    item["color"] = new_color
        except json.JSONDecodeError:
            pass

    return items
