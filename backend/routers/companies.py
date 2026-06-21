"""
企业库路由模块
提供企业信息的增删改查、评测执行、评测历史管理等功能
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from database.db import get_db
from database.models import Company, EvaluationRecord
from models import SimpleEvaluationRequest, CompanyInfo
from evaluation_engine import EvaluationEngine

# ============================================================
# 路由实例创建
# ============================================================

router = APIRouter(prefix="/api/v1/companies", tags=["企业库"])

# 全局评测引擎实例
evaluation_engine = EvaluationEngine()

# ============================================================
# Pydantic 请求/响应模型
# ============================================================

class CompanyCreateRequest(BaseModel):
    """创建企业请求"""
    name: str = Field(..., min_length=1, max_length=200, description="企业名称")
    industry: Optional[str] = Field(None, max_length=100, description="所属行业")
    stage: str = Field(..., description="发展阶段: seed/angel/pre-a/a-round")
    founded_year: Optional[int] = Field(None, ge=1990, le=2030, description="成立年份")
    employees: Optional[int] = Field(None, ge=0, description="员工人数")
    location: Optional[str] = Field(None, max_length=200, description="所在地区")
    description: Optional[str] = Field(None, max_length=2000, description="企业简介")
    tech_direction: Optional[str] = Field(None, max_length=500, description="核心技术方向")
    qualifications: Optional[List[str]] = Field(None, description="已获资质列表")
    funding_status: Optional[str] = Field(None, max_length=100, description="融资状态")


class CompanyUpdateRequest(BaseModel):
    """更新企业请求（所有字段可选）"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    stage: Optional[str] = Field(None)
    founded_year: Optional[int] = Field(None, ge=1990, le=2030)
    employees: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    tech_direction: Optional[str] = Field(None, max_length=500)
    qualifications: Optional[List[str]] = None
    funding_status: Optional[str] = Field(None, max_length=100)


class EvaluateRequest(BaseModel):
    """执行评测请求"""
    dimension_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="各维度总分数，如 {'rd_innovation': 75.0}"
    )
    evaluator: Optional[str] = Field(None, description="评测人/机构")


class CompanyListResponse(BaseModel):
    """企业列表响应项"""
    id: int
    name: str
    industry: Optional[str]
    stage: str
    founded_year: Optional[int]
    employees: Optional[int]
    location: Optional[str]
    tech_direction: Optional[str]
    funding_status: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class EvaluationHistoryItem(BaseModel):
    """评测历史记录项"""
    id: int
    evaluation_id: str
    total_score: Optional[float]
    overall_grade: Optional[str]
    overall_grade_label: Optional[str]
    evaluator: Optional[str]
    evaluation_date: Optional[str]
    created_at: Optional[str]


# ============================================================
# 辅助函数
# ============================================================

def _create_success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
    """创建统一格式的成功响应"""
    return {"success": True, "data": data, "message": message}


def _validate_stage(stage: str) -> None:
    """验证发展阶段是否合法"""
    valid_stages = ["seed", "angel", "pre-a", "a-round"]
    if stage not in valid_stages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的发展阶段: {stage}，必须是以下之一: {', '.join(valid_stages)}"
        )


# ============================================================
# 路由：创建企业
# ============================================================

@router.post("")
async def create_company(request: CompanyCreateRequest, db: Session = Depends(get_db)):
    """创建企业信息
    
    接收企业基本信息，保存到数据库。名称和阶段为必填项。
    """
    _validate_stage(request.stage)
    
    # 检查是否已存在同名企业
    existing = db.query(Company).filter(Company.name == request.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"企业 '{request.name}' 已存在"
        )
    
    company = Company(
        name=request.name,
        industry=request.industry,
        stage=request.stage,
        founded_year=request.founded_year,
        employees=request.employees,
        location=request.location,
        description=request.description,
        tech_direction=request.tech_direction,
        qualifications=request.qualifications or [],
        funding_status=request.funding_status,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    
    return _create_success_response({
        "id": company.id,
        "name": company.name,
        "industry": company.industry,
        "stage": company.stage,
        "created_at": company.created_at.isoformat() if company.created_at else None,
    }, message="企业创建成功")


# ============================================================
# 路由：企业列表（支持筛选）
# ============================================================

@router.get("")
async def list_companies(
    keyword: Optional[str] = None,
    industry: Optional[str] = None,
    stage: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """获取企业列表
    
    支持按关键词（名称/简介/技术方向）、行业、发展阶段筛选。
    """
    query = db.query(Company)
    
    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                Company.name.like(like_pattern),
                Company.description.like(like_pattern),
                Company.tech_direction.like(like_pattern),
            )
        )
    
    if industry:
        query = query.filter(Company.industry == industry)
    
    if stage:
        query = query.filter(Company.stage == stage)
    
    total = query.count()
    companies = query.order_by(Company.created_at.desc()).offset(offset).limit(limit).all()
    
    items = []
    for c in companies:
        # 计算评测次数和最新得分
        eval_count = len(c.evaluations) if c.evaluations else 0
        latest_score = None
        if c.evaluations:
            latest = sorted(c.evaluations, key=lambda x: x.evaluation_date or datetime.min, reverse=True)[0]
            latest_score = latest.total_score
        
        items.append({
            "id": c.id,
            "name": c.name,
            "industry": c.industry,
            "stage": c.stage,
            "founded_year": c.founded_year,
            "employees": c.employees,
            "location": c.location,
            "tech_direction": c.tech_direction,
            "funding_status": c.funding_status,
            "evaluation_count": eval_count,
            "latest_score": latest_score,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        })
    
    return _create_success_response({
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    })


