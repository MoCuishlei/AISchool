"""
数据库连接与模型定义
"""
import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Text,
    DateTime, ForeignKey, Enum
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/aischool"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# ── 数据模型 ──────────────────────────────────────

class Student(Base):
    __tablename__ = "students"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    outlines  = relationship("LearningOutline", back_populates="student", cascade="all, delete")
    histories = relationship("ChatHistory",     back_populates="student", cascade="all, delete")


class LearningOutline(Base):
    __tablename__ = "learning_outlines"
    id         = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    topic      = Column(String(200), nullable=False)
    level      = Column(String(20), default="beginner")
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="outlines")
    items   = relationship("OutlineItem", back_populates="outline",
                           cascade="all, delete", order_by="OutlineItem.sort_order")


class OutlineItem(Base):
    __tablename__ = "outline_items"
    id          = Column(Integer, primary_key=True, index=True)
    outline_id  = Column(Integer, ForeignKey("learning_outlines.id"), nullable=False)
    title       = Column(String(200), nullable=False)
    description = Column(Text, default="")
    color       = Column(Enum("red", "yellow", "green", name="color_enum"), default="red")
    sort_order  = Column(Integer, default=0)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    outline = relationship("LearningOutline", back_populates="items")


class ChatHistory(Base):
    __tablename__ = "chat_histories"
    id         = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    topic      = Column(String(200), nullable=False)
    role       = Column(String(10), nullable=False)   # "user" | "ai"
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="histories")


def init_db():
    """创建所有表（幂等，已存在不影响）"""
    Base.metadata.create_all(bind=engine)


def get_session():
    """获取数据库 Session"""
    return SessionLocal()
