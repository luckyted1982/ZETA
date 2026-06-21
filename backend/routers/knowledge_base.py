"""
知识库路由模块
提供知识文档的增删改查、AI 问答、分类统计等功能
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from database.db import get_db
from database.models import KnowledgeDoc
from ai.deepseek_client import get_deepseek_client
from ai.prompts import format_knowledge_qa_prompt

# ============================================================
# 路由实例创建
# ============================================================

router = APIRouter(prefix="/api/v1/knowledge", tags=["知识库"])

# ============================================================
# Pydantic 请求/响应模型
# ============================================================

class KnowledgeDocCreate(BaseModel):
    """添加知识文档请求"""
    title: str = Field(..., min_length=1, max_length=500, description="文档标题")
    doc_type: str = Field(..., description="文档类型: law/policy/report/standard/whitepaper")
    category: Optional[str] = Field(None, max_length=100, description="细分分类")
    content: str = Field(..., min_length=1, description="完整内容")
    content_summary: Optional[str] = Field(None, description="内容摘要")
    source_url: Optional[str] = Field(None, max_length=1000, description="来源链接")
    tags: Optional[List[str]] = Field(None, description="标签列表")


class KnowledgeDocUpdate(BaseModel):
    """更新知识文档请求"""
    title: Optional[str] = Field(None, max_length=500)
    doc_type: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = None
    content_summary: Optional[str] = None
    source_url: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None


class KnowledgeQueryRequest(BaseModel):
    """知识库问答请求"""
    question: str = Field(..., min_length=1, description="用户问题")
    top_k: int = Field(5, ge=1, le=20, description="检索相关文档数量")
    doc_types: Optional[List[str]] = Field(None, description="限定文档类型")


# ============================================================
# 辅助函数
# ============================================================

def _create_success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
    """创建统一格式的成功响应"""
    return {"success": True, "data": data, "message": message}


def _search_knowledge_docs(
    db: Session,
    keyword: str,
    top_k: int = 5,
    doc_types: Optional[List[str]] = None,
) -> List[KnowledgeDoc]:
    """关键词检索知识库文档
    
    简单实现：在标题、内容、标签中模糊匹配关键词。
    生产环境建议接入向量检索（如 Embedding + FAISS）。
    """
    query = db.query(KnowledgeDoc).filter(KnowledgeDoc.is_active == True)
    
    # 关键词匹配（标题、内容、标签）
    like_pattern = f"%{keyword}%"
    query = query.filter(
        or_(
            KnowledgeDoc.title.like(like_pattern),
            KnowledgeDoc.content.like(like_pattern),
            KnowledgeDoc.category.like(like_pattern),
        )
    )
    
    # 文档类型过滤
    if doc_types:
        query = query.filter(KnowledgeDoc.doc_type.in_(doc_types))
    
    # 按相关性排序（标题匹配优先）
    results = query.order_by(
        func.case(
            (KnowledgeDoc.title.like(like_pattern), 1),
            else_=0
        ).desc()
    ).limit(top_k).all()
    
    return results


def _build_context_from_docs(docs: List[KnowledgeDoc]) -> str:
    """从检索到的文档构建上下文文本"""
    context_parts = []
    for doc in docs:
        part = f"【{doc.title}】({doc.doc_type})\n"
        # 截取内容前 2000 字作为上下文
        content_snippet = doc.content[:2000] if doc.content else ""
        if len(doc.content or "") > 2000:
            content_snippet += "..."
        part += content_snippet
        context_parts.append(part)
    return "\n\n---\n\n".join(context_parts)


# ============================================================
# 路由：添加知识文档
# ============================================================

@router.post("/docs")
async def create_knowledge_doc(request: KnowledgeDocCreate, db: Session = Depends(get_db)):
    """添加知识库文档
    
    支持法规、政策、研报、标准、白皮书等类型。
    """
    # 验证文档类型
    valid_types = ["law", "policy", "report", "standard", "whitepaper"]
    if request.doc_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的文档类型: {request.doc_type}，必须是以下之一: {', '.join(valid_types)}"
        )
    
    # 自动生成摘要（如果未提供）
    content_summary = request.content_summary or (request.content[:300] + "..." if len(request.content) > 300 else request.content)
    
    doc = KnowledgeDoc(
        title=request.title,
        doc_type=request.doc_type,
        category=request.category,
        content=request.content,
        content_summary=content_summary,
        source_url=request.source_url,
        tags=request.tags or [],
        is_active=True,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    return _create_success_response({
        "id": doc.id,
        "title": doc.title,
        "doc_type": doc.doc_type,
        "category": doc.category,
        "source_url": doc.source_url,
        "tags": doc.tags,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
    }, message="知识文档添加成功")


# ============================================================
# 路由：知识文档列表（支持筛选）
# ============================================================

@router.get("/docs")
async def list_knowledge_docs(
    doc_type: Optional[str] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """获取知识文档列表
    
    支持按文档类型、分类、关键词筛选。
    """
    query = db.query(KnowledgeDoc).filter(KnowledgeDoc.is_active == True)
    
    if doc_type:
        query = query.filter(KnowledgeDoc.doc_type == doc_type)
    
    if category:
        query = query.filter(KnowledgeDoc.category == category)
    
    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                KnowledgeDoc.title.like(like_pattern),
                KnowledgeDoc.content.like(like_pattern),
                KnowledgeDoc.tags.like(like_pattern),
            )
        )
    
    total = query.count()
    docs = query.order_by(KnowledgeDoc.created_at.desc()).offset(offset).limit(limit).all()
    
    items = []
    for d in docs:
        items.append({
            "id": d.id,
            "title": d.title,
            "doc_type": d.doc_type,
            "category": d.category,
            "content_summary": d.content_summary,
            "source_url": d.source_url,
            "tags": d.tags,
            "is_active": d.is_active,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        })
    
    return _create_success_response({
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    })


# ============================================================
# 路由：知识文档详情
# ============================================================

@router.get("/docs/{id}")
async def get_knowledge_doc(id: int, db: Session = Depends(get_db)):
    """获取知识文档详情"""
    doc = db.query(KnowledgeDoc).filter(
        KnowledgeDoc.id == id,
        KnowledgeDoc.is_active == True,
    ).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到知识文档: ID={id}"
        )
    
    return _create_success_response({
        "id": doc.id,
        "title": doc.title,
        "doc_type": doc.doc_type,
        "category": doc.category,
        "content": doc.content,
        "content_summary": doc.content_summary,
        "source_url": doc.source_url,
        "tags": doc.tags,
        "is_active": doc.is_active,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
    })


# ============================================================
# 路由：更新知识文档
# ============================================================

@router.put("/docs/{id}")
async def update_knowledge_doc(id: int, request: KnowledgeDocUpdate, db: Session = Depends(get_db)):
    """更新知识文档"""
    doc = db.query(KnowledgeDoc).filter(
        KnowledgeDoc.id == id,
        KnowledgeDoc.is_active == True,
    ).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到知识文档: ID={id}"
        )
    
    # 验证文档类型（如果传入）
    if request.doc_type is not None:
        valid_types = ["law", "policy", "report", "standard", "whitepaper"]
        if request.doc_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的文档类型: {request.doc_type}"
            )
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doc, field, value)
    
    doc.updated_at = datetime.now()
    db.commit()
    db.refresh(doc)
    
    return _create_success_response({
        "id": doc.id,
        "title": doc.title,
        "doc_type": doc.doc_type,
        "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
    }, message="知识文档更新成功")


# ============================================================
# 路由：软删除知识文档
# ============================================================

@router.delete("/docs/{id}")
async def delete_knowledge_doc(id: int, db: Session = Depends(get_db)):
    """软删除知识文档
    
    将 is_active 设为 False，数据保留可追溯。
    """
    doc = db.query(KnowledgeDoc).filter(KnowledgeDoc.id == id).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到知识文档: ID={id}"
        )
    
    doc.is_active = False
    doc.updated_at = datetime.now()
    db.commit()
    
    return _create_success_response({
        "id": doc.id,
        "title": doc.title,
    }, message="知识文档已删除")


# ============================================================
# 路由：AI 问答
# ============================================================

@router.post("/query")
async def knowledge_query(request: KnowledgeQueryRequest, db: Session = Depends(get_db)):
    """知识库 AI 问答
    
    1. 关键词检索相关文档
    2. 构建上下文
    3. 调用 DeepSeek 生成专业回答
    """
    # 检索相关文档
    related_docs = _search_knowledge_docs(
        db=db,
        keyword=request.question,
        top_k=request.top_k,
        doc_types=request.doc_types,
    )
    
    if not related_docs:
        # 没有相关文档时，直接让AI基于通用知识回答
        context = "（知识库中未检索到直接相关文档，以下为基于通用专业知识的回答）"
    else:
        context = _build_context_from_docs(related_docs)
    
    # 调用 DeepSeek 生成回答
    try:
        client = get_deepseek_client()
        qa_prompt = format_knowledge_qa_prompt(context, request.question)
        system_prompt = client.get_system_prompt("knowledge_expert")
        
        ai_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": qa_prompt},
        ]
        resp = await client.chat(ai_messages, temperature=0.7, max_tokens=3000)
        answer = resp["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 回答生成失败: {str(e)}"
        )
    
    # 构建引用来源
    references = []
    for doc in related_docs:
        references.append({
            "id": doc.id,
            "title": doc.title,
            "doc_type": doc.doc_type,
            "category": doc.category,
            "source_url": doc.source_url,
        })
    
    return _create_success_response({
        "question": request.question,
        "answer": answer,
        "references": references,
        "retrieved_count": len(related_docs),
    }, message="回答生成成功")


# ============================================================
# 路由：分类统计
# ============================================================

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """获取知识库分类统计
    
    按文档类型和分类统计数量。
    """
    # 按 doc_type 统计
    type_stats = db.query(
        KnowledgeDoc.doc_type,
        func.count(KnowledgeDoc.id).label("count")
    ).filter(KnowledgeDoc.is_active == True).group_by(KnowledgeDoc.doc_type).all()
    
    # 按 category 统计
    category_stats = db.query(
        KnowledgeDoc.category,
        func.count(KnowledgeDoc.id).label("count")
    ).filter(
        KnowledgeDoc.is_active == True,
        KnowledgeDoc.category.isnot(None),
    ).group_by(KnowledgeDoc.category).all()
    
    return _create_success_response({
        "doc_types": [
            {"type": t, "count": c, "label": _get_doc_type_label(t)}
            for t, c in type_stats
        ],
        "categories": [
            {"category": cat, "count": c}
            for cat, c in category_stats
        ],
        "total": sum(c for _, c in type_stats),
    })


def _get_doc_type_label(doc_type: str) -> str:
    """获取文档类型中文标签"""
    labels = {
        "law": "法律法规",
        "policy": "政策文件",
        "report": "行业研报",
        "standard": "评测标准",
        "whitepaper": "白皮书",
    }
    return labels.get(doc_type, doc_type)
