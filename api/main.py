"""
FastAPI Web API — AI School 完整教学流程
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any
import uvicorn, os, base64
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from db.database import get_db, create_tables
from db import crud
from fastapi.responses import StreamingResponse
from core.direct_llm import direct_teach, direct_practice, generate_syllabus
from core.assessment_llm import generate_assessment_questions, evaluate_assessment, generate_assessment_questions_stream
from core.classroom_llm import start_lesson, ask_question, generate_mini_quiz, evaluate_quiz, generate_mini_quiz_stream
from core.exam_llm import generate_exam, evaluate_exam, generate_exam_stream

load_dotenv()

app = FastAPI(title="AI School API", description="完整 AI 课堂系统", version="2.0.0")

# CORS — 允许所有本地开发端口
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", "http://localhost:3001", "http://localhost:3002",
        "http://localhost:5173", "http://localhost:5174",
        "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    """启动时自动建表"""
    try:
        create_tables()
        print("✅ 数据库表已创建/确认")
    except Exception as e:
        print(f"⚠️ 数据库初始化警告: {e}")


# ─── 健康检查 ─────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0", "service": "AI School"}


# ════════════════════════════════════════════════════════
# 会话管理
# ════════════════════════════════════════════════════════

class CreateSessionRequest(BaseModel):
    subject: str
    student_name: str = "学习者"


@app.post("/session/create")
def create_session_api(req: CreateSessionRequest, db: Session = Depends(get_db)):
    student = crud.get_or_create_student(db, req.student_name)
    session = crud.create_session(db, student.id, req.subject)
    return {
        "session_id": session.id,
        "student_id": student.id,
        "subject": session.subject,
        "status": session.status,
    }


@app.get("/session/{session_id}")
def get_session_api(session_id: int, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    items = crud.get_syllabus_items(db, session_id)
    unlock = crud.get_exam_unlock_status(db, session_id)
    return {
        "session_id": session.id,
        "subject": session.subject,
        "status": session.status,
        "progress_pct": session.progress_pct,
        "proficiency_data": session.proficiency_data,
        "syllabus_items": [
            {"id": i.id, "section_id": i.section_id, "section_title": i.section_title,
             "item_id": i.item_id, "item_title": i.item_title,
             "item_description": i.item_description, "status": i.status,
             "mastery_score": i.mastery_score}
            for i in items
        ],
        "exam_unlock": unlock,
    }


@app.get("/session/student/{student_name}")
def get_student_sessions_api(student_name: str, db: Session = Depends(get_db)):
    student = crud.get_or_create_student(db, student_name)
    sessions = crud.get_student_sessions(db, student.id)
    return {
        "student_id": student.id,
        "sessions": [
            {"session_id": s.id, "subject": s.subject, "status": s.status,
             "progress_pct": s.progress_pct,
             "created_at": s.created_at.isoformat() if s.created_at else None,
             "updated_at": s.updated_at.isoformat() if s.updated_at else None}
            for s in sessions
        ]
    }


# ════════════════════════════════════════════════════════
# 入学测评
# ════════════════════════════════════════════════════════

@app.post("/assessment/start/{session_id}")
def start_assessment(session_id: int, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    questions = generate_assessment_questions(session.subject, count=10)
    if not questions:
        raise HTTPException(500, "生成题目失败，请重试")
    record = crud.create_assessment(db, session_id, questions)
    return {
        "assessment_id": record.id,
        "session_id": session_id,
        "subject": session.subject,
        "questions": questions,
        "total": len(questions),
    }

@app.post("/assessment/start_stream/{session_id}")
def start_assessment_stream(session_id: int, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    
    subject = session.subject  # 提前取出，避免在生成器内依赖外部 Session

    def event_stream():
        # 生成器内部自己创建独立的 DB Session，与路由函数的 Depends 完全解耦
        from db.database import SessionLocal
        stream_db = SessionLocal()
        try:
            for event in generate_assessment_questions_stream(subject, count=10):
                if event["status"] == "done":
                    questions = event.get("questions", [])
                    if questions:
                        record = crud.create_assessment(stream_db, session_id, questions)
                        event["assessment_id"] = record.id
                        event["total"] = len(questions)
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
        finally:
            stream_db.close()
            
    return StreamingResponse(event_stream(), media_type="text/event-stream")


class SubmitAssessmentRequest(BaseModel):
    answers: List[str]      # 与 questions 等长，每题一个答案字符串


@app.post("/assessment/submit/{session_id}")
def submit_assessment(session_id: int, req: SubmitAssessmentRequest, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    record = db.query(crud.AssessmentRecord).filter_by(session_id=session_id).first()
    if not record:
        raise HTTPException(404, "测评记录不存在，请先调用 /assessment/start")

    proficiency, report = evaluate_assessment(session.subject, record.questions, req.answers)
    record = crud.complete_assessment(db, session_id, req.answers, proficiency, report)

    return {
        "session_id": session_id,
        "proficiency": proficiency,
        "report": report,
    }


# ════════════════════════════════════════════════════════
# 大纲（持久化）
# ════════════════════════════════════════════════════════

class GenerateSyllabusRequest(BaseModel):
    topic: str


@app.post("/syllabus/generate/{session_id}")
def generate_syllabus_for_session(session_id: int, req: GenerateSyllabusRequest,
                                   db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    data = generate_syllabus(req.topic or session.subject)
    if not data:
        raise HTTPException(500, "大纲生成失败")
    crud.bulk_create_syllabus(db, session_id, data)
    crud.update_session_status(db, session_id, "learning")
    items = crud.get_syllabus_items(db, session_id)
    return {
        "session_id": session_id,
        "syllabus": data,
        "items_created": len(items),
    }


class UpdateItemStatusRequest(BaseModel):
    status: str             # none/learning/done
    mastery_score: Optional[float] = None


@app.put("/syllabus/item/{item_db_id}")
def update_item_status(item_db_id: int, req: UpdateItemStatusRequest,
                       db: Session = Depends(get_db)):
    item = db.query(crud.SyllabusItem).filter(crud.SyllabusItem.id == item_db_id).first()
    if not item:
        raise HTTPException(404, "条目不存在")
    updated = crud.update_item_status(db, item.session_id, item_db_id, req.status, req.mastery_score)
    progress = crud.update_session_progress(db, item.session_id)
    return {"item_id": item_db_id, "status": updated.status, "progress_pct": progress}


# ════════════════════════════════════════════════════════
# 课堂
# ════════════════════════════════════════════════════════

class StartLessonRequest(BaseModel):
    item_db_id: int         # SyllabusItem.id
    reteach: bool = False   # 是否重新上课（小测验未过）


@app.post("/classroom/start/{session_id}")
def classroom_start(session_id: int, req: StartLessonRequest, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    item = db.query(crud.SyllabusItem).filter(
        crud.SyllabusItem.id == req.item_db_id,
        crud.SyllabusItem.session_id == session_id
    ).first()
    if not item:
        raise HTTPException(404, "知识点不存在")

    # 获取或创建课堂对话
    convo = db.query(crud.ClassroomConversation).filter_by(
        session_id=session_id, item_id=item.item_id
    ).first()

    attempt = 1
    if convo and req.reteach:
        crud.increment_attempt(db, convo.id)
        convo = db.query(crud.ClassroomConversation).filter_by(id=convo.id).first()
        attempt = convo.attempt_count
    elif convo and not req.reteach:
        # 断线续学：返回已有内容
        return {
            "conversation_id": convo.id,
            "item_id": item.item_id,
            "item_title": item.item_title,
            "lesson_content": convo.lesson_content,
            "history": convo.messages,
            "attempt": convo.attempt_count,
            "resumed": True,
        }

    # 全新上课
    lesson_content = start_lesson(session.subject, item.item_title, attempt)
    if convo is None:
        convo = crud.get_or_create_conversation(
            db, session_id, item.item_id, item.item_title, lesson_content)
    else:
        convo.lesson_content = lesson_content
        convo.messages = []
        db.commit()

    # 标记知识点为"学习中"
    crud.update_item_status(db, session_id, req.item_db_id, "learning")

    return {
        "conversation_id": convo.id,
        "item_id": item.item_id,
        "item_title": item.item_title,
        "lesson_content": lesson_content,
        "history": [],
        "attempt": attempt,
        "resumed": False,
    }


class AskQuestionRequest(BaseModel):
    conversation_id: int
    question: str


@app.post("/classroom/ask/{session_id}")
def classroom_ask(session_id: int, req: AskQuestionRequest, db: Session = Depends(get_db)):
    convo = db.query(crud.ClassroomConversation).filter(
        crud.ClassroomConversation.id == req.conversation_id,
        crud.ClassroomConversation.session_id == session_id
    ).first()
    if not convo:
        raise HTTPException(404, "课堂对话不存在")
    session = crud.get_session(db, session_id)

    answer = ask_question(
        session.subject, convo.item_title,
        convo.lesson_content,
        convo.messages or [],
        req.question
    )
    crud.append_message(db, convo.id, "user", req.question)
    crud.append_message(db, convo.id, "assistant", answer)
    return {"answer": answer, "conversation_id": convo.id}


class StartQuizRequest(BaseModel):
    conversation_id: int
    item_db_id: int


@app.post("/classroom/start-quiz/{session_id}")
def classroom_start_quiz(session_id: int, req: StartQuizRequest, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    item = db.query(crud.SyllabusItem).filter(
        crud.SyllabusItem.id == req.item_db_id,
        crud.SyllabusItem.session_id == session_id
    ).first()
    if not item:
        raise HTTPException(404, "知识点不存在")

    attempt_number = crud.get_item_quiz_count(db, session_id, item.item_id) + 1
    questions = generate_mini_quiz(session.subject, item.item_title, count=4)
    if not questions:
        raise HTTPException(500, "生成题目失败，请重试")

    record = crud.create_quiz(db, session_id, item.item_id, item.item_title,
                              questions, attempt_number)
    return {
        "quiz_id": record.id,
        "item_id": item.item_id,
        "item_title": item.item_title,
        "questions": questions,
        "attempt_number": attempt_number,
    }

@app.post("/classroom/start-quiz_stream/{session_id}")
def classroom_start_quiz_stream(session_id: int, req: StartQuizRequest, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    item = db.query(crud.SyllabusItem).filter(
        crud.SyllabusItem.id == req.item_db_id,
        crud.SyllabusItem.session_id == session_id
    ).first()
    if not item:
        raise HTTPException(404, "知识点不存在")

    attempt_number = crud.get_item_quiz_count(db, session_id, item.item_id) + 1

    # 提前记录需要的数据，避免在生成器内依赖外部 Session
    subject = session.subject
    item_id = item.item_id
    item_title = item.item_title

    def event_stream():
        from db.database import SessionLocal
        stream_db = SessionLocal()
        try:
            for event in generate_mini_quiz_stream(subject, item_title, count=4):
                if event["status"] == "done":
                    questions = event.get("questions", [])
                    if questions:
                        record = crud.create_quiz(stream_db, session_id, item_id, item_title,
                                                  questions, attempt_number)
                        event["quiz_id"] = record.id
                        event["item_id"] = item_id
                        event["item_title"] = item_title
                        event["attempt_number"] = attempt_number
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
        finally:
            stream_db.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/classroom/submit-quiz/{session_id}")
async def classroom_submit_quiz(
    session_id: int,
    quiz_id: int = Form(...),
    item_db_id: int = Form(...),
    answers: str = Form(...),       # JSON 字符串
    images: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db)
):
    """提交小测验答案（支持文字+图片）"""
    import json as _json
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    quiz = db.query(crud.QuizRecord).filter(crud.QuizRecord.id == quiz_id).first()
    if not quiz:
        raise HTTPException(404, "测验记录不存在")

    answers_list = _json.loads(answers)

    # 处理图片
    images_b64 = []
    for img in images:
        content = await img.read()
        images_b64.append(base64.b64encode(content).decode())

    score, passed, feedback = evaluate_quiz(
        session.subject, quiz.item_title,
        quiz.questions, answers_list, images_b64
    )

    crud.complete_quiz(db, quiz_id, answers_list, score, passed, feedback)

    if passed:
        crud.update_item_status(db, session_id, item_db_id, "done", score)

    return {
        "quiz_id": quiz_id,
        "score": score,
        "passed": passed,
        "feedback": feedback,
        "progress_pct": crud.get_exam_unlock_status(db, session_id)["progress"],
    }


# ════════════════════════════════════════════════════════
# 考试
# ════════════════════════════════════════════════════════

@app.get("/exam/unlock-check/{session_id}")
def exam_unlock_check(session_id: int, db: Session = Depends(get_db)):
    return crud.get_exam_unlock_status(db, session_id)


class GenerateExamRequest(BaseModel):
    exam_type: str      # "midterm" / "final"


@app.post("/exam/generate/{session_id}")
def exam_generate(session_id: int, req: GenerateExamRequest, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    unlock = crud.get_exam_unlock_status(db, session_id)
    if req.exam_type == "midterm" and not unlock["midterm"]:
        raise HTTPException(403, f"期中考试未解锁（当前进度 {unlock['progress']}%，需 ≥50%）")
    if req.exam_type == "final" and not unlock["final"]:
        raise HTTPException(403, f"期末考试未解锁（当前进度 {unlock['progress']}%，需 ≥90%）")

    items = crud.get_syllabus_items(db, session_id)
    if req.exam_type == "midterm":
        covered = [i.item_title for i in items if i.status == "done"]
    else:
        covered = [i.item_title for i in items]

    questions = generate_exam(session.subject, covered, req.exam_type)
    if not questions:
        raise HTTPException(500, "试卷生成失败，请重试")

    record = crud.create_exam(db, session_id, req.exam_type, covered, questions)
    return {
        "exam_id": record.id,
        "exam_type": req.exam_type,
        "subject": session.subject,
        "covered_count": len(covered),
        "questions": questions,
        "total": len(questions),
    }

@app.post("/exam/generate_stream/{session_id}")
def exam_generate_stream(session_id: int, req: GenerateExamRequest, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    unlock = crud.get_exam_unlock_status(db, session_id)
    if req.exam_type == "midterm" and not unlock["midterm"]:
        raise HTTPException(403, f"期中考试未解锁（当前进度 {unlock['progress']}%，需 ≥50%）")
    if req.exam_type == "final" and not unlock["final"]:
        raise HTTPException(403, f"期末考试未解锁（当前进度 {unlock['progress']}%，需 ≥90%）")

    items = crud.get_syllabus_items(db, session_id)
    if req.exam_type == "midterm":
        covered = [i.item_title for i in items if i.status == "done"]
    else:
        covered = [i.item_title for i in items]

    def event_stream():
        for event in generate_exam_stream(session.subject, covered, req.exam_type):
            if event["status"] == "done":
                questions = event.get("questions", [])
                if questions:
                    record = crud.create_exam(db, session_id, req.exam_type, covered, questions)
                    event["exam_id"] = record.id
                    event["exam_type"] = req.exam_type
                    event["subject"] = session.subject
                    event["covered_count"] = len(covered)
                    event["total"] = len(questions)
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/exam/submit/{session_id}")
async def exam_submit(
    session_id: int,
    exam_id: int = Form(...),
    answers: str = Form(...),
    images: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db)
):
    import json as _json
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    exam = db.query(crud.ExamRecord).filter(crud.ExamRecord.id == exam_id).first()
    if not exam:
        raise HTTPException(404, "考试记录不存在")

    answers_list = _json.loads(answers)
    score, report = evaluate_exam(session.subject, exam.exam_type, exam.questions, answers_list)
    crud.complete_exam(db, exam_id, answers_list, score, report)
    return {"exam_id": exam_id, "score": score, "report": report}


# ════════════════════════════════════════════════════════
# 兼容旧接口（快速学习/练习题 直连 LLM）
# ════════════════════════════════════════════════════════

class QuickTeachRequest(BaseModel):
    topic: str
    question: Optional[str] = None


@app.post("/learning/quick-teach")
def quick_teach(req: QuickTeachRequest):
    try:
        content = direct_teach(req.topic, req.question)
        return {"topic": req.topic, "content": content, "type": "quick_teach"}
    except Exception as e:
        raise HTTPException(500, str(e))


class PracticeRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    count: int = 5


@app.post("/learning/practice")
def practice(req: PracticeRequest):
    try:
        result = direct_practice(req.topic, req.difficulty, req.count)
        return {"topic": req.topic, "content": result, "type": "practice"}
    except Exception as e:
        raise HTTPException(500, str(e))


class SyllabusRequest(BaseModel):
    topic: str


@app.post("/learning/syllabus")
def syllabus_standalone(req: SyllabusRequest):
    try:
        data = generate_syllabus(req.topic)
        return {"topic": req.topic, "syllabus": data}
    except Exception as e:
        raise HTTPException(500, str(e))


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)