"""
Agent配置定义 - 支持多种LLM模型
"""

from crewai import Agent
from crewai.tools import tool
from typing import Any
from config.llm_config import LLMConfig

# 工具定义
@tool("search_knowledge_base")
def search_knowledge_base(query: str) -> str:
    """从知识库中搜索相关知识点"""
    # 这里可以集成向量数据库搜索
    return f"搜索知识点: {query}"

@tool("save_learning_progress")
def save_learning_progress(student_id: str, progress: str) -> str:
    """保存学生学习进度，progress为进度描述字符串"""
    print(f"保存学生 {student_id} 的学习进度: {progress}")
    return "进度已保存"

@tool("generate_questions")
def generate_questions(topic: str, difficulty: str, count: str = "5") -> str:
    """根据主题和难度生成题目，返回题目列表文本"""
    n = int(count) if str(count).isdigit() else 5
    questions = [
        f"{topic} 相关题目 {i+1} (难度: {difficulty})"
        for i in range(n)
    ]
    return "\n".join(questions)

@tool("evaluate_answer")
def evaluate_answer(question: str, answer: str) -> str:
    """评估学生答案，返回评估结果文本"""
    return (
        "评估结果：正确\n"
        "得分：85分\n"
        "反馈：回答基本正确，可以更详细一些\n"
        "建议：尝试提供更多例子；解释背后的原理"
    )

# Agent定义 - 使用统一的LLM配置
def create_orchestrator_agent() -> Agent:
    """创建总控Agent"""
    return Agent(
        role="学习总控",
        goal="协调所有学习Agent，为学生制定个性化学习计划",
        backstory="""你是一位经验丰富的教育协调专家，擅长分析学生的学习需求，
        制定科学的学习路径，并协调各个学科专家共同工作。""",
        tools=[search_knowledge_base, save_learning_progress],
        verbose=True,
        allow_delegation=True,
        llm=LLMConfig.get_llm()
    )

def create_tutor_agent() -> Agent:
    """创建教学Agent"""
    return Agent(
        role="学科教学专家",
        goal="用清晰易懂的方式讲解知识点，解答学生疑问",
        backstory="""你是一位有10年教学经验的学科专家，擅长将复杂的概念
        转化为简单易懂的语言，善于使用例子和类比帮助学生理解。""",
        tools=[search_knowledge_base],
        verbose=True,
        llm=LLMConfig.get_llm()
    )

def create_question_generator_agent() -> Agent:
    """创建出题Agent"""
    return Agent(
        role="题目设计专家",
        goal="根据学习进度和难度要求，设计高质量的练习题",
        backstory="""你是一位专业的题目设计师，擅长设计各种难度级别的题目，
        能够准确把握知识点的考察重点，设计出既有趣又有挑战性的题目。""",
        tools=[generate_questions],
        verbose=True,
        llm=LLMConfig.get_llm()
    )

def create_evaluator_agent() -> Agent:
    """创建测验Agent"""
    return Agent(
        role="学习评估专家",
        goal="评估学生的学习效果，提供详细的反馈和改进建议",
        backstory="""你是一位严谨的教育评估专家，擅长通过多种方式评估学习效果，
        能够给出具体、可操作的改进建议，帮助学生持续进步。""",
        tools=[evaluate_answer],
        verbose=True,
        llm=LLMConfig.get_llm()
    )

def create_memory_manager_agent() -> Agent:
    """创建记忆管理Agent"""
    return Agent(
        role="学习记忆管家",
        goal="管理学生的学习历史、知识点掌握情况和学习偏好",
        backstory="""你是一位细心的学习记录员，擅长整理和分析学习数据，
        能够准确记录学生的学习轨迹，为个性化教学提供数据支持。""",
        tools=[save_learning_progress],
        verbose=True,
        llm=LLMConfig.get_llm()
    )