# ============================================================
# 路由：企业详情
# ============================================================

@router.get("/{id}")
async def get_company(id: int, db: Session = Depends(get_db)):
    """获取企业详情
    
    包含企业基本信息和关联的评测记录数量。
    """
    company = db.query(Company).filter(Company.id == id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到企业: ID={id}"
        )
    
    # 统计评测记录数
    eval_count = db.query(EvaluationRecord).filter(
        EvaluationRecord.company_id == id
    ).count()
    
    return _create_success_response({
        "id": company.id,
        "name": company.name,
        "industry": company.industry,
        "stage": company.stage,
        "founded_year": company.founded_year,
        "employees": company.employees,
        "location": company.location,
        "description": company.description,
        "tech_direction": company.tech_direction,
        "qualifications": company.qualifications or [],
        "funding_status": company.funding_status,
        "evaluation_count": eval_count,
        "created_at": company.created_at.isoformat() if company.created_at else None,
        "updated_at": company.updated_at.isoformat() if company.updated_at else None,
    })


# ============================================================
# 路由：更新企业
# ============================================================

@router.put("/{id}")
async def update_company(id: int, request: CompanyUpdateRequest, db: Session = Depends(get_db)):
    """更新企业信息
    
    只更新传入的字段，未传入的字段保持不变。
    """
    company = db.query(Company).filter(Company.id == id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到企业: ID={id}"
        )
    
    # 验证阶段（如果传入）
    if request.stage is not None:
        _validate_stage(request.stage)
    
    # 只更新非 None 的字段
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    
    company.updated_at = datetime.now()
    db.commit()
    db.refresh(company)
    
    return _create_success_response({
        "id": company.id,
        "name": company.name,
        "industry": company.industry,
        "stage": company.stage,
        "updated_at": company.updated_at.isoformat() if company.updated_at else None,
    }, message="企业更新成功")


# ============================================================
# 路由：删除企业（级联删除）
# ============================================================

@router.delete("/{id}")
async def delete_company(id: int, db: Session = Depends(get_db)):
    """删除企业及其关联数据
    
    级联删除：评测记录、文档等关联数据一并删除。
    """
    company = db.query(Company).filter(Company.id == id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到企业: ID={id}"
        )
    
    name = company.name
    db.delete(company)
    db.commit()
    
    return _create_success_response({
        "id": id,
        "name": name,
    }, message="企业删除成功")


# ============================================================
# 路由：执行评测
# ============================================================

