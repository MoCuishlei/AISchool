"""
AI School - 项目启动和配置脚本
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """打印项目标题"""
    print("🎓" * 30)
    print("🎓        AI School - 多Agent学习辅导系统        🎓")
    print("🎓" * 30)
    print()

def check_environment():
    """检查环境"""
    print("🔍 检查环境...")
    
    # 检查Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"❌ Python版本过低: {sys.version}")
        print("   需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本: {sys.version}")
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"📁 当前目录: {current_dir}")
    
    # 检查关键文件
    required_files = ["requirements.txt", "main.py", "config/agents.py"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少文件: {', '.join(missing_files)}")
        return False
    
    print("✅ 项目文件完整")
    
    # 检查OpenClaw集成
    try:
        from config.openclaw_integration import detect_openclaw_config
        config = detect_openclaw_config()
        if config["detected"]:
            print(f"✅ 检测到OpenClaw配置: {config['model']}")
        else:
            print("ℹ️  未检测到OpenClaw配置，将使用默认配置")
    except ImportError:
        print("ℹ️  OpenClaw集成模块未找到")
    
    return True

def setup_environment():
    """设置环境"""
    print("\n⚙️  设置环境...")
    
    # 创建虚拟环境（可选）
    create_venv = input("是否创建Python虚拟环境？ (y/n): ").lower().strip()
    if create_venv == 'y':
        venv_name = input("虚拟环境名称 (默认: venv): ").strip() or "venv"
        
        if platform.system() == "Windows":
            venv_cmd = f"python -m venv {venv_name}"
        else:
            venv_cmd = f"python3 -m venv {venv_name}"
        
        print(f"创建虚拟环境: {venv_cmd}")
        result = os.system(venv_cmd)
        
        if result == 0:
            print(f"✅ 虚拟环境创建成功: {venv_name}")
            
            # 激活提示
            if platform.system() == "Windows":
                print(f"激活命令: {venv_name}\\Scripts\\activate")
            else:
                print(f"激活命令: source {venv_name}/bin/activate")
        else:
            print("❌ 虚拟环境创建失败")
    
    # 安装依赖
    install_deps = input("\n是否安装Python依赖？ (y/n): ").lower().strip()
    if install_deps == 'y':
        print("安装依赖...")
        
        if platform.system() == "Windows":
            pip_cmd = "pip install -r requirements.txt"
        else:
            pip_cmd = "pip3 install -r requirements.txt"
        
        print(f"执行: {pip_cmd}")
        result = os.system(pip_cmd)
        
        if result == 0:
            print("✅ 依赖安装成功")
        else:
            print("❌ 依赖安装失败")
    
    # 设置环境变量
    setup_env = input("\n是否设置环境变量文件？ (y/n): ").lower().strip()
    if setup_env == 'y':
        if not os.path.exists(".env"):
            if os.path.exists(".env.example"):
                import shutil
                shutil.copy(".env.example", ".env")
                print("✅ 已创建 .env 文件")
                print("⚠️  请编辑 .env 文件设置你的API密钥")
            else:
                print("❌ 找不到 .env.example 文件")
        else:
            print("✅ .env 文件已存在")
    
    return True

def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 50)
    print("📋 主菜单")
    print("=" * 50)
    
    options = [
        ("1", "运行演示模式", "run_demo"),
        ("2", "运行完整系统", "run_full"),
        ("3", "启动Web API", "run_api"),
        ("4", "测试Agent功能", "test_agents"),
        ("5", "运行使用示例", "run_examples"),
        ("6", "Docker启动", "run_docker"),
        ("7", "查看项目结构", "show_structure"),
        ("8", "退出", "exit")
    ]
    
    for num, name, _ in options:
        print(f"{num}. {name}")
    
    return options

def run_demo():
    """运行演示模式"""
    print("\n🎭 启动演示模式...")
    if os.path.exists("run_local.py"):
        os.system("python run_local.py")
    else:
        print("❌ 找不到 run_local.py")

def run_full():
    """运行完整系统"""
    print("\n🚀 启动完整系统...")
    if os.path.exists("main.py"):
        os.system("python main.py")
    else:
        print("❌ 找不到 main.py")

def run_api():
    """启动Web API"""
    print("\n🌐 启动Web API...")
    print("API将在 http://localhost:8000 运行")
    print("文档: http://localhost:8000/docs")
    print("按 Ctrl+C 停止")
    
    try:
        os.system("python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
    except KeyboardInterrupt:
        print("\nAPI服务已停止")

def test_agents():
    """测试Agent功能"""
    print("\n🧪 测试Agent功能...")
    if os.path.exists("test_agents.py"):
        os.system("python test_agents.py")
    else:
        print("❌ 找不到 test_agents.py")

def run_examples():
    """运行使用示例"""
    print("\n📚 运行使用示例...")
    
    examples = [
        ("基础使用示例", "examples/basic_usage.py"),
        ("高级功能示例", "examples/advanced_features.py")
    ]
    
    print("请选择示例:")
    for i, (name, path) in enumerate(examples, 1):
        if os.path.exists(path):
            print(f"{i}. {name}")
        else:
            print(f"{i}. {name} (文件不存在)")
    
    print(f"{len(examples) + 1}. 返回主菜单")
    
    try:
        choice = int(input("\n请选择: ").strip())
    except ValueError:
        print("❌ 请输入数字")
        return
    
    if 1 <= choice <= len(examples):
        name, path = examples[choice - 1]
        if os.path.exists(path):
            print(f"\n运行: {name}")
            os.system(f"python {path}")
        else:
            print(f"❌ 找不到文件: {path}")
    elif choice == len(examples) + 1:
        return
    else:
        print("❌ 无效选择")

def run_docker():
    """Docker启动"""
    print("\n🐳 Docker启动...")
    
    # 检查Docker
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker已安装")
    except:
        print("❌ Docker未安装或不可用")
        print("请先安装Docker: https://docs.docker.com/get-docker/")
        return
    
    # 检查docker-compose
    try:
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        print("✅ docker-compose已安装")
    except:
        print("❌ docker-compose未安装")
        print("请先安装docker-compose: https://docs.docker.com/compose/install/")
        return
    
    print("\nDocker选项:")
    print("1. 构建并启动所有服务")
    print("2. 仅启动应用容器")
    print("3. 查看服务状态")
    print("4. 停止所有服务")
    print("5. 返回主菜单")
    
    try:
        choice = int(input("\n请选择: ").strip())
    except ValueError:
        print("❌ 请输入数字")
        return
    
    if choice == 1:
        print("构建并启动所有服务...")
        os.system("docker-compose up --build -d")
        print("✅ 服务已启动")
        print("应用: http://localhost:8000")
        print("数据库: localhost:5432")
        print("Redis: localhost:6379")
        
    elif choice == 2:
        print("启动应用容器...")
        os.system("docker build -t aischool .")
        os.system('docker run -p 8000:8000 --env-file .env aischool')
        
    elif choice == 3:
        print("服务状态:")
        os.system("docker-compose ps")
        
    elif choice == 4:
        print("停止所有服务...")
        os.system("docker-compose down")
        print("✅ 服务已停止")
        
    elif choice == 5:
        return
        
    else:
        print("❌ 无效选择")

def show_structure():
    """显示项目结构"""
    print("\n📁 项目结构:")
    print("=" * 50)
    
    structure = """
