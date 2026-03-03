"""
高级功能示例
展示如何扩展和定制AI School系统
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from typing import Dict, Any, List
import json

# ==================== 自定义工具 ====================

@tool
def analyze_learning_style(text: str) -> Dict[str, Any]:
    """分析学生的学习风格"""
    # 这里可以集成更复杂的分析模型
    styles = ["visual", "auditory", "kinesthetic", "reading/writing"]
    return {
        "primary_style": "visual",
        "secondary_style": "reading/writing",
        "confidence": 0.85,
        "recommendations": [
            "使用图表和示意图",
            "提供代码示例",
            "分步骤讲解"
        ]
    }

@tool
def generate_interactive_exercise(topic: str, style: str) -> Dict[str, Any]:
    """根据学习风格生成交互式练习"""
    exercises = {
        "visual": f"为{topic}创建一个流程图或思维导图",
        "auditory": f"录制一个讲解{topic}的音频，然后自我复述",
        "kinesthetic": f"通过实际编码练习{topic}，边做边学",
        "reading/writing": f"阅读{topic}的相关文档，然后写一篇总结"
    }
    
    return {
        "exercise_type": exercises.get(style, "综合练习"),
        "description": f"适合{style}学习者的{topic}练习",
        "steps": ["准备材料", "开始练习", "检查结果", "反思总结"],
        "estimated_time": "30分钟"
    }

@tool  
def track_engagement(student_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
    """跟踪学生学习参与度"""
    return {
        "student_id": student_id,
        "engagement_score": 78,
        "focus_time": session_data.get("duration", 45),
        "interaction_count": session_data.get("interactions", 12),
        "recommendations": [
            "增加互动环节",
            "缩短单次学习时间",
            "添加更多实际例子"
        ]
    }

# ==================== 自定义Agent ====================

def create_learning_analyst_agent() -> Agent:
    """创建学习分析师Agent"""
    return Agent(
        role="学习分析师",
        goal="分析学生学习数据，提供个性化改进建议",
        backstory="""你是一位数据驱动的学习科学家，擅长通过分析学习行为数据，
        发现学生的学习模式和瓶颈，提供科学的改进建议。""",
        tools=[analyze_learning_style, track_engagement],
        verbose=True
    )

def create_interactive_designer_agent() -> Agent:
    """创建交互设计师Agent"""
    return Agent(
        role="交互学习设计师",
        goal="设计有趣、有效的交互式学习活动",
        backstory="""你是一位创新的教育设计师，擅长将枯燥的知识点转化为
        有趣的交互体验，让学生在学习中保持高度参与。""",
        tools=[generate_interactive_exercise],
        verbose=True
    )

# ==================== 自定义任务 ====================

def create_learning_analysis_task(analyst_agent, student_data: Dict[str, Any]) -> Task:
    """创建学习分析任务"""
    return Task(
        description=f"""分析学生的学习数据，提供个性化建议。
        
        学生数据：{json.dumps(student_data, ensure_ascii=False, indent=2)}
        
        请分析：
        1. 学习风格偏好
        2. 学习效率评估
        3. 参与度分析
        4. 个性化改进建议""",
        agent=analyst_agent,
        expected_output="详细的学习分析报告和改进方案"
    )

def create_interactive_design_task(designer_agent, topic: str, 
                                  learning_style: str) -> Task:
    """创建交互设计任务"""
    return Task(
        description=f"""为{topic}主题设计适合{learning_style}学习者的交互式学习活动。
        
        设计要求：
        1. 符合学习风格偏好
        2. 有趣且有效
        3. 包含明确的步骤
        4. 提供反馈机制""",
        agent=designer_agent,
        expected_output=f"针对{topic}的交互式学习活动设计"
    )

# ==================== 扩展的学习Crew ====================

class AdvancedLearningCrew:
    """扩展的学习Crew，包含高级功能"""
    
    def __init__(self, student_id: str = "advanced_student"):
        self.student_id = student_id
        self.agents = self._create_agents()
        
    def _create_agents(self):
        """创建所有Agent（包括基础Agent和扩展Agent）"""
        from config.agents import (
            create_orchestrator_agent,
            create_tutor_agent,
            create_question_generator_agent
        )
        
        return {
            "orchestrator": create_orchestrator_agent(),
            "tutor": create_tutor_agent(),
            "question_generator": create_question_generator_agent(),
            "analyst": create_learning_analyst_agent(),
            "designer": create_interactive_designer_agent()
        }
    
    def personalized_learning_path(self, topic: str, student_profile: Dict[str, Any]):
        """个性化学习路径"""
        print(f"🎯 为{student_profile.get('name')}创建个性化学习路径")
        print(f"主题: {topic}")
        
        # 1. 学习风格分析
        analysis_task = create_learning_analysis_task(
            self.agents["analyst"],
            student_profile
        )
        
        # 2. 交互式学习设计
        design_task = create_interactive_design_task(
            self.agents["designer"],
            topic,
            student_profile.get("learning_style", "visual")
        )
        
        # 3. 教学任务
        from config.tasks import create_teach_topic_task
        teach_task = create_teach_topic_task(
            self.agents["tutor"],
            topic,
            student_profile.get("level", "beginner")
        )
        
        # 创建Crew
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=[analysis_task, design_task, teach_task],
            process=Process.sequential,
            verbose=True,
            memory=True
        )
        
        return crew.kickoff()
    
    def gamified_learning_session(self, topic: str, game_type: str = "quest"):
        """游戏化学习会话"""
        print(f"🎮 游戏化学习: {topic}")
        print(f"游戏类型: {game_type}")
        
        # 这里可以集成更复杂的游戏化逻辑
        game_elements = {
            "quest": {"name": "知识探索任务", "reward": "智慧勋章"},
            "challenge": {"name": "技能挑战赛", "reward": "挑战者证书"},
            "puzzle": {"name": "解谜学习", "reward": "解谜大师称号"}
        }
        
        game = game_elements.get(game_type, game_elements["quest"])
        
        from config.tasks import create_teach_topic_task
        teach_task = Task(
            description=f"""以{game['name']}的形式讲解{topic}。
            
            游戏化要求：
            1. 将知识点转化为任务目标
            2. 设置阶段性奖励
            3. 添加挑战元素
            4. 提供即时反馈
            5. 最终奖励: {game['reward']}""",
            agent=self.agents["tutor"],
            expected_output=f"游戏化的{topic}教学内容"
        )
        
        crew = Crew(
            agents=[self.agents["tutor"], self.agents["designer"]],
            tasks=[teach_task],
            process=Process.sequential,
            verbose=True
        )
        
        return crew.kickoff()

# ==================== 示例函数 ====================

def example_personalized_learning():
    """示例：个性化学习"""
    print("示例: 个性化学习路径")
    print("=" * 50)
    
    crew = AdvancedLearningCrew(student_id="personalized_001")
    
    student_profile = {
        "name": "小红",
        "age": 16,
        "level": "intermediate",
        "learning_style": "visual",
        "previous_scores": {"math": 85, "programming": 78},
        "preferences": {
            "prefers_examples": True,
            "likes_challenges": True,
            "needs_breaks": True
        },
        "learning_history": [
            {"topic": "Python基础", "score": 82, "duration": "2小时"},
            {"topic": "函数编程", "score": 75, "duration": "3小时"}
        ]
    }
    
    print(f"学生档案分析:")
    for key, value in student_profile.items():
        if key != "learning_history":
            print(f"  {key}: {value}")
    
    print(f"\n学习历史:")
    for history in student_profile["learning_history"]:
        print(f"  - {history['topic']}: 分数{history['score']}, 时长{history['duration']}")
    
    result = crew.personalized_learning_path(
        topic="Python面向对象编程",
        student_profile=student_profile
    )
    
    print(f"\n个性化学习方案:")
    print("-" * 30)
    print(result)
    
    return result

def example_gamified_learning():
    """示例：游戏化学习"""
    print("\n\n示例: 游戏化学习")
    print("=" * 50)
    
    crew = AdvancedLearningCrew(student_id="gamified_001")
    
    result = crew.gamified_learning_session(
        topic="Python异常处理",
        game_type="quest"
    )
    
    print(f"游戏化学习内容:")
    print("-" * 30)
    print(result)
    
    return result

def example_custom_tool_integration():
    """示例：自定义工具集成"""
    print("\n\n示例: 自定义工具集成")
    print("=" * 50)
    
    # 测试自定义工具
    print("1. 测试学习风格分析工具:")
    style_analysis = analyze_learning_style("喜欢看图表和视频学习")
    print(f"   分析结果: {style_analysis}")
    
    print("\n2. 测试交互练习生成工具:")
    exercise = generate_interactive_exercise("Python列表", "visual")
    print(f"   生成的练习: {exercise}")
    
    print("\n3. 测试参与度跟踪工具:")
    engagement = track_engagement("test_001", {
        "duration": 60,
        "interactions": 15,
        "topic": "Python基础"
    })
    print(f"   参与度分析: {engagement}")
    
    print("\n✅ 所有自定义工具测试完成")

def main():
    """主函数"""
    print("🚀 AI School - 高级功能示例")
    print("=" * 60)
    
    print("本示例展示如何扩展AI School系统:")
    print("1. 添加自定义工具")
    print("2. 创建新的Agent角色")
    print("3. 实现个性化学习")
    print("4. 集成游戏化元素")
    print()
    
    examples = [
        ("个性化学习路径", example_personalized_learning),
        ("游戏化学习", example_gamified_learning),
        ("自定义工具集成", example_custom_tool_integration)
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    print(f"{len(examples) + 1}. 运行所有示例")
    print(f"{len(examples) + 2}. 退出")
    
    try:
        choice = int(input("\n请选择示例 (1-5): ").strip())
    except ValueError:
        print("❌ 请输入数字")
        return
    
    if 1 <= choice <= len(examples):
        name, func = examples[choice - 1]
        print(f"\n运行: {name}")
        print("=" * 60)
        func()
        
    elif choice == len(examples) + 1:
        for name, func in examples:
            print(f"\n运行: {name}")
            print("=" * 60)
            func()
            input("\n按Enter键继续下一个示例...")
            
    elif choice == len(examples) + 2:
        print("👋 退出")
        return
        
    else:
        print("❌ 无效选择")
        return
    
    print("\n" + "=" * 60)
    print("🎉 高级功能示例完成!")
    print("\n扩展建议:")
    print("1. 在 config/agents.py 中添加更多专业Agent")
    print("2. 创建学科特定的工具函数")
    print("3. 集成外部API（如题库API、视频API）")
    print("4. 实现学习数据分析和可视化")

if __name__ == "__main__":
    main()