"""
AI评测助手路由模块
提供对话交互、报告生成、文件上传解析、评分提取等功能
"""

import os
import re
import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Conversation, Document
from ai.deepseek_client import get_deepseek_client
from ai.prompts import (
    format_research_prompt,
    format_document_prompt,
)
from ai.document_parser import parse_document

# ============================================================
# 路由实例创建
# ============================================================

router = APIRouter(prefix="/api/v1/ai", tags=["AI评测助手"])

# 上传文件存储目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============================================================
# 8维度映射配置
# ============================================================

DIMENSION_NAME_MAP = {
    "研发创新能力": "rd_innovation",
    "知识产权实力": "ip_protection",
    "资质培育进度": "qualification_progress",
    "融资与估值能力": "financing_valuation",
    "法律治理合规": "legal_governance",
    "财务税务能力": "financial_tax",
    "上市准备度": "ipo_readiness",
    "人才资源": "talent_resources",
}

DIMENSION_ID_MAP = {v: k for k, v in DIMENSION_NAME_MAP.items()}

# ============================================================
# Pydantic 请求/响应模型
# ============================================================

class ChatMessage(BaseModel):
    """单条对话消息"""
    role: str = Field(..., description="消息角色：user/assistant/system")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """非流式对话请求"""
    session_id: Optional[str] = Field(None, description="会话ID，为空则创建新会话")
    message: str = Field(..., description="用户消息内容")
    company_info: Optional[Dict[str, Any]] = Field(None, description="企业信息（用于生成报告）")


class ChatResponse(BaseModel):
    """对话响应包装"""
    success: bool = Field(True, description="是否成功")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    message: str = Field("操作成功", description="提示信息")


class StreamChatRequest(BaseModel):
    """流式对话请求"""
    session_id: Optional[str] = Field(None, description="会话ID")
    message: str = Field(..., description="用户消息内容")
    company_info: Optional[Dict[str, Any]] = Field(None, description="企业信息（用于生成报告）")


class ExtractScoresRequest(BaseModel):
    """提取评分请求"""
    session_id: str = Field(..., description="会话ID")
    report_text: Optional[str] = Field(None, description="报告文本，为空则使用会话中的报告")


class ExportReportRequest(BaseModel):
    """导出报告请求"""
    session_id: str = Field(..., description="会话ID")
    format: str = Field("markdown", description="导出格式：markdown")


class ConversationSummary(BaseModel):
    """对话摘要"""
    session_id: str
    title: str
    current_task: str
    status: str
    created_at: datetime
    updated_at: datetime


class ConversationDetail(BaseModel):
    """对话详情"""
    session_id: str
    title: str
    messages: List[Dict[str, Any]]
    current_task: str
    status: str
    generated_report: Optional[str]
    extracted_scores: Optional[Dict[str, float]]
    company_info: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


# ============================================================
# 辅助函数
# ============================================================

def _generate_session_id() -> str:
    """生成唯一会话ID"""
    return str(uuid.uuid4())


def _detect_report_intent(message: str) -> bool:
    """检测用户是否有生成报告的意图
    
    关键词匹配：生成报告、调研报告、分析报告、评估报告等
    """
    intent_keywords = [
        "生成报告", "调研报告", "分析报告", "评估报告",
        "生成调研", "出报告", "写报告", "报告生成",
    ]
    lower_msg = message.lower()
    return any(kw in lower_msg for kw in intent_keywords)


def _extract_scores_from_text(text: str) -> Dict[str, float]:
    """从报告文本中提取8维度评分
    
    匹配格式：
    - 研发创新能力: 75分
    - 研发创新能力 75
    """
    scores = {}
    # 匹配多种格式：
    # - 研发创新能力: 75分
    # - 研发创新能力 75
    # - 研发创新能力：75
    # - 1. 研发创新能力: 75分
    # - 研发创新能力: 75
    patterns = [
        # 标准格式：维度名 + : + 数字 + 可选"分"
        r"(?:研发创新能力|知识产权实力|资质培育进度|融资与估值能力|"
        r"法律治理合规|财务税务能力|上市准备度|人才资源)"
        r"[:：]\s*(\d+(?:\.\d+)?)\s*分?",
        # 行首格式：数字. 维度名 + : + 数字
        r"\d+\.\s*(?:研发创新能力|知识产权实力|资质培育进度|融资与估值能力|"
        r"法律治理合规|财务税务能力|上市准备度|人才资源)"
        r"[:：]\s*(\d+(?:\.\d+)?)",
    ]
    
    for pattern_str in patterns:
        pattern = re.compile(pattern_str)
        for match in pattern.finditer(text):
            dim_text = match.group(0)
            score_str = match.group(1)
            # 提取维度名（去掉数字、标点、分数部分）
            dim_name = re.sub(r"\d+\.\s*|[：:]\s*\d+(?:\.\d+)?\s*分?", "", dim_text).strip()
            dim_id = DIMENSION_NAME_MAP.get(dim_name)
            if dim_id and dim_id not in scores:
                try:
                    scores[dim_id] = float(score_str)
                except ValueError:
                    continue
    
    return scores