AISchool/
├── 📄 README.md                    # 项目说明
├── 📄 requirements.txt             # Python依赖
├── 📄 .env.example                 # 环境变量模板
├── 📄 Dockerfile                   # Docker构建
├── 📄 docker-compose.yml           # Docker Compose
├── 📄 main.py                      # 主程序入口
├── 📄 run_local.py                 # 演示模式
├── 📄 test_agents.py               # Agent测试
│
├── 📂 config/                     # 配置目录
│   ├── 📄 agents.py              # Agent定义
│   └── 📄 tasks.py               # 任务定义
│
├── 📂 core/                       # 核心逻辑
│   └── 📄 learning_crew.py       # 多Agent系统
│
├── 📂 api/                        # Web API
│   └── 📄 main.py                # FastAPI应用
│
├── 📂 examples/                   # 示例代码
│   ├── 📄 basic_usage.py         # 基础示例
│   └── 📄 advanced_features.py   # 高级示例
│
├── 📂 scripts/                    # 脚本目录
│   ├── 📄 run_demo.sh            # Linux/Mac脚本
│   └── 📄 run_demo.bat           # Windows脚本
│
└── 📄 DEPLOYMENT.md              # 部署指南
    """
    
    print(structure)
    
    print("\n🔧 核心文件说明:")
    print("  config/agents.py    - 定义5个核心Agent")
    print("  config/tasks.py     - 定义学习任务")
    print("  core/learning_crew.py - Agent协作系统")
    print("  main.py             - 命令行交互入口")
    print("  api/main.py         - Web API入口")

def main():
    """主函数"""
    print_header()
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请修复问题后重试")
        return
    
    # 设置环境
    setup = input("\n是否进行环境设置？ (y/n): ").lower().strip()
    if setup == 'y':
        if not setup_environment():
            print("❌ 环境设置失败")
            return
    
    # 主循环
    while True:
        options = show_menu()
        
        try:
            choice = input("\n请选择 (1-8): ").strip()
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        
        if choice == "8":
            print("👋 再见!")
            break
        
        # 执行对应功能
        action_map = {num: action for num, _, action in options}
        if choice in action_map:
            action = action_map[choice]
            
            if action == "exit":
                print("👋 再见!")
                break
            elif action == "show_structure":
                show_structure()
            else:
                # 调用对应的函数
                globals()[action]()
        else:
            print("❌ 无效选择")
        
        input("\n按Enter键返回主菜单...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()