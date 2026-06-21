"""
评测标准路由模块
提供评测标准列表、详情、AI 深度解释、8维度概览等功能
"""

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.db import get_db
from database.models import Standard
from ai.deepseek_client import get_deepseek_client
from ai.prompts import format_standard_explain_prompt

# ============================================================
# 路由实例创建
# ============================================================

router = APIRouter(prefix="/api/v1/standards", tags=["评测标准"])

# ============================================================
# 8维度定义（用于概览接口）
# ============================================================

DIMENSION_DEFINITIONS = {
    "rd_innovation": {
        "name": "研发创新能力",
        "description": "评估企业研发体系的完整性、创新方法的先进性和技术规划的前瞻性",
        "sub_dimensions": [
            "研发投入强度", "研发管理体系", "技术路线规划", "创新方法论", "技术情报能力"
        ],
    },
    "ip_protection": {
        "name": "知识产权实力",
        "description": "评估企业知识产权布局质量、运营能力和合规水平",
        "sub_dimensions": [
            "专利布局质量", "知识产权数量", "知识产权运营", "开源合规", "商业秘密保护"
        ],
    },
    "qualification_progress": {
        "name": "资质培育进度",
        "description": "评估企业科技资质获取、规划和合规水平",
        "sub_dimensions": [
            "已获资质", "资质进阶规划", "合规性管理", "政策匹配度"
        ],
    },
    "financing_valuation": {
        "name": "融资与估值能力",
        "description": "评估企业融资历史、估值合理性和资本健康度",
        "sub_dimensions": [
            "融资历史", "估值合理性", "资本健康度", "融资准备度", "股权架构"
        ],
    },
    "legal_governance": {
        "name": "法律治理合规",
        "description": "评估企业公司治理、合同管理和合规水平",
        "sub_dimensions": [
            "公司治理", "合同管理", "劳动法合规", "数据合规", "知识产权法务"
        ],
    },
    "financial_tax": {
        "name": "财务税务能力",
        "description": "评估企业财务规范、税务筹划和成本管理水平",
        "sub_dimensions": [
            "财务规范", "税务筹划", "成本管理", "财务预测"
        ],
    },
    "ipo_readiness": {
        "name": "上市准备度",
        "description": "评估企业对资本市场的认知和上市合规基础",
        "sub_dimensions": [
            "资本市场认知", "合规基础", "中介机构", "时间规划"
        ],
    },
    "talent_resources": {
        "name": "人才资源",
        "description": "评估企业创始人团队、核心人才和组织文化建设",
        "sub_dimensions": [
            "创始人团队", "核心人才", "招聘体系", "激励机制", "组织文化"
        ],
    },
}

# ============================================================
# Pydantic 请求/响应模型
# ============================================================

class ExplainRequest(BaseModel):
    """AI 解释请求"""
    detail_level: str = Field("standard", description="详细程度: brief/standard/detailed")


# ============================================================
# 辅助函数
# ============================================================

def _create_success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
    """创建统一格式的成功响应"""
    return {"success": True, "data": data, "message": message}


# ============================================================
# 路由：标准列表（支持筛选）
# ============================================================

@router.get("")
async def list_standards(
    dimension_id: Optional[str] = None,
    importance_level: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """获取评测标准列表
    
    支持按维度ID、重要程度、关键词筛选。
    """
    query = db.query(Standard)
    
    if dimension_id:
        query = query.filter(Standard.dimension_id == dimension_id)
    
    if importance_level:
        query = query.filter(Standard.importance_level == importance_level)
    
    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            func.lower(Standard.name).like(func.lower(like_pattern))
        )
    
    total = query.count()
    standards = query.order_by(
        Standard.dimension_id,
        Standard.sub_indicator_id,
        Standard.indicator_id,
    ).offset(offset).limit(limit).all()
    
    items = []
    for s in standards:
        items.append({
            "id": s.id,
            "dimension_id": s.dimension_id,
            "sub_indicator_id": s.sub_indicator_id,
            "indicator_id": s.indicator_id,
            "name": s.name,
            "description": s.description,
            "importance_level": s.importance_level,
            "scoring_criteria_preview": (
                s.scoring_criteria[:200] + "..."
                if s.scoring_criteria and len(s.scoring_criteria) > 200
                else s.scoring_criteria
            ),
            "ai_enhanced_explanation": (
                s.ai_enhanced_explanation[:200] + "..."
                if s.ai_enhanced_explanation and len(s.ai_enhanced_explanation) > 200
                else s.ai_enhanced_explanation
            ),
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        })
    
    return _create_success_response({
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    })


# ============================================================
# 路由：标准详情
# ============================================================

