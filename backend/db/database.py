"""
数据库连接和初始化
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from db.models import Base

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/aischool"
)

# Docker 内连接使用 db 主机名
if "localhost" in DATABASE_URL:
    import os
    if os.getenv("RUNNING_IN_DOCKER"):
        DATABASE_URL = DATABASE_URL.replace("localhost", "db")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,          # 自动重连
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """创建所有表（幂等）"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI 依赖注入：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
