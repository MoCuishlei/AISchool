"""
LLM 配置工具 - 统一管理 API 地址、Key 和模型名称
优先读取数据库配置，若无则回退至 .env 环境变量
"""

import os
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db import crud

def get_llm_config(db: Session = None):
    """
    获取 LLM 配置。如果未提供 db，则内部开启临时会话读取。
    """
    local_db = db
    if not local_db:
        local_db = SessionLocal()
    
    try:
        base_url = crud.get_config(local_db, "llm_base_url") or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        api_key = crud.get_config(local_db, "llm_api_key") or os.getenv("DEEPSEEK_API_KEY")
        model_name = crud.get_config(local_db, "llm_model_name") or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        return {
            "base_url": base_url,
            "api_key": api_key,
            "model": model_name
        }
    finally:
        if not db:
            local_db.close()

def get_openai_client(db: Session = None):
    """获取配置好的 OpenAI 客户端"""
    from openai import OpenAI
    cfg = get_llm_config(db)
    return OpenAI(
        api_key=cfg["api_key"],
        base_url=cfg["base_url"]
    ), cfg["model"]
