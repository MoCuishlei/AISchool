"""
存储层：封装所有数据库读写操作
"""
from datetime import datetime
from typing import List, Dict, Optional
from core.database import get_session, Student, LearningOutline, OutlineItem, ChatHistory


# ── Student ──────────────────────────────────────

def get_or_create_student(name: str) -> Student:
    db = get_session()
    try:
        student = db.query(Student).filter(Student.name == name).first()
        if not student:
            student = Student(name=name)
            db.add(student)
            db.commit()
            db.refresh(student)
        return student
    finally:
        db.close()


def get_student(name: str) -> Optional[Student]:
    db = get_session()
    try:
        return db.query(Student).filter(Student.name == name).first()
    finally:
        db.close()


# ── Outline ──────────────────────────────────────

def save_outline(student_id: int, topic: str, level: str,
                 items: List[Dict]) -> LearningOutline:
    """
    items 格式：[{"title": str, "description": str, "color": "red"|"yellow"|"green"}]
    若同一 student + topic 已存在大纲则覆盖
    """
    db = get_session()
    try:
        # 删除旧大纲（如果有）
        old = (db.query(LearningOutline)
               .filter(LearningOutline.student_id == student_id,
                       LearningOutline.topic == topic)
               .first())
        if old:
            db.delete(old)
            db.commit()

        outline = LearningOutline(student_id=student_id, topic=topic, level=level)
        db.add(outline)
        db.flush()

        for i, item in enumerate(items):
            db.add(OutlineItem(
                outline_id=outline.id,
                title=item["title"],
                description=item.get("description", ""),
                color=item.get("color", "red"),
                sort_order=i,
            ))

        db.commit()
        db.refresh(outline)
        return outline
    finally:
        db.close()


def get_outline(student_id: int, topic: str) -> Optional[LearningOutline]:
    db = get_session()
    try:
        return (db.query(LearningOutline)
                .filter(LearningOutline.student_id == student_id,
                        LearningOutline.topic == topic)
                .first())
    finally:
        db.close()


def update_item_color(item_id: int, color: str):
    """color: 'red' | 'yellow' | 'green'"""
    db = get_session()
    try:
        item = db.query(OutlineItem).filter(OutlineItem.id == item_id).first()
        if item:
            item.color = color
            item.updated_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


def get_outline_items(outline_id: int) -> List[OutlineItem]:
    db = get_session()
    try:
        return (db.query(OutlineItem)
                .filter(OutlineItem.outline_id == outline_id)
                .order_by(OutlineItem.sort_order)
                .all())
    finally:
        db.close()


# ── Chat History ──────────────────────────────────

def save_chat(student_id: int, topic: str, role: str, content: str):
    db = get_session()
    try:
        db.add(ChatHistory(
            student_id=student_id,
            topic=topic,
            role=role,
            content=content,
        ))
        db.commit()
    finally:
        db.close()


def get_recent_chats(student_id: int, topic: str, limit: int = 10) -> List[ChatHistory]:
    db = get_session()
    try:
        return (db.query(ChatHistory)
                .filter(ChatHistory.student_id == student_id,
                        ChatHistory.topic == topic)
                .order_by(ChatHistory.created_at.desc())
                .limit(limit)
                .all())[::-1]
    finally:
        db.close()
