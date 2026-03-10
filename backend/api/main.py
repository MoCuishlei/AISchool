"""
FastAPI Web API — AI School 完整教学流程
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any
import uvicorn, os, base64, traceback
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import json

from db.database import get_db, create_tables
from db import crud
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from core.direct_llm import direct_teach, direct_practice, generate_syllabus
from core.assessment_llm import generate_assessment_questions, evaluate_assessment, generate_assessment_questions_stream
from core.classroom_llm import start_lesson, ask_question, generate_mini_quiz, evaluate_quiz, generate_mini_quiz_stream
from core.exam_llm import generate_exam, evaluate_exam, generate_exam_stream

load_dotenv()

app = FastAPI(title="AI School API", description="完整 AI 课堂系统", version="2.0.0")

# CORS — 允许所有访问（支持小程序迁移与外部部署）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def api_prefix_middleware(request: Request, call_next):
    # 如果路径以 /api/ 开头，则去掉 /api 前缀以匹配后端路由
    if request.url.path.startswith("/api/"):
        request.scope["path"] = request.url.path[4:]
    return await call_next(request)


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
    
    # 获取未完成的测评记录（如果有）
    assessment_info = None
    record = db.query(crud.AssessmentRecord).filter(crud.AssessmentRecord.session_id == session_id).first()
    if record and not record.completed:
        assessment_info = {
            "id": record.id,
            "has_questions": bool(record.questions),
            "answers_count": len(record.answers) if record.answers else 0
        }

    return {
        "session_id": session.id,
        "subject": session.subject,
        "status": session.status,
        "progress_pct": session.progress_pct,
        "proficiency_data": session.proficiency_data,
        "assessment": assessment_info,
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


@app.delete("/session/{session_id}")
def delete_session_api(session_id: int, db: Session = Depends(get_db)):
    success = crud.delete_session(db, session_id)
    if not success:
        raise HTTPException(404, "会话不存在或已删除")
    return {"status": "success", "session_id": session_id}


# ════════════════════════════════════════════════════════
# 入学测评
# ════════════════════════════════════════════════════════

@app.post("/assessment/start/{session_id}")
def start_assessment(session_id: int, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
        
    # 检查是否存在未完成的测评
    existing_record = db.query(crud.AssessmentRecord).filter(crud.AssessmentRecord.session_id == session_id).first()
    if existing_record and not existing_record.completed and existing_record.questions:
        return {
            "assessment_id": existing_record.id,
            "session_id": session_id,
            "subject": session.subject,
            "questions": existing_record.questions,
            "answers": existing_record.answers or [],
            "total": len(existing_record.questions),
        }
        
    # 增加：检查主题维度的全局缓存
    cached_questions = crud.get_assessment_cache(db, session.subject)
    if cached_questions:
        record = crud.create_assessment(db, session_id, cached_questions)
        return {
            "assessment_id": record.id,
            "session_id": session_id,
            "subject": session.subject,
            "questions": cached_questions,
            "total": len(cached_questions),
            "cached": True
        }

    questions = generate_assessment_questions(session.subject, count=10)
    if not questions:
        raise HTTPException(500, "生成题目失败，请重试")
    
    # 存入全局缓存
    crud.set_assessment_cache(db, session.subject, questions)
    
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
        
    # 断线重连：如果在这个 session_id 下已经有未完成的评测记录
    existing_record = db.query(crud.AssessmentRecord).filter(crud.AssessmentRecord.session_id == session_id).first()
    if existing_record and not existing_record.completed and existing_record.questions:
        # 直接由生成器立即返回完整的原有数据，不再请求大模型
        def quick_stream():
            event = {
                "status": "done",
                "questions": existing_record.questions,
                "answers": existing_record.answers or [],
                "assessment_id": existing_record.id,
                "total": len(existing_record.questions)
            }
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        return StreamingResponse(quick_stream(), media_type="text/event-stream")
    
    subject = session.subject  # 提前取出，避免在生成器内依赖外部 Session

    def event_stream():
        # 生成器内部自己创建独立的 DB Session，与路由函数的 Depends 完全解耦
        from db.database import SessionLocal
        stream_db = SessionLocal()
        try:
            # 增加：流式也先检查缓存
            cached_qs = crud.get_assessment_cache(stream_db, subject)
            if cached_qs:
                record = crud.create_assessment(stream_db, session_id, cached_qs)
                event = {
                    "status": "done",
                    "questions": cached_qs,
                    "answers": [],
                    "assessment_id": record.id,
                    "total": len(cached_qs),
                    "cached": True
                }
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                return

            for event in generate_assessment_questions_stream(subject, count=10):
                if event["status"] == "done":
                    questions = event.get("questions", [])
                    if questions:
                        # 存入全局缓存
                        crud.set_assessment_cache(stream_db, subject, questions)
                        record = crud.create_assessment(stream_db, session_id, questions)
                        event["assessment_id"] = record.id
                        event["total"] = len(questions)
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            traceback.print_exc()
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

    proficiency, report, overall_score = evaluate_assessment(session.subject, record.questions, req.answers)
    record = crud.complete_assessment(db, session_id, req.answers, proficiency, report, overall_score)

    return {
        "session_id": session_id,
        "proficiency": proficiency,
        "report": report,
        "overall_score": overall_score
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


@app.post("/assessment/save_answers/{session_id}")
def save_assessment_answers(session_id: int, req: dict, db: Session = Depends(get_db)):
    """保存测评进度（中间答案）"""
    record = db.query(crud.AssessmentRecord).filter(crud.AssessmentRecord.session_id == session_id).first()
    if not record:
        raise HTTPException(404, "测评记录不存在")
    if record.completed:
        raise HTTPException(400, "测评已完成，无法修改答案")
    
    # 获取前端传来的 answers 数组
    answers = req.get("answers", [])
    record.answers = answers
    db.commit()
    return {"status": "success", "session_id": session_id}


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
            traceback.print_exc()
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
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    quiz = db.query(crud.QuizRecord).filter(crud.QuizRecord.id == quiz_id).first()
    if not quiz:
        raise HTTPException(404, "测验记录不存在")

    answers_list = json.loads(answers)

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


@app.get("/session/{session_id}/quizzes")
def get_session_quizzes(session_id: int, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    
    quizzes = db.query(crud.QuizRecord).filter(
        crud.QuizRecord.session_id == session_id,
        crud.QuizRecord.passed.isnot(None) # completed quizzes
    ).order_by(crud.QuizRecord.created_at.desc()).all()
    
    quiz_list = [
        {
            "id": q.id,
            "type": "quiz",
            "item_id": q.item_id,
            "item_title": q.item_title,
            "questions": q.questions,
            "answers": q.answers,
            "score": q.score,
            "passed": q.passed,
            "ai_feedback": q.ai_feedback,
            "attempt_number": q.attempt_number,
            "created_at": q.created_at.isoformat() if q.created_at else None
        } for q in quizzes
    ]

    # 加入入学测评记录
    assessment = db.query(crud.AssessmentRecord).filter(
        crud.AssessmentRecord.session_id == session_id,
        crud.AssessmentRecord.completed == True
    ).first()

    if assessment:
        quiz_list.append({
            "id": assessment.id,
            "type": "assessment",
            "item_title": "入学诊断测试",
            "questions": assessment.questions,
            "answers": assessment.answers,
            "score": assessment.proficiency_result.get("__overall__", 0) if assessment.proficiency_result else 0,
            "passed": True,
            "ai_feedback": assessment.learning_report,
            "attempt_number": 1,
            "created_at": assessment.created_at.isoformat() if assessment.created_at else None
        })

    # 重新按时间排序，确保入学测试在正确位置或按需排序
    # 这里我们保持倒序，入学测试通常是最后（最早）的一个
    
    return {
        "session_id": session_id,
        "quizzes": quiz_list
    }


# ════════════════════════════════════════════════════════
# 期中/期末考试
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
        try:
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

        except Exception as e:
            traceback.print_exc()
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/exam/submit/{session_id}")
async def exam_submit(
    session_id: int,
    exam_id: int = Form(...),
    answers: str = Form(...),
    images: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db)
):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    exam = db.query(crud.ExamRecord).filter(crud.ExamRecord.id == exam_id).first()
    if not exam:
        raise HTTPException(404, "考试记录不存在")

    answers_list = json.loads(answers)
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


class ConfigSaveRequest(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class ConfigTestRequest(BaseModel):
    llm_base_url: str
    llm_api_key: str
    llm_model_name: str


@app.get("/config")
def get_configs(db: Session = Depends(get_db)):
    """获取所有配置"""
    configs = crud.get_all_configs(db)
    return {"configs": configs}


@app.post("/config/save")
def save_config(req: ConfigSaveRequest, db: Session = Depends(get_db)):
    """保存或更新配置"""
    crud.set_config(db, req.key, req.value, req.description)
    return {"status": "ok"}


@app.post("/config/test")
def test_llm_config(req: ConfigTestRequest):
    """测试 LLM 配置是否可用 (真实调用)"""
    from openai import OpenAI
    try:
        client = OpenAI(
            api_key=req.llm_api_key,
            base_url=req.llm_base_url
        )
        # 发起一个极其简单的对话请求
        response = client.chat.completions.create(
            model=req.llm_model_name,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5
        )
        content = response.choices[0].message.content
        return {"status": "ok", "message": f"连接成功！模型响应: {content}"}
    except Exception as e:
        error_msg = str(e)
        # 简化一些常见的错误信息
        if "api_key" in error_msg.lower():
            error_msg = "API Key 错误或无效"
        elif "base_url" in error_msg.lower():
            error_msg = "Base URL 格式错误或无法访问"
        
        raise HTTPException(status_code=400, detail=f"连接失败: {error_msg}")


@app.post("/learning/syllabus")
def syllabus_standalone(req: SyllabusRequest):
    try:
        data = generate_syllabus(req.topic)
        return {"topic": req.topic, "syllabus": data}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/analytics/dashboard/{session_id}")
def get_dashboard_analytics(session_id: int, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    
    # 1. 趋势数据 (Trend): 获取所有已通过的测验分数
    quizzes = db.query(crud.QuizRecord).filter(
        crud.QuizRecord.session_id == session_id,
        crud.QuizRecord.passed == True
    ).order_by(crud.QuizRecord.created_at.asc()).all()
    
    trend = [
        {"date": q.created_at.isoformat() if q.created_at else None, "score": q.score, "item": q.item_title}
        for q in quizzes
    ]
    
    # 2. 掌握度分布 (Mastery Distribution): 从 session.proficiency_data 提取
    mastery_dist = session.proficiency_data or {}
    
    # 3. 考分预测 (Projection)
    avg_score = sum([q.score for q in quizzes]) / len(quizzes) if quizzes else 60
    # 加权计算：平均分 * 0.7 + 过程活跃度等
    projected_score = min(100, avg_score * 0.8 + (session.progress_pct or 0) * 0.3)
    
    return {
        "session_id": session_id,
        "subject": session.subject,
        "progress": session.progress_pct,
        "trend": trend,
        "mastery_distribution": mastery_dist,
        "projected_score": round(projected_score, 1)
    }


# ════════════════════════════════════════════════════════
# 静态文件挂载 (仅用于 Standalone 单镜像部署模式)
# ════════════════════════════════════════════════════════

static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