@router.post("/{id}/evaluate")
async def evaluate_company(id: int, request: EvaluateRequest, db: Session = Depends(get_db)):
    """对企业执行评测
    
    调用 EvaluationEngine 的 evaluate_simple 方法，
    将结果保存到 EvaluationRecord 表。
    """
    company = db.query(Company).filter(Company.id == id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到企业: ID={id}"
        )
    
    # 验证维度分数
    if not request.dimension_scores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请至少为一个维度评分"
        )
    
    for dim_id, score in request.dimension_scores.items():
        if score < 0 or score > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"维度 {dim_id} 的分数 {score} 超出范围，必须在 0-100 之间"
            )
    
    # 构建评测请求
    company_info = CompanyInfo(
        name=company.name,
        stage=company.stage,
        industry=company.industry,
        founded_year=company.founded_year,
        employees=company.employees,
        location=company.location,
        description=company.description,
    )
    
    eval_request = SimpleEvaluationRequest(
        company=company_info,
        dimension_scores=request.dimension_scores,
        evaluator=request.evaluator,
    )
    
    try:
        # 执行评测
        result = evaluation_engine.evaluate_simple(eval_request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评测执行失败: {str(e)}"
        )
    
    # 生成唯一评测ID
    evaluation_id = str(uuid.uuid4())
    
    # 保存到数据库
    record = EvaluationRecord(
        company_id=company.id,
        evaluation_id=evaluation_id,
        dimension_scores=request.dimension_scores,
        total_score=result.total_score,
        overall_grade=result.overall_grade,
        overall_grade_label=result.overall_grade_label,
        stage_weights=result.stage_weights,
        strengths=result.strengths,
        weaknesses=result.weaknesses,
        risks=result.risks,
        scoring_explanation=result.scoring_explanation,
        evaluator=request.evaluator,
        evaluation_date=datetime.now(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return _create_success_response({
        "evaluation_id": evaluation_id,
        "company_id": company.id,
        "company_name": company.name,
        "total_score": result.total_score,
        "overall_grade": result.overall_grade,
        "overall_grade_label": result.overall_grade_label,
        "stage_weights": result.stage_weights,
        "strengths": result.strengths,
        "weaknesses": result.weaknesses,
        "risks": result.risks,
        "evaluation_date": record.evaluation_date.isoformat() if record.evaluation_date else None,
    }, message="评测完成")


# ============================================================
# 路由：评测历史
# ============================================================

@router.get("/{id}/evaluations")
async def get_evaluation_history(
    id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """获取企业的评测历史记录
    
    按时间倒序返回评测记录列表。
    """
    company = db.query(Company).filter(Company.id == id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到企业: ID={id}"
        )
    
    query = db.query(EvaluationRecord).filter(EvaluationRecord.company_id == id)
    total = query.count()
    records = query.order_by(EvaluationRecord.evaluation_date.desc()).offset(offset).limit(limit).all()
    
    items = []
    for r in records:
        items.append({
            "id": r.id,
            "evaluation_id": r.evaluation_id,
            "total_score": r.total_score,
            "overall_grade": r.overall_grade,
            "overall_grade_label": r.overall_grade_label,
            "evaluator": r.evaluator,
            "evaluation_date": r.evaluation_date.isoformat() if r.evaluation_date else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    
    return _create_success_response({
        "company_id": id,
        "company_name": company.name,
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    })


# ============================================================
# 路由：评测详情
# ============================================================

@router.get("/{id}/evaluations/{evaluation_id}")
async def get_evaluation_detail(id: int, evaluation_id: str, db: Session = Depends(get_db)):
    """获取单次评测详情"""
    company = db.query(Company).filter(Company.id == id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到企业: ID={id}"
        )
    
    record = db.query(EvaluationRecord).filter(
        EvaluationRecord.company_id == id,
        EvaluationRecord.evaluation_id == evaluation_id,
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到评测记录: {evaluation_id}"
        )
    
    return _create_success_response({
        "id": record.id,
        "evaluation_id": record.evaluation_id,
        "company_id": record.company_id,
        "company_name": company.name,
        "dimension_scores": record.dimension_scores,
        "total_score": record.total_score,
        "overall_grade": record.overall_grade,
        "overall_grade_label": record.overall_grade_label,
        "stage_weights": record.stage_weights,
        "strengths": record.strengths,
        "weaknesses": record.weaknesses,
        "risks": record.risks,
        "ai_diagnosis": record.ai_diagnosis,
        "scoring_explanation": record.scoring_explanation,
        "evaluator": record.evaluator,
        "evaluation_date": record.evaluation_date.isoformat() if record.evaluation_date else None,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    })


# ============================================================
# 路由：重新评测
# ============================================================

@router.post("/{id}/evaluations/{evaluation_id}/re-evaluate")
async def re_evaluate(id: int, evaluation_id: str, db: Session = Depends(get_db)):
    """重新评测
    
    基于已有评测记录的维度分数，重新执行评测（可用于更新算法后重新计算）。
    """
    company = db.query(Company).filter(Company.id == id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到企业: ID={id}"
        )
    
    old_record = db.query(EvaluationRecord).filter(
        EvaluationRecord.company_id == id,
        EvaluationRecord.evaluation_id == evaluation_id,
    ).first()
    
    if not old_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到评测记录: {evaluation_id}"
        )
    
    dimension_scores = old_record.dimension_scores or {}
    if not dimension_scores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原评测记录没有维度分数，无法重新评测"
        )
    
    # 构建评测请求
    company_info = CompanyInfo(
        name=company.name,
        stage=company.stage,
        industry=company.industry,
        founded_year=company.founded_year,
        employees=company.employees,
        location=company.location,
        description=company.description,
    )
    
    eval_request = SimpleEvaluationRequest(
        company=company_info,
        dimension_scores=dimension_scores,
        evaluator=old_record.evaluator,
    )
    
    try:
        result = evaluation_engine.evaluate_simple(eval_request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新评测失败: {str(e)}"
        )
    
    # 更新原记录
    old_record.total_score = result.total_score
    old_record.overall_grade = result.overall_grade
    old_record.overall_grade_label = result.overall_grade_label
    old_record.stage_weights = result.stage_weights
    old_record.strengths = result.strengths
    old_record.weaknesses = result.weaknesses
    old_record.risks = result.risks
    old_record.scoring_explanation = result.scoring_explanation
    old_record.evaluation_date = datetime.now()
    db.commit()
    db.refresh(old_record)
    
    return _create_success_response({
        "evaluation_id": old_record.evaluation_id,
        "company_id": company.id,
        "company_name": company.name,
        "total_score": result.total_score,
        "overall_grade": result.overall_grade,
        "overall_grade_label": result.overall_grade_label,
        "evaluation_date": old_record.evaluation_date.isoformat() if old_record.evaluation_date else None,
    }, message="重新评测完成")
