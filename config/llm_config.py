"""
LLM配置管理器
支持多种模型提供商：DeepSeek, OpenAI, 本地模型
"""

import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 尝试导入 crewAI LLM 包装器
try:
    from crewai import LLM as CrewAI_LLM
    _HAS_CREWAI_LLM = True
except ImportError:
    _HAS_CREWAI_LLM = False

class LLMConfig:
    """LLM配置管理器"""
    
    @staticmethod
    def get_provider() -> str:
        """获取配置的LLM提供商"""
        return os.getenv("LLM_PROVIDER", "deepseek").lower()
    
    @staticmethod
    def get_deepseek_config() -> List[Dict[str, Any]]:
        """获取DeepSeek配置"""
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("未设置DEEPSEEK_API_KEY或OPENAI_API_KEY")
        
        return [{
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "api_key": api_key,
            "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        }]
    
    @staticmethod
    def get_openai_config() -> List[Dict[str, Any]]:
        """获取OpenAI配置"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("未设置OPENAI_API_KEY")
        
        return [{
            "model": os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            "api_key": api_key
        }]
    
    @staticmethod
    def get_local_config() -> List[Dict[str, Any]]:
        """获取本地模型配置（Ollama等）"""
        endpoint = os.getenv("LOCAL_MODEL_ENDPOINT", "http://localhost:11434")
        model_name = os.getenv("LOCAL_MODEL_NAME", "llama3.1")
        
        return [{
            "model": model_name,
            "api_key": "ollama",  # Ollama不需要API密钥
            "base_url": endpoint
        }]
    
    @staticmethod
    def get_config() -> List[Dict[str, Any]]:
        """根据配置获取LLM配置"""
        provider = LLMConfig.get_provider()
        
        if provider == "deepseek":
            return LLMConfig.get_deepseek_config()
        elif provider == "openai":
            return LLMConfig.get_openai_config()
        elif provider == "local":
            return LLMConfig.get_local_config()
        else:
            # 默认使用DeepSeek
            try:
                return LLMConfig.get_deepseek_config()
            except ValueError:
                # 如果DeepSeek配置失败，尝试OpenAI
                try:
                    return LLMConfig.get_openai_config()
                except ValueError:
                    # 最后尝试本地模型
                    return LLMConfig.get_local_config()
    
    @staticmethod
    def get_agent_llm_config() -> Dict[str, Any]:
        """获取Agent的LLM配置（兼容旧版，保留备用）"""
        return {
            "config_list": LLMConfig.get_config(),
            "temperature": 0.7,
            "timeout": 120,
            "max_tokens": 2000
        }

    @staticmethod
    def get_llm():
        """获取crewAI兼容的LLM对象（适用于crewAI 0.28+）"""
        cfg = LLMConfig.get_config()[0]
        kwargs = {
            "model": cfg["model"],
            "api_key": cfg["api_key"],
            "temperature": 0.7,
            "max_tokens": 2000,
        }
        if "base_url" in cfg:
            kwargs["base_url"] = cfg["base_url"]

        if _HAS_CREWAI_LLM:
            return CrewAI_LLM(**kwargs)
        else:
            # 降级：返回模型字符串，让crewAI自行处理
            return cfg["model"]

    @staticmethod
    def check_config() -> Dict[str, Any]:
        """检查配置状态"""
        provider = LLMConfig.get_provider()
        
        try:
            config = LLMConfig.get_config()
            return {
                "status": "ready",
                "provider": provider,
                "model": config[0]["model"],
                "base_url": config[0].get("base_url", "default"),
                "message": f"✅ {provider.upper()} 配置正常"
            }
        except Exception as e:
            return {
                "status": "error",
                "provider": provider,
                "error": str(e),
                "message": f"❌ {provider.upper()} 配置错误: {e}"
            }