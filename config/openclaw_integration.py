"""
OpenClaw集成配置
自动使用当前OpenClaw会话的模型和API配置
"""

import os
import sys
from typing import Dict, Any

def detect_openclaw_config() -> Dict[str, Any]:
    """
    检测OpenClaw环境配置
    返回可用于AI School的配置
    """
    config = {
        "detected": False,
        "model": None,
        "provider": None,
        "api_key": None,
        "base_url": None
    }
    
    # 检查OpenClaw环境变量
    openclaw_model = os.getenv("OPENCLAW_MODEL")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if openclaw_model:
        config["detected"] = True
        config["model"] = openclaw_model
        
        # 根据模型名称判断提供商
        model_lower = openclaw_model.lower()
        
        if "deepseek" in model_lower:
            config["provider"] = "deepseek"
            config["base_url"] = "https://api.deepseek.com/v1"
            
            # DeepSeek模型名称处理
            if "/" in openclaw_model:
                # 格式如 "deepseek/deepseek-chat"
                config["model"] = openclaw_model.split("/")[-1]
            else:
                config["model"] = openclaw_model
                
        elif "gpt" in model_lower:
            config["provider"] = "openai"
            config["base_url"] = "https://api.openai.com/v1"
            
        elif "claude" in model_lower:
            config["provider"] = "anthropic"
            config["base_url"] = "https://api.anthropic.com/v1"
            
        elif "llama" in model_lower or "qwen" in model_lower:
            config["provider"] = "local"
            config["base_url"] = os.getenv("LOCAL_MODEL_ENDPOINT", "http://localhost:11434")
    
    # 使用OpenClaw的API密钥
    if openai_api_key and openai_api_key != "your_openai_api_key_here":
        config["api_key"] = openai_api_key
    
    return config

def apply_openclaw_config():
    """
    应用OpenClaw配置到环境变量
    返回配置状态
    """
    config = detect_openclaw_config()
    
    if not config["detected"]:
        return {
            "success": False,
            "message": "未检测到OpenClaw配置",
            "config": config
        }
    
    # 设置环境变量
    if config["provider"]:
        os.environ["LLM_PROVIDER"] = config["provider"]
    
    if config["model"]:
        if config["provider"] == "deepseek":
            os.environ["DEEPSEEK_MODEL"] = config["model"]
        elif config["provider"] == "openai":
            os.environ["OPENAI_MODEL"] = config["model"]
    
    if config["api_key"]:
        # 设置对应提供商的API密钥
        if config["provider"] == "deepseek":
            os.environ["DEEPSEEK_API_KEY"] = config["api_key"]
        elif config["provider"] == "openai":
            os.environ["OPENAI_API_KEY"] = config["api_key"]
        elif config["provider"] == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = config["api_key"]
    
    if config["base_url"]:
        if config["provider"] == "deepseek":
            os.environ["DEEPSEEK_BASE_URL"] = config["base_url"]
        elif config["provider"] == "openai":
            os.environ["OPENAI_BASE_URL"] = config["base_url"]
    
    return {
        "success": True,
        "message": f"已应用OpenClaw配置: {config['provider']} - {config['model']}",
        "config": config
    }

def get_openclaw_agent_config() -> Dict[str, Any]:
    """
    获取基于OpenClaw配置的Agent LLM配置
    """
    config = detect_openclaw_config()
    
    if not config["detected"] or not config["api_key"]:
        # 返回默认配置
        return {
            "config_list": [{
                "model": "deepseek-chat",
                "api_key": "",
                "base_url": "https://api.deepseek.com/v1"
            }]
        }
    
    # 返回OpenClaw检测到的配置
    return {
        "config_list": [{
            "model": config["model"],
            "api_key": config["api_key"],
            "base_url": config["base_url"]
        }],
        "temperature": 0.7,
        "timeout": 120,
        "max_tokens": 2000
    }

def test_openclaw_integration():
    """测试OpenClaw集成"""
    print("测试OpenClaw集成...")
    
    config = detect_openclaw_config()
    print(f"检测到配置: {config['detected']}")
    
    if config["detected"]:
        print(f"模型: {config['model']}")
        print(f"提供商: {config['provider']}")
        print(f"API密钥: {'已设置' if config['api_key'] else '未设置'}")
        print(f"Base URL: {config['base_url']}")
        
        # 应用配置
        result = apply_openclaw_config()
        print(f"应用结果: {result['message']}")
    else:
        print("未检测到OpenClaw配置")
        print("当前环境变量:")
        for key in ["OPENCLAW_MODEL", "OPENAI_API_KEY", "DEEPSEEK_API_KEY"]:
            value = os.getenv(key)
            if value:
                print(f"  {key}: {value[:20]}..." if len(value) > 20 else f"  {key}: {value}")
    
    return config

if __name__ == "__main__":
    test_openclaw_integration()