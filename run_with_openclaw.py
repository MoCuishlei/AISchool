"""
使用OpenClaw配置运行AI School
自动检测并使用当前OpenClaw会话的模型和API配置
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

print("🚀 AI School - OpenClaw集成版")
print("=" * 50)

# 导入OpenClaw集成模块
try:
    from config.openclaw_integration import apply_openclaw_config, test_openclaw_integration
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在AISchool目录中运行")
    sys.exit(1)

# 测试OpenClaw集成
print("🔍 检测OpenClaw配置...")
config_result = test_openclaw_integration()

if not config_result["detected"]:
    print("\n⚠️  未检测到OpenClaw配置")
    print("可能的原因:")
    print("1. 未在OpenClaw环境中运行")
    print("2. 环境变量未正确设置")
    print("3. 当前目录不是AISchool项目根目录")
    
    use_default = input("\n是否使用默认配置继续？ (y/n): ").lower().strip()
    if use_default != 'y':
        print("👋 退出")
        sys.exit(0)
    
    # 设置默认配置
    os.environ["LLM_PROVIDER"] = "deepseek"
    os.environ["DEEPSEEK_MODEL"] = "deepseek-chat"
    print("✅ 使用默认DeepSeek配置")

# 应用OpenClaw配置
print("\n⚙️  应用配置...")
apply_result = apply_openclaw_config()
print(f"✅ {apply_result['message']}")

# 检查模型配置
print("\n🔧 检查模型配置...")
try:
    from config.llm_config import LLMConfig
    config_status = LLMConfig.check_config()
    print(f"状态: {config_status['message']}")
    
    if config_status['status'] == 'error':
        print(f"❌ 配置错误: {config_status['error']}")
        print("\n建议:")
        print("1. 检查API密钥设置")
        print("2. 检查网络连接")
        print("3. 运行演示模式学习系统功能")
        
        run_demo = input("\n是否运行演示模式？ (y/n): ").lower().strip()
        if run_demo == 'y':
            print("\n🎭 启动演示模式...")
            import run_local
            run_local.main()
            sys.exit(0)
        else:
            sys.exit(1)
            
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    sys.exit(1)

# 选择运行模式
print("\n" + "=" * 50)
print("📋 运行模式选择")
print("=" * 50)

print("1. 完整学习会话 (命令行交互)")
print("2. 快速教学模式")
print("3. 练习题生成模式")
print("4. Web API服务")
print("5. 测试Agent功能")
print("6. 运行示例代码")
print("7. 退出")

try:
    choice = input("\n请选择模式 (1-7): ").strip()
except KeyboardInterrupt:
    print("\n👋 退出")
    sys.exit(0)

if choice == "1":
    # 完整学习会话
    print("\n🚀 启动完整学习会话...")
    import main
    main.main()
    
elif choice == "2":
    # 快速教学
    print("\n📚 快速教学模式")
    from core.learning_crew import LearningCrew
    
    topic = input("请输入教学主题 (例如: Python函数): ").strip()
    if not topic:
        topic = "Python函数定义"
    
    crew = LearningCrew(student_id="openclaw_student")
    result = crew.quick_teach(topic)
    
    print(f"\n📖 教学内容:")
    print("=" * 40)
    print(result)
    
elif choice == "3":
    # 练习题生成
    print("\n📝 练习题生成模式")
    from core.learning_crew import LearningCrew
    
    topic = input("请输入主题: ").strip()
    if not topic:
        topic = "Python列表操作"
    
    difficulty = input("难度 (easy/medium/hard, 默认: medium): ").strip() or "medium"
    count = input("题目数量 (默认: 5): ").strip()
    count = int(count) if count.isdigit() else 5
    
    crew = LearningCrew(student_id="openclaw_student")
    result = crew.generate_practice(topic, difficulty, count)
    
    print(f"\n📋 生成的练习题:")
    print("=" * 40)
    print(result)
    
elif choice == "4":
    # Web API
    print("\n🌐 启动Web API服务...")
    print("API将在 http://localhost:8000 运行")
    print("文档: http://localhost:8000/docs")
    print("按 Ctrl+C 停止")
    
    try:
        import uvicorn
        uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\nAPI服务已停止")
    except ImportError:
        print("❌ 未安装uvicorn，请运行: pip install uvicorn")
        
elif choice == "5":
    # 测试Agent
    print("\n🧪 测试Agent功能...")
    import test_agents
    test_agents.test_agent_creation()
    test_agents.test_tools()
    test_agents.test_simple_interaction()
    
elif choice == "6":
    # 运行示例
    print("\n📚 运行示例代码")
    print("1. 基础使用示例")
    print("2. 高级功能示例")
    print("3. 返回")
    
    example_choice = input("\n请选择: ").strip()
    
    if example_choice == "1":
        import examples.basic_usage
        examples.basic_usage.main()
    elif example_choice == "2":
        import examples.advanced_features
        examples.advanced_features.main()
    else:
        print("返回主菜单")
        
elif choice == "7":
    print("👋 再见!")
    sys.exit(0)
    
else:
    print("❌ 无效选择")
    sys.exit(1)

print("\n" + "=" * 50)
print("🎉 AI School 运行完成!")
print("\n配置信息:")
print(f"模型: {config_status.get('model', '未知')}")
print(f"提供商: {config_status.get('provider', '未知')}")
print(f"状态: {config_status.get('message', '未知')}")

print("\n💡 提示:")
print("1. 要修改配置，编辑 .env 文件")
print("2. 要添加新功能，修改 config/ 目录下的文件")
print("3. 要扩展系统，参考 examples/ 目录")
print("4. 要部署系统，参考 DEPLOYMENT.md")

print("\n🚀 再次运行: python run_with_openclaw.py")