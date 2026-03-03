"""
基础使用示例
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置环境变量（演示用）
os.environ["OPENAI_API_KEY"] = "your_api_key_here"  # 替换为你的API密钥

from core.learning_crew import LearningCrew

def example_complete_session():
    """示例：完整学习会话"""
    print("示例1: 完整学习会话")
    print("=" * 50)
    
    # 创建学习Crew
    crew = LearningCrew(student_id="example_student_001")
    
    # 学生信息
    student_info = {
        "name": "小明",
        "level": "beginner",
        "goals": ["学习Python基础", "能够编写简单程序"],
        "preferences": {
            "learning_style": "visual",
            "pace": "moderate"
        }
    }
    
    # 创建学习会话
    crew.create_learning_session(
        topic="Python变量和数据类型",
        student_info=student_info
    )
    
    print(f"学生: {student_info['name']}")
    print(f"主题: Python变量和数据类型")
    print(f"水平: {student_info['level']}")
    print(f"目标: {', '.join(student_info['goals'])}")
    
    # 运行学习会话
    print("\n开始学习流程...")
    result = crew.run()
    
    print(f"\n学习结果摘要:")
    print("-" * 30)
    print(result)
    
    return result

def example_quick_teach():
    """示例：快速教学"""
    print("\n\n示例2: 快速教学")
    print("=" * 50)
    
    crew = LearningCrew(student_id="example_student_002")
    
    # 快速教学
    result = crew.quick_teach(
        topic="Python函数定义",
        question="如何定义一个简单的函数？"
    )
    
    print(f"教学主题: Python函数定义")
    print(f"\n教学内容:")
    print("-" * 30)
    print(result)
    
    return result

def example_practice_generation():
    """示例：练习题生成"""
    print("\n\n示例3: 练习题生成")
    print("=" * 50)
    
    crew = LearningCrew(student_id="example_student_003")
    
    # 生成练习题
    result = crew.generate_practice(
        topic="Python列表操作",
        difficulty="medium",
        count=5
    )
    
    print(f"主题: Python列表操作")
    print(f"难度: medium")
    print(f"数量: 5题")
    print(f"\n生成的练习题:")
    print("-" * 30)
    print(result)
    
    return result

def example_custom_agent_interaction():
    """示例：自定义Agent交互"""
    print("\n\n示例4: 自定义Agent工作流")
    print("=" * 50)
    
    from crewai import Crew, Process
    from config.agents import create_tutor_agent, create_question_generator_agent
    from config.tasks import create_teach_topic_task, create_generate_questions_task
    
    # 创建特定的Agent
    tutor = create_tutor_agent()
    question_generator = create_question_generator_agent()
    
    # 创建自定义任务
    teach_task = create_teach_topic_task(tutor, "Python字典", "intermediate")
    practice_task = create_generate_questions_task(question_generator, "Python字典", "intermediate", 3)
    
    # 创建自定义Crew
    custom_crew = Crew(
        agents=[tutor, question_generator],
        tasks=[teach_task, practice_task],
        process=Process.sequential,
        verbose=True
    )
    
    print("自定义工作流: 教学 + 练习")
    print("主题: Python字典")
    print("水平: intermediate")
    
    result = custom_crew.kickoff()
    
    print(f"\n自定义工作流结果:")
    print("-" * 30)
    print(result)
    
    return result

def main():
    """主函数"""
    print("🎓 AI School - 使用示例")
    print("=" * 60)
    
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("⚠️  注意: 未设置有效的OPENAI_API_KEY")
        print("以下示例将展示代码结构，实际运行需要设置API密钥")
        print("设置方法: export OPENAI_API_KEY=your_key_here")
        print("或在代码中设置: os.environ['OPENAI_API_KEY'] = 'your_key'")
        print()
    
    examples = [
        ("完整学习会话", example_complete_session),
        ("快速教学", example_quick_teach),
        ("练习题生成", example_practice_generation),
        ("自定义Agent工作流", example_custom_agent_interaction)
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{i}. {name}")
    
    print(f"\n{len(examples) + 1}. 运行所有示例")
    print(f"{len(examples) + 2}. 退出")
    
    try:
        choice = int(input("\n请选择示例 (1-6): ").strip())
    except ValueError:
        print("❌ 请输入数字")
        return
    
    if 1 <= choice <= len(examples):
        # 运行单个示例
        name, func = examples[choice - 1]
        print(f"\n运行: {name}")
        print("=" * 60)
        func()
        
    elif choice == len(examples) + 1:
        # 运行所有示例
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
    print("🎉 示例运行完成!")
    print("\n下一步建议:")
    print("1. 查看 config/ 目录下的Agent和任务配置")
    print("2. 修改 core/learning_crew.py 自定义学习流程")
    print("3. 运行 test_agents.py 测试Agent功能")
    print("4. 启动Web API: python -m uvicorn api.main:app --reload")

if __name__ == "__main__":
    main()