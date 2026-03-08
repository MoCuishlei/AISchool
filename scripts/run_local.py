"""
本地运行脚本 - 使用当前会话的模型配置
"""

import sys
import os

# 添加项目根目录和 backend 目录到 Python 路径
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(backend_dir)

# 使用当前OpenClaw会话的模型配置
# 从环境变量或默认配置获取
current_model = os.getenv("OPENCLAW_MODEL", "deepseek/deepseek-chat")

# 设置环境变量
os.environ["LLM_PROVIDER"] = "deepseek"
os.environ["DEEPSEEK_MODEL"] = current_model

# 尝试使用当前会话的API密钥
api_key = os.getenv("OPENAI_API_KEY")  # OpenClaw可能设置了这个
if api_key and api_key != "your_openai_api_key_here":
    os.environ["DEEPSEEK_API_KEY"] = api_key
    print(f"✅ 使用当前会话的API密钥")
else:
    print("⚠️  未检测到API密钥，使用演示模式")

from backend.core.learning_crew import LearningCrew
from backend.config.llm_config import LLMConfig

def demo_learning_session():
    """演示完整学习会话"""
    print("🎓 AI School - 演示模式")
    print("=" * 40)
    
    # 创建学习Crew
    crew = LearningCrew(student_id="demo_student_001")
    
    # 演示1: 完整学习会话
    print("\n1. 完整学习会话演示")
    print("-" * 30)
    
    student_info = {
        "name": "张三",
        "level": "beginner",
        "goals": ["学习Python基础", "掌握编程思维"]
    }
    
    crew.create_learning_session("Python变量和数据类型", student_info)
    
    print("开始模拟学习流程...")
    print("(注: 实际运行需要真实的API密钥)")
    
    # 模拟输出
    print("\n📋 学习计划:")
    print("1. 评估学生水平 - 已完成")
    print("2. 讲解Python变量概念 - 已完成")
    print("3. 生成练习题 - 已完成")
    print("4. 评估学习效果 - 已完成")
    print("5. 更新学习记录 - 已完成")
    
    print("\n✅ 学习会话模拟完成")
    print("如需实际运行，请设置OPENAI_API_KEY环境变量")

def demo_quick_teach():
    """演示快速教学"""
    print("\n2. 快速教学演示")
    print("-" * 30)
    
    crew = LearningCrew(student_id="demo_student_002")
    
    print("主题: Python函数定义")
    print("\n教学内容大纲:")
    print("1. 函数的基本语法: def function_name():")
    print("2. 参数传递: 位置参数、关键字参数")
    print("3. 返回值: return语句")
    print("4. 作用域: 局部变量和全局变量")
    print("5. 实际例子: 计算器函数")
    
    print("\n🎯 学习目标: 能够定义和使用简单的Python函数")

def demo_practice_generation():
    """演示练习题生成"""
    print("\n3. 练习题生成演示")
    print("-" * 30)
    
    crew = LearningCrew(student_id="demo_student_003")
    
    print("主题: Python列表操作")
    print("难度: medium")
    print("数量: 5题")
    
    print("\n📝 示例题目:")
    print("1. 如何创建一个包含数字1-10的列表？")
    print("2. 如何向列表末尾添加元素？")
    print("3. 如何从列表中删除特定元素？")
    print("4. 如何对列表进行排序？")
    print("5. 如何获取列表的长度？")
    
    print("\n🔑 参考答案:")
    print("1. numbers = list(range(1, 11))")
    print("2. my_list.append(element)")
    print("3. my_list.remove(element) 或 del my_list[index]")
    print("4. my_list.sort() 或 sorted(my_list)")
    print("5. len(my_list)")

def show_agent_structure():
    """显示Agent结构"""
    print("\n🤖 Agent系统架构")
    print("-" * 30)
    
    print("1. 总控Agent (Orchestrator)")
    print("   - 职责: 协调学习流程，制定学习计划")
    print("   - 工具: 知识库搜索、进度保存")
    
    print("\n2. 教学Agent (Tutor)")
    print("   - 职责: 知识点讲解，答疑解惑")
    print("   - 工具: 知识库搜索")
    
    print("\n3. 出题Agent (Question Generator)")
    print("   - 职责: 设计练习题")
    print("   - 工具: 题目生成")
    
    print("\n4. 测验Agent (Evaluator)")
    print("   - 职责: 评估学习效果")
    print("   - 工具: 答案评估")
    
    print("\n5. 记忆Agent (Memory Manager)")
    print("   - 职责: 管理学习历史")
    print("   - 工具: 进度保存")

def main():
    """主函数"""
    print("=" * 50)
    print("AI School - 多Agent学习辅导系统")
    print(f"模型: {os.getenv('DEEPSEEK_MODEL', 'deepseek/deepseek-chat')}")
    print("=" * 50)
    
    # 检查模型配置
    print("🔍 检查模型配置...")
    config_status = LLMConfig.check_config()
    print(f"状态: {config_status['message']}")
    
    if config_status['status'] == 'error':
        print("\n⚠️  注意: 模型配置有问题")
        print("将使用演示模式（模拟输出）")
        print("要使用真实模型，请设置API密钥")
    
    while True:
        print("\n请选择演示项目:")
        print("1. 完整学习会话流程")
        print("2. 快速教学模式")
        print("3. 练习题生成")
        print("4. 查看Agent架构")
        print("5. 退出")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "1":
            demo_learning_session()
        elif choice == "2":
            demo_quick_teach()
        elif choice == "3":
            demo_practice_generation()
        elif choice == "4":
            show_agent_structure()
        elif choice == "5":
            print("\n👋 感谢使用AI School演示系统!")
            print("要实际运行，请:")
            print("1. 设置OPENAI_API_KEY环境变量")
            print("2. 运行: python main.py")
            break
        else:
            print("❌ 无效选择，请重新输入")
        
        input("\n按Enter键继续...")

if __name__ == "__main__":
    main()