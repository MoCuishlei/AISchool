"""
任务定义
"""

from crewai import Task
from typing import Dict, Any

def create_assess_student_task(orchestrator_agent, student_info: Dict[str, Any]) -> Task:
    """创建评估学生任务"""
    return Task(
        description=f"""评估学生 {student_info.get('name', '新学生')} 的学习需求。
        学生信息：{student_info}
        
        请分析：
        1. 学生的当前水平
        2. 学习目标
        3. 适合的学习风格
        4. 建议的学习计划""",
        agent=orchestrator_agent,
        expected_output="详细的学生评估报告和学习计划建议"
    )

def create_teach_topic_task(tutor_agent, topic: str, student_level: str) -> Task:
    """创建教学任务"""
    return Task(
        description=f"""为{student_level}水平的学生讲解{topic}知识点。
        
        要求：
        1. 从基础概念开始讲解
        2. 使用生动的例子和类比
        3. 提供实际应用场景
        4. 总结关键要点""",
        agent=tutor_agent,
        expected_output=f"关于{topic}的完整教学内容和学习指导"
    )

def create_generate_questions_task(question_generator_agent, topic: str, 
                                  difficulty: str, count: int = 5) -> Task:
    """创建出题任务"""
    return Task(
        description=f"""为{topic}主题设计{difficulty}难度的{count}道练习题。
        
        题目要求：
        1. 覆盖知识点的不同方面
        2. 难度适中，符合{difficulty}级别
        3. 包含选择题、填空题、简答题等不同题型
        4. 提供参考答案""",
        agent=question_generator_agent,
        expected_output=f"{count}道关于{topic}的练习题及参考答案"
    )

def create_evaluate_learning_task(evaluator_agent, student_answers: Dict[str, Any]) -> Task:
    """创建评估任务"""
    return Task(
        description=f"""评估学生的学习成果。
        
        学生答案：{student_answers}
        
        请提供：
        1. 总体评分和评价
        2. 每道题的详细反馈
        3. 知识掌握情况分析
        4. 后续学习建议""",
        agent=evaluator_agent,
        expected_output="详细的学习评估报告和改进建议"
    )

def create_update_memory_task(memory_manager_agent, student_id: str, 
                             learning_data: Dict[str, Any]) -> Task:
    """创建更新记忆任务"""
    return Task(
        description=f"""更新学生{student_id}的学习记录。
        
        学习数据：{learning_data}
        
        需要记录：
        1. 学习过的知识点
        2. 练习题的完成情况
        3. 测验成绩
        4. 学习偏好和习惯""",
        agent=memory_manager_agent,
        expected_output="学习记录更新确认和数据分析摘要"
    )