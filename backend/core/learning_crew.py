"""
学习辅导Crew - 核心多Agent协作系统
"""

from crewai import Crew, Process
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

from config.agents import (
    create_orchestrator_agent,
    create_tutor_agent,
    create_question_generator_agent,
    create_evaluator_agent,
    create_memory_manager_agent
)

from config.tasks import (
    create_assess_student_task,
    create_teach_topic_task,
    create_generate_questions_task,
    create_evaluate_learning_task,
    create_update_memory_task
)

# 加载环境变量
load_dotenv()

class LearningCrew:
    """学习辅导Crew"""
    
    def __init__(self, student_id: str = "default_student"):
        self.student_id = student_id
        self.agents = self._create_agents()
        self.crew = None
        
    def _create_agents(self):
        """创建所有Agent"""
        return {
            "orchestrator": create_orchestrator_agent(),
            "tutor": create_tutor_agent(),
            "question_generator": create_question_generator_agent(),
            "evaluator": create_evaluator_agent(),
            "memory_manager": create_memory_manager_agent()
        }
    
    def create_learning_session(self, topic: str, student_info: Dict[str, Any] = None):
        """创建完整的学习会话"""
        if student_info is None:
            student_info = {
                "name": "新学生",
                "level": "beginner",
                "goals": [f"学习{topic}"]
            }
        
        # 创建任务序列
        tasks = [
            # 1. 评估学生
            create_assess_student_task(
                self.agents["orchestrator"], 
                student_info
            ),
            
            # 2. 教学讲解
            create_teach_topic_task(
                self.agents["tutor"],
                topic,
                student_info.get("level", "beginner")
            ),
            
            # 3. 生成练习题
            create_generate_questions_task(
                self.agents["question_generator"],
                topic,
                student_info.get("level", "beginner"),
                count=3
            ),
            
            # 4. 模拟评估（这里用示例答案）
            create_evaluate_learning_task(
                self.agents["evaluator"],
                {"topic": topic, "answers": ["示例答案1", "示例答案2"]}
            ),
            
            # 5. 更新学习记录
            create_update_memory_task(
                self.agents["memory_manager"],
                self.student_id,
                {
                    "topic": topic,
                    "completed": True,
                    "score": 85,
                    "feedback": "学习完成"
                }
            )
        ]
        
        # 创建Crew
        self.crew = Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            process=Process.sequential,  # 顺序执行
            verbose=True,
            memory=False  # 关闭内置记忆（需要OpenAI Embedding，与DeepSeek不兼容）
        )
        
        return self
    
    def run(self):
        """运行学习会话"""
        if not self.crew:
            raise ValueError("请先调用 create_learning_session 创建会话")
        
        print(f"🚀 开始学习会话 - 学生: {self.student_id}")
        print("=" * 50)
        
        result = self.crew.kickoff()
        
        print("=" * 50)
        print("✅ 学习会话完成")
        
        return result
    
    def quick_teach(self, topic: str, question: str = None):
        """快速教学模式"""
        print(f"📚 快速教学: {topic}")
        
        # 只使用教学Agent
        from crewai import Crew
        quick_crew = Crew(
            agents=[self.agents["tutor"]],
            tasks=[
                create_teach_topic_task(
                    self.agents["tutor"],
                    topic,
                    "general"
                )
            ],
            verbose=True
        )
        
        return quick_crew.kickoff()
    
    def generate_practice(self, topic: str, difficulty: str = "medium", count: int = 5):
        """生成练习题"""
        print(f"📝 生成练习题: {topic} ({difficulty}难度)")
        
        from crewai import Crew
        practice_crew = Crew(
            agents=[self.agents["question_generator"]],
            tasks=[
                create_generate_questions_task(
                    self.agents["question_generator"],
                    topic,
                    difficulty,
                    count
                )
            ],
            verbose=True
        )
        
        return practice_crew.kickoff()