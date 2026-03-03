"""
测试OpenClaw集成
"""

import os
import sys

# 手动设置OpenClaw环境变量（模拟）
os.environ["OPENCLAW_MODEL"] = "deepseek/deepseek-chat"
os.environ["OPENAI_API_KEY"] = "sk-test-key-123456"

print("测试OpenClaw集成配置...")
print(f"OPENCLAW_MODEL: {os.getenv('OPENCLAW_MODEL')}")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')[:10]}...")

# 导入配置模块
sys.path.append('.')
from config.openclaw_integration import detect_openclaw_config, apply_openclaw_config

# 测试检测
config = detect_openclaw_config()
print(f"\n检测结果:")
print(f"  检测到: {config['detected']}")
print(f"  模型: {config['model']}")
print(f"  提供商: {config['provider']}")
print(f"  API密钥: {'已设置' if config['api_key'] else '未设置'}")
print(f"  Base URL: {config['base_url']}")

# 测试应用
print(f"\n应用配置...")
result = apply_openclaw_config()
print(f"  结果: {result['message']}")

# 检查环境变量
print(f"\n环境变量检查:")
print(f"  LLM_PROVIDER: {os.getenv('LLM_PROVIDER')}")
print(f"  DEEPSEEK_MODEL: {os.getenv('DEEPSEEK_MODEL')}")
print(f"  DEEPSEEK_API_KEY: {os.getenv('DEEPSEEK_API_KEY')[:10]}...")
print(f"  DEEPSEEK_BASE_URL: {os.getenv('DEEPSEEK_BASE_URL')}")

print("\n✅ 测试完成")