def _create_success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
    """创建统一格式的成功响应"""
    return {"success": True, "data": data, "message": message}


def _create_error_response(message: str) -> Dict[str, Any]:
    """创建统一格式的错误响应"""
    return {"success": False, "data": None, "message": message}


# ============================================================
# 路由：非流式对话
# ============================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """非流式对话接口
    
    支持普通对话和生成报告意图识别。当检测到用户请求生成报告时，
    调用 DeepSeek 生成 8 维度调研报告。
    """
    # 获取或创建会话
    if request.session_id:
        conversation = db.query(Conversation).filter(
            Conversation.session_id == request.session_id
        ).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到会话: {request.session_id}"
            )
    else:
        session_id = _generate_session_id()
        conversation = Conversation(
            session_id=session_id,
            title=f"新对话 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            messages=[],
            current_task="chat",
            status="active",
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 更新企业信息（如果提供）
    if request.company_info:
        conversation.company_info = request.company_info
        # 更新标题
        company_name = request.company_info.get("name", "")
        if company_name and conversation.title.startswith("新对话"):
            conversation.title = f"{company_name} 评测对话"

    # 添加用户消息到历史
    messages_history = conversation.messages or []
    messages_history.append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.now().isoformat(),
    })

    # 检测生成报告意图
    is_report_intent = _detect_report_intent(request.message)
    ai_response_content = ""

    if is_report_intent and request.company_info:
        # 生成调研报告
        conversation.current_task = "report"
        try:
            client = get_deepseek_client()
            research_prompt = format_research_prompt(request.company_info)
            system_prompt = client.get_system_prompt("researcher")
            
            ai_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": research_prompt},
            ]
            
            resp = await client.chat(ai_messages, temperature=0.7, max_tokens=4000)
            ai_response_content = resp["choices"][0]["message"]["content"]
            conversation.generated_report = ai_response_content
            
            # 尝试提取评分
            extracted = _extract_scores_from_text(ai_response_content)
            if extracted:
                conversation.extracted_scores = extracted
                
        except Exception as e:
            conversation.status = "error"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI 报告生成失败: {str(e)}"
            )
    else:
        # 普通对话
        try:
            client = get_deepseek_client()
            system_prompt = (
                "你是 AI 科创企业评测助手。通过与用户对话收集企业信息，"
                "帮助用户理解评测标准和改进方向。保持专业、友好、高效的对话风格。"
            )
            
            ai_messages = [{"role": "system", "content": system_prompt}]
            # 添加历史消息（最近10条，避免超出上下文）
            for msg in messages_history[-10:]:
                ai_messages.append({"role": msg["role"], "content": msg["content"]})
            
            resp = await client.chat(ai_messages, temperature=0.7, max_tokens=2000)
            ai_response_content = resp["choices"][0]["message"]["content"]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI 对话失败: {str(e)}"
            )

    # 添加AI回复到历史
    messages_history.append({
        "role": "assistant",
        "content": ai_response_content,
        "timestamp": datetime.now().isoformat(),
    })
    conversation.messages = messages_history
    conversation.updated_at = datetime.now()
    
    db.commit()
    db.refresh(conversation)

    return ChatResponse(
        success=True,
        data={
            "session_id": conversation.session_id,
            "reply": ai_response_content,
            "is_report": is_report_intent,
            "extracted_scores": conversation.extracted_scores,
        },
        message="对话完成" if not is_report_intent else "报告生成成功",
    )


# ============================================================
# 路由：流式对话（SSE）
# ============================================================

@router.post("/chat/stream")
async def chat_stream(request: StreamChatRequest, db: Session = Depends(get_db)):
    """SSE 流式对话接口
    
    逐段返回 AI 生成的文本内容，适合前端实时展示。
    """
    # 获取或创建会话
    if request.session_id:
        conversation = db.query(Conversation).filter(
            Conversation.session_id == request.session_id
        ).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到会话: {request.session_id}"
            )
    else:
        session_id = _generate_session_id()
        conversation = Conversation(
            session_id=session_id,
            title=f"流式对话 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            messages=[],
            current_task="chat",
            status="active",
        )
        db.add(conversation)
        db.commit()

    # 添加用户消息到历史
    messages_history = conversation.messages or []
    messages_history.append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.now().isoformat(),
    })

    # 更新企业信息（如果提供）
    if request.company_info:
        conversation.company_info = request.company_info
        company_name = request.company_info.get("name", "")
        if company_name and conversation.title.startswith("流式对话"):
            conversation.title = f"{company_name} 评测对话"

    # 检测生成报告意图
    is_report_intent = _detect_report_intent(request.message)

    async def event_generator():
        """SSE 事件生成器"""
        full_content = ""
        try:
            client = get_deepseek_client()

            if is_report_intent and request.company_info:
                # 生成调研报告
                conversation.current_task = "report"
                research_prompt = format_research_prompt(request.company_info)
                system_prompt = client.get_system_prompt("researcher")
                ai_messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": research_prompt},
                ]
                max_tokens = 4000
            else:
                # 普通对话
                system_prompt = (
                    "你是 AI 科创企业评测助手。通过与用户对话收集企业信息，"
                    "帮助用户理解评测标准和改进方向。保持专业、友好、高效的对话风格。"
                )
                ai_messages = [{"role": "system", "content": system_prompt}]
                for msg in messages_history[-10:]:
                    ai_messages.append({"role": msg["role"], "content": msg["content"]})
                max_tokens = 2000

            async for chunk in client.chat_stream(ai_messages, temperature=0.7, max_tokens=max_tokens):
                full_content += chunk
                yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"

            # 流结束后，保存完整回复到数据库
            messages_history.append({
                "role": "assistant",
                "content": full_content,
                "timestamp": datetime.now().isoformat(),
            })
            conversation.messages = messages_history

            # 如果是报告，保存报告并尝试提取评分
            if is_report_intent and request.company_info:
                conversation.generated_report = full_content
                extracted = _extract_scores_from_text(full_content)
                if extracted:
                    conversation.extracted_scores = extracted

            conversation.updated_at = datetime.now()
            db.commit()

            yield f"data: {json.dumps({'type': 'done', 'session_id': conversation.session_id, 'extracted_scores': conversation.extracted_scores}, ensure_ascii=False)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ============================================================
# 路由：对话列表
# ============================================================

@router.get("/conversations")
async def list_conversations(
    status: Optional[str] = None,
    task: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """获取对话列表
    
    支持按状态、任务类型筛选，分页返回。
    """
    query = db.query(Conversation)
    
    if status:
        query = query.filter(Conversation.status == status)
    if task:
        query = query.filter(Conversation.current_task == task)
    
    total = query.count()
    conversations = query.order_by(Conversation.updated_at.desc()).offset(offset).limit(limit).all()
    
    items = []
    for conv in conversations:
        items.append({
            "session_id": conv.session_id,
            "title": conv.title,
            "current_task": conv.current_task,
            "status": conv.status,
            "created_at": conv.created_at.isoformat() if conv.created_at else None,
            "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
        })
    
    return _create_success_response({
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    })


# ============================================================
# 路由：对话详情
# ============================================================

@router.get("/conversations/{session_id}")
async def get_conversation(session_id: str, db: Session = Depends(get_db)):
    """获取单个对话详情"""
    conversation = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到会话: {session_id}"
        )
    
    return _create_success_response({
        "session_id": conversation.session_id,
        "title": conversation.title,
        "messages": conversation.messages or [],
        "current_task": conversation.current_task,
        "status": conversation.status,
        "generated_report": conversation.generated_report,
        "extracted_scores": conversation.extracted_scores,
        "company_info": conversation.company_info,
        "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
        "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
    })


# ============================================================
# 路由：文件上传与AI分析
# ============================================================

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(..., description="上传文件（PDF/DOCX/XLSX/TXT）"),
    session_id: Optional[str] = Form(None, description="关联会话ID"),
    company_id: Optional[int] = Form(None, description="关联企业ID"),
    db: Session = Depends(get_db),
):
    """文件上传、解析与AI分析
    
    1. 保存文件到 uploads/ 目录
    2. 调用文档解析模块提取文本
    3. 调用 DeepSeek 进行 8 维度分析
    4. 保存解析结果到数据库
    """
    # 验证文件类型
    allowed_extensions = (".pdf", ".docx", ".xlsx", ".txt", ".md")
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {file_ext}，仅支持 {', '.join(allowed_extensions)}"
        )
    
    # 保存文件
    safe_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )
    
    # 解析文档
    try:
        file_type = file_ext.lstrip(".")
        parse_result = parse_document(file_path, file_type=file_type)
    except Exception as e:
        # 解析失败也保留文件，但记录错误
        parse_result = {
            "status": "error",
            "error": str(e),
            "text": "",
            "summary": "",
            "pages": 0,
        }
    
    # 创建数据库记录
    doc_record = Document(
        company_id=company_id,
        conversation_id=None,  # 后面关联
        filename=file.filename,
        original_path=file_path,
        file_type=file_type,
        file_size=len(content),
        parsed_text=parse_result.get("text", ""),
        parsed_summary=parse_result.get("summary", ""),
        status="parsed" if parse_result.get("status") == "success" else "error",
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)
    
    # 关联会话
    conversation = None
    if session_id:
        conversation = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
    
    if not conversation:
        # 创建新会话
        session_id = _generate_session_id()
        conversation = Conversation(
            session_id=session_id,
            title=f"文档分析: {file.filename}",
            messages=[],
            current_task="review",
            status="active",
            documents=[doc_record.id],
        )
        db.add(conversation)
    else:
        docs = conversation.documents or []
        docs.append(doc_record.id)
        conversation.documents = docs
        conversation.updated_at = datetime.now()
    
    # AI 分析文档
    ai_analysis = ""
    if parse_result.get("status") == "success" and parse_result.get("text"):
        try:
            client = get_deepseek_client()
            doc_prompt = format_document_prompt(parse_result["text"])
            system_prompt = client.get_system_prompt("document_analyst")
            
            ai_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": doc_prompt},
            ]
            resp = await client.chat(ai_messages, temperature=0.7, max_tokens=4000)
            ai_analysis = resp["choices"][0]["message"]["content"]
            
            # 将AI分析加入对话
            messages = conversation.messages or []
            messages.append({
                "role": "system",
                "content": f"[文档分析] 已上传文件: {file.filename}",
                "timestamp": datetime.now().isoformat(),
            })
            messages.append({
                "role": "assistant",
                "content": ai_analysis,
                "timestamp": datetime.now().isoformat(),
            })
            conversation.messages = messages
            
            # 尝试提取评分
            extracted = _extract_scores_from_text(ai_analysis)
            if extracted:
                conversation.extracted_scores = extracted
                
        except Exception as e:
            ai_analysis = f"AI 分析过程中发生错误: {str(e)}"
    
    db.commit()
    db.refresh(conversation)
    db.refresh(doc_record)
    
    return _create_success_response({
        "document_id": doc_record.id,
        "session_id": conversation.session_id,
        "filename": file.filename,
        "file_type": file_type,
        "file_size": len(content),
        "parse_status": parse_result.get("status"),
        "parse_summary": parse_result.get("summary", ""),
        "pages": parse_result.get("pages", 0),
        "ai_analysis": ai_analysis,
        "extracted_scores": conversation.extracted_scores if conversation else None,
    }, message="文件上传并分析完成")


# ============================================================
# 路由：提取评分
# ============================================================

@router.post("/extract-scores")
async def extract_scores(request: ExtractScoresRequest, db: Session = Depends(get_db)):
    """从报告文本提取8维度评分
    
    支持从已生成的报告或传入的文本中提取评分。
    """
    conversation = db.query(Conversation).filter(
        Conversation.session_id == request.session_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到会话: {request.session_id}"
        )
    
    # 获取报告文本
    report_text = request.report_text or conversation.generated_report or ""
    if not report_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="会话中未生成报告，且未提供 report_text"
        )
    
    scores = _extract_scores_from_text(report_text)
    
    # 保存提取结果
    conversation.extracted_scores = scores
    conversation.updated_at = datetime.now()
    db.commit()
    
    # 构建中文维度名结果
    score_details = {}
    for dim_id, score in scores.items():
        dim_name = DIMENSION_ID_MAP.get(dim_id, dim_id)
        score_details[dim_name] = score
    
    return _create_success_response({
        "session_id": request.session_id,
        "scores": scores,
        "score_details": score_details,
        "missing_dimensions": [
            dim_id for dim_id in DIMENSION_NAME_MAP.values()
            if dim_id not in scores
        ],
    }, message="评分提取完成")


# ============================================================
# 路由：导出报告
# ============================================================

@router.post("/export-report")
async def export_report(request: ExportReportRequest, db: Session = Depends(get_db)):
    """导出报告为 Markdown 格式
    
    返回报告全文及元信息，前端可直接下载为 .md 文件。
    """
    conversation = db.query(Conversation).filter(
        Conversation.session_id == request.session_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到会话: {request.session_id}"
        )
    
    report = conversation.generated_report or ""
    if not report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="会话中未生成报告，无法导出"
        )
    
    # 构建 Markdown 文件内容
    company_info = conversation.company_info or {}
    company_name = company_info.get("name", "未命名企业")
    
    markdown_content = f"""# {company_name} 科创企业调研报告

> 生成时间: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S') if conversation.created_at else '未知'}
> 会话ID: {conversation.session_id}

---

{report}

---

## 提取评分

"""
    scores = conversation.extracted_scores or {}
    if scores:
        for dim_id, score in scores.items():
            dim_name = DIMENSION_ID_MAP.get(dim_id, dim_id)
            markdown_content += f"- {dim_name}: {score} 分\n"
    else:
        markdown_content += "（未提取到评分）\n"
    
    return _create_success_response({
        "session_id": request.session_id,
        "format": "markdown",
        "filename": f"{company_name}_调研报告.md",
        "content": markdown_content,
    }, message="报告导出成功")