@router.get("/{id}")
async def get_standard(id: int, db: Session = Depends(get_db)):
    """获取单个评测标准详情"""
    standard = db.query(Standard).filter(Standard.id == id).first()
    
    if not standard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到评测标准: ID={id}"
        )
    
    return _create_success_response({
        "id": standard.id,
        "dimension_id": standard.dimension_id,
        "sub_indicator_id": standard.sub_indicator_id,
        "indicator_id": standard.indicator_id,
        "name": standard.name,
        "description": standard.description,
        "scoring_criteria": standard.scoring_criteria,
        "scoring_examples": standard.scoring_examples,
        "ai_enhanced_explanation": standard.ai_enhanced_explanation,
        "references": standard.references,
        "importance_level": standard.importance_level,
        "created_at": standard.created_at.isoformat() if standard.created_at else None,
        "updated_at": standard.updated_at.isoformat() if standard.updated_at else None,
    })


# ============================================================
# 路由：AI 生成深度解释（带缓存）
# ============================================================

@router.post("/{id}/explain")
async def explain_standard(id: int, request: ExplainRequest, db: Session = Depends(get_db)):
    """AI 生成评测标准的深度解释
    
    如果标准表中已缓存 ai_enhanced_explanation，直接返回。
    否则调用 DeepSeek 生成并保存到数据库。
    """
    standard = db.query(Standard).filter(Standard.id == id).first()
    
    if not standard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到评测标准: ID={id}"
        )
    
    # 检查缓存
    if standard.ai_enhanced_explanation:
        return _create_success_response({
            "id": standard.id,
            "name": standard.name,
            "dimension_id": standard.dimension_id,
            "explanation": standard.ai_enhanced_explanation,
            "source": "cache",
            "detail_level": request.detail_level,
        }, message="返回缓存的解释内容")
    
    # 获取维度信息
    dim_info = DIMENSION_DEFINITIONS.get(standard.dimension_id, {})
    
    # 构建标准信息字典
    standard_info = {
        "dimension_name": dim_info.get("name", standard.dimension_id),
        "dimension_description": dim_info.get("description", ""),
        "indicator_name": standard.name,
        "indicator_description": standard.description or "",
        "scoring_criteria": standard.scoring_criteria or "",
    }
    
    # 调用 DeepSeek 生成解释
    try:
        client = get_deepseek_client()
        explain_prompt = format_standard_explain_prompt(standard_info)
        system_prompt = client.get_system_prompt("standard_explainer")
        
        ai_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": explain_prompt},
        ]
        
        # 根据详细程度调整 max_tokens
        max_tokens = {"brief": 1500, "standard": 2500, "detailed": 4000}.get(
            request.detail_level, 2500
        )
        
        resp = await client.chat(ai_messages, temperature=0.7, max_tokens=max_tokens)
        explanation = resp["choices"][0]["message"]["content"]
        
        # 保存到缓存
        standard.ai_enhanced_explanation = explanation
        db.commit()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 解释生成失败: {str(e)}"
        )
    
    return _create_success_response({
        "id": standard.id,
        "name": standard.name,
        "dimension_id": standard.dimension_id,
        "explanation": explanation,
        "source": "ai_generated",
        "detail_level": request.detail_level,
    }, message="AI 解释生成成功并缓存")


# ============================================================
# 路由：8维度概览
# ============================================================

@router.get("/dimensions/summary")
async def get_dimensions_summary(db: Session = Depends(get_db)):
    """获取8维度评测概览
    
    返回每个维度的定义、指标数量和重要程度分布。
    """
    # 统计每个维度的指标数量
    stats = db.query(
        Standard.dimension_id,
        func.count(Standard.id).label("indicator_count"),
        func.count(func.distinct(Standard.sub_indicator_id)).label("sub_indicator_count"),
    ).group_by(Standard.dimension_id).all()
    
    # 统计重要程度分布
    importance_stats = db.query(
        Standard.dimension_id,
        Standard.importance_level,
        func.count(Standard.id).label("count"),
    ).group_by(Standard.dimension_id, Standard.importance_level).all()
    
    # 构建重要程度分布字典
    importance_map: Dict[str, Dict[str, int]] = {}
    for dim_id, level, cnt in importance_stats:
        if dim_id not in importance_map:
            importance_map[dim_id] = {}
        importance_map[dim_id][level or "unknown"] = cnt
    
    # 组装结果
    dimensions = []
    for dim_id, info in DIMENSION_DEFINITIONS.items():
        stat = next((s for s in stats if s[0] == dim_id), None)
        indicator_count = stat[1] if stat else 0
        sub_indicator_count = stat[2] if stat else 0
        
        dimensions.append({
            "dimension_id": dim_id,
            "name": info["name"],
            "description": info["description"],
            "sub_dimensions": info["sub_dimensions"],
            "indicator_count": indicator_count,
            "sub_indicator_count": sub_indicator_count,
            "importance_distribution": importance_map.get(dim_id, {}),
        })
    
    # 计算总计
    total_indicators = sum(d["indicator_count"] for d in dimensions)
    
    return _create_success_response({
        "dimensions": dimensions,
        "total_dimensions": len(dimensions),
        "total_indicators": total_indicators,
    })
