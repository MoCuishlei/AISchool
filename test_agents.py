"""
Agent测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.agents import (
    create_orchestrator_agent,
    create_tutor_agent,
    create_question_generator_agent,
    create_evaluator_agent,
    create_memory_manager_agent
)

def test_agent_creation():
    """测试Agent创建"""
    print("🧪 测试Agent创建...")
    
    agents = {
        "总控Agent": create_orchestrator_agent(),
        "教学Agent": create_tutor_agent(),
        "出题Agent": create_question_generator_agent(),
        "测验Agent": create_evaluator_agent(),
        "记忆Agent": create_memory_manager_agent()
    }
    
    for name, agent in agents.items():
        print(f"\n{name}:")
        print(f"  角色: {agent.role}")
        print(f"  目标: {agent.goal}")
        print(f"  工具数量: {len(agent.tools)}")
        print(f"  允许委托: {agent.allow_delegation}")
    
    print(f"\n✅ 所有Agent创建成功，共{len(agents)}个Agent")

def test_tools():
    """测试工具函数"""
    print("\n🧪 测试工具函数...")
    
    from config.agents import (
        search_knowledge_base,
        generate_questions,
        evaluate_answer,
        save_learning_progress
    )
    
    # 测试知识库搜索
    print("1. 测试知识库搜索:")
    result = search_knowledge_base("Python变量")
    print(f"   结果: {result}")
    
    # 测试题目生成
    print("\n2. 测试题目生成:")
    questions = generate_questions("Python列表", "medium", 3)
    print(f"   生成的题目: {questions}")
    
    # 测试答案评估
    print("\n3. 测试答案评估:")
    evaluation = evaluate_answer("什么是Python列表？", "列表是Python中的可变序列")
    print(f"   评估结果: {evaluation}")
    
    # 测试进度保存
    print("\n4. 测试进度保存:")
    progress = {
        "student_id": "test_001",
        "topic": "Python基础",
        "score": 85,
        "completed": True
    }
    saved = save_learning_progress("test_001", progress)
    print(f"   保存状态: {saved}")
    
    print("\n✅ 所有工具测试完成")

def test_simple_interaction():
    """测试简单交互"""
    print("\n🧪 测试Agent简单交互...")
    
    # 创建教学Agent
    tutor = create_tutor_agent()
    
    print("模拟教学Agent讲解'Python函数':")
    print("=" * 40)
    
    # 模拟Agent思考过程
    print("🤔 Agent思考中...")
    print("💡 识别到用户想学习Python函数")
    print("📚 准备从基础概念开始讲解")
    print("🎯 教学目标: 让学生理解函数的定义和使用")
    
    print("\n📖 教学内容大纲:")
    print("1. 函数的基本语法")
    print("2. 参数和返回值")
    print("3. 作用域概念")
    print("4. 实际例子演示")
    
    print("\n✅ 教学准备完成")

if __name__ == "__main__":
    print("🎓 AI School - Agent测试套件")
    print("=" * 50)
    
    test_agent_creation()
    test_tools()
    test_simple_interaction()
    
    print("\n" + "=" * 50)
    print("🎉 所有测试完成!")
    print("\n下一步:")
    print("1. 设置OPENAI_API_KEY环境变量")
    print("2. 运行: python main.py (完整交互)")
    print("3. 运行: python run_local.py (演示模式)")