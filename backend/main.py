from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json
import httpx

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import get_settings
from evaluation_engine import EvaluationEngine, STAGE_WEIGHTS, EVALUATION_INDICATORS, BENCHMARK_DATA
from models import (
    EvaluationRequest, EvaluationResponse, EvaluationResult,
    AIDiagnosisResponse, AIDiagnosisReport, DimensionsResponse,
    StagesResponse, BenchmarksResponse, DimensionDefinition,
    SubIndicatorDefinition, IndicatorDefinition, BenchmarkData,
    StageDefinition, GradeSummary, SimpleEvaluationRequest
)

# ============================================================
# 数据库初始化与路由导入
# ============================================================
from database.db import init_db
from routers import ai_assistant, companies, knowledge_base, standards

# ============================================================
# FastAPI 应用实例创建
# ============================================================

app = FastAPI(
    title="AI驱动的科创企业评测系统",
    description="为科创企业提供多维度评测、AI深度诊断和基准对比服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置跨域资源共享（CORS），允许前端应用访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 启动事件：初始化数据库
# ============================================================

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库表结构"""
    init_db()

# ============================================================
# 注册路由模块
# ============================================================

app.include_router(ai_assistant.router)
app.include_router(companies.router)
app.include_router(knowledge_base.router)
app.include_router(standards.router)

# 初始化评测引擎（全局单例）
evaluation_engine = EvaluationEngine()

# DeepSeek API 配置（懒加载）
_deepseek_client: Optional[httpx.AsyncClient] = None


def get_deepseek_client() -> httpx.AsyncClient:
    """获取DeepSeek API客户端（单例模式）"""
    global _deepseek_client
    if _deepseek_client is None:
        settings = get_settings()
        _deepseek_client = httpx.AsyncClient(
            base_url=settings.DEEPSEEK_BASE_URL,
            headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
            timeout=60.0,
        )
    return _deepseek_client


# ============================================================
# 健康检查接口
# ============================================================

@app.get("/health", tags=["系统"])
async def health_check():
    """系统健康检查接口"""
    return {
        "status": "healthy",
        "service": "ai-evaluation-platform",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/", tags=["系统"])
async def root():
    """API根路径，返回服务基本信息"""
    return {
        "name": "AI驱动的科创企业评测系统",
        "version": "1.0.0",
        "docs": "/docs",
    }


# ============================================================
# 评测接口（简化版）
# ============================================================

@app.post("/api/v1/evaluate-simple", response_model=EvaluationResponse, tags=["评测"])
async def evaluate_company_simple(request: SimpleEvaluationRequest):
    """简化版评测接口：每个维度提供一个总分数
    
    接收企业基本信息和8个维度的总分数，自动将分数分配到
    该维度下的所有三级指标，然后执行完整评测。
    
    Args:
        request: 简化评测请求，包含 company 和 dimension_scores
        
    Returns:
        完整评测结果
    """
    try:
        # 验证至少有一个维度评分
        if not request.dimension_scores:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请至少为一个维度评分"
            )
        
        # 验证企业阶段合法性
        valid_stages = ['seed', 'angel', 'pre-a', 'a-round']
        if request.company.stage not in valid_stages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的发展阶段: {request.company.stage}"
            )
        
        # 执行简化评测
        result = evaluation_engine.evaluate_simple(request)
        
        # 保存评测结果
        evaluation_engine.save_evaluation(result)
        
        return EvaluationResponse(
            success=True,
            data=result,
            message="评测完成"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评测过程中发生错误: {str(e)}"
        )


# ============================================================
# 评测接口（完整版）
# ============================================================

@app.post("/api/v1/evaluate", response_model=EvaluationResponse, tags=["评测"])
async def evaluate_company(request: EvaluationRequest):
    """提交评测问卷，返回评测结果
    
    接收企业基本信息和各维度评测数据，执行完整评测计算：
    - 验证企业阶段合法性
    - 根据发展阶段应用对应的权重
    - 计算各维度得分（支持空值处理，使用默认值）
    - 计算综合得分和等级
    - 对比同阶段基准数据
    - 识别优势、劣势和风险
    
    Args:
        request: 评测请求，包含企业信息和各维度评分数据
        
    Returns:
        完整评测结果
    """
    try:
        # 执行评测计算
        result = evaluation_engine.evaluate(request)
        
        # 保存评测结果（内存存储，生产环境应持久化到数据库）
        evaluation_engine.save_evaluation(result)
        
        return EvaluationResponse(
            success=True,
            data=result,
            message="评测完成"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评测过程中发生错误: {str(e)}"
        )


# ============================================================
# AI深度诊断接口
# ============================================================

async def generate_ai_diagnosis(evaluation: EvaluationResult) -> AIDiagnosisReport:
    """基于评测结果生成AI深度诊断报告
    
    调用DeepSeek API生成个性化诊断报告，包含：
    - 优势分析
    - 劣势分析
    - 风险预警
    - 改进路线图
    - 服务推荐
    
    Args:
        evaluation: 评测结果
        
    Returns:
        AI诊断报告
    """
    settings = get_settings()
    
    # 构建详细的诊断prompt
    prompt = _build_diagnosis_prompt(evaluation)
    
    # 调用DeepSeek API
    try:
        client = get_deepseek_client()
        
        # 构建请求体
        request_body = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是一位资深的科创企业咨询顾问，专注于为科技创新企业提供深度诊断和战略建议。"
                        "你需要基于评测数据，生成专业、客观、可执行的诊断报告。"
                        "报告要求：语言专业严谨，分析深入透彻，建议具体可行，字数控制在5000字以内。"
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4000,
        }
        
        response = await client.post("/chat/completions", json=request_body)
        response_data = response.json()
        
        if response.status_code != 200:
            error_msg = response_data.get("error", {}).get("message", "未知错误")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"DeepSeek API调用失败: {error_msg}"
            )
        
        # 解析AI生成的报告内容
        report_content = response_data["choices"][0]["message"]["content"]
        
        # 解析报告中的结构化信息（使用简单的启发式解析）
        strengths_analysis, weaknesses_analysis, risk_warnings, improvement_roadmap, service_recommendations = \
            _parse_diagnosis_report(report_content)
        
        return AIDiagnosisReport(
            diagnosis_id=str(uuid.uuid4()),
            evaluation_id=evaluation.evaluation_id,
            company_name=evaluation.company.name,
            stage=evaluation.company.stage,
            total_score=evaluation.total_score,
            overall_grade=evaluation.overall_grade,
            report_content=report_content,
            strengths_analysis=strengths_analysis,
            weaknesses_analysis=weaknesses_analysis,
            risk_warnings=risk_warnings,
            improvement_roadmap=improvement_roadmap,
            service_recommendations=service_recommendations,
            model_used="deepseek-chat"
        )
        
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"无法连接到DeepSeek API: {str(e)}"
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI诊断生成失败: {str(e)}"
        )


def _build_diagnosis_prompt(evaluation: EvaluationResult) -> str:
    """构建AI诊断的详细prompt
    
    包含评测数据、同阶段基准、改进建议框架等完整信息。
    """
    company = evaluation.company
    
    # 构建维度得分明细
    dimension_details = []
    for dim in evaluation.dimensions:
        benchmark = dim.benchmark if dim.benchmark is not None else "无数据"
        gap = f"{dim.gap:+.1f}" if dim.gap is not None else "无数据"
        dimension_details.append(
            f"\n【{dim.name}】得分: {dim.score}分，评级: {dim.grade}({dim.grade_label})，"
            f"权重: {dim.weight:.0%}，同阶段基准: {benchmark}，差距: {gap}"
        )
        
        # 添加二级指标详情
        for sub in dim.sub_indicators:
            default_info = f"（其中{sub.default_count}项使用默认值）" if sub.default_count > 0 else ""
            dimension_details.append(
                f"  - {sub.name}: {sub.score}分 {default_info}"
            )
    
    prompt = f"""请为以下科创企业生成深度诊断报告。

## 企业基本信息
- 企业名称: {company.name}
- 发展阶段: {company.stage}
- 行业: {company.industry or "未提供"}
- 成立年份: {company.founded_year or "未提供"}
- 员工人数: {company.employees or "未提供"}
- 所在地区: {company.location or "未提供"}
- 企业简介: {company.description or "未提供"}

## 评测结果概览
- 综合得分: {evaluation.total_score}分
- 综合评级: {evaluation.overall_grade}({evaluation.overall_grade_label})
- 评测时间: {evaluation.evaluation_date.strftime("%Y-%m-%d %H:%M")}

## 各维度评测详情
{''.join(dimension_details)}

## 优势维度
{chr(10).join([f"- {s}" for s in evaluation.strengths]) or "暂无显著优势"}

## 劣势维度
{chr(10).join([f"- {s}" for s in evaluation.weaknesses]) or "暂无显著劣势"}

## 风险预警
{chr(10).join([f"- {r}" for r in evaluation.risks]) or "暂无重大风险"}

## 报告要求
请生成一份完整的深度诊断报告，包含以下部分：

1. **执行摘要**（300字以内）：对企业的整体评价和核心结论

2. **优势分析**：
   - 详细分析企业的核心优势
   - 说明这些优势如何转化为竞争壁垒
   - 建议如何进一步强化优势

3. **劣势分析**：
   - 深入剖析存在的主要短板
   - 分析短板形成的原因
   - 评估短板对发展的影响程度

4. **风险预警**：
   - 识别潜在的法律风险、财务风险、经营风险
   - 评估风险发生的可能性和影响
   - 提出风险应对预案

5. **改进路线图**：
   - 短期（3个月）：紧急需要改进的事项
   - 中期（6-12个月）：系统性改进计划
   - 长期（1-3年）：战略性能力建设
   - 每项改进建议需明确：目标、措施、责任方、验收标准

6. **服务推荐**：
   - 基于评测结果，推荐企业需要的外部专业服务
   - 如：知识产权代理、财税咨询、法律顾问、融资顾问、政策申报等
   - 说明每项服务的紧迫程度和预期价值

7. **总结与展望**：
   - 对企业发展前景的整体判断
   - 关键成功因素
   - 下一阶段重点关注事项

请确保报告内容专业、客观、具体，避免空泛的建议。使用专业术语但保持可读性。字数控制在5000字以内。
"""
    return prompt


def _parse_diagnosis_report(report_content: str) -> tuple:
    """解析AI生成的诊断报告，提取结构化信息
    
    使用简单的启发式解析，将报告内容拆分为结构化数据。
    """
    lines = report_content.split('\n')
    
    strengths = []
    weaknesses = []
    risks = []
    roadmap = []
    services = []
    
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 识别章节标题
        lower_line = line.lower()
        if '优势' in line or 'strength' in lower_line:
            current_section = 'strengths'
            continue
        elif '劣势' in line or 'weakness' in lower_line or '短板' in line:
            current_section = 'weaknesses'
            continue
        elif '风险' in line or 'risk' in lower_line:
            current_section = 'risks'
            continue
        elif '改进' in line or 'roadmap' in lower_line or '路线' in line:
            current_section = 'roadmap'
            continue
        elif '服务' in line or 'service' in lower_line or '推荐' in line:
            current_section = 'services'
            continue
        elif '摘要' in line or '总结' in line or '结论' in line:
            current_section = None
            continue
        
        # 收集列表项（以 - 或 数字 开头的行）
        if line.startswith('-') or line.startswith('•') or line[0:2].strip('.').isdigit():
            item = line.lstrip('- •').strip()
            if item and len(item) > 10:
                if current_section == 'strengths':
                    strengths.append(item)
                elif current_section == 'weaknesses':
                    weaknesses.append(item)
                elif current_section == 'risks':
                    risks.append(item)
                elif current_section == 'roadmap':
                    roadmap.append(item)
                elif current_section == 'services':
                    services.append(item)
    
    # 如果解析结果为空，返回默认提示
    if not strengths:
        strengths = ["详见报告正文优势分析部分"]
    if not weaknesses:
        weaknesses = ["详见报告正文劣势分析部分"]
    if not risks:
        risks = ["详见报告正文风险预警部分"]
    if not roadmap:
        roadmap = ["详见报告正文改进路线图部分"]
    if not services:
        services = ["详见报告正文服务推荐部分"]
    
    return strengths, weaknesses, risks, roadmap, services


@app.post("/api/v1/evaluate/{evaluation_id}/ai-diagnosis", response_model=AIDiagnosisResponse, tags=["AI诊断"])
async def generate_ai_diagnosis_endpoint(evaluation_id: str):
    """基于评测结果生成AI深度诊断报告
    
    接收评测ID，获取已保存的评测结果，调用DeepSeek API生成
    个性化深度诊断报告（5000字以内）。
    
    Args:
        evaluation_id: 评测ID
        
    Returns:
        AI深度诊断报告，包含：
        - 优势分析
        - 劣势分析
        - 风险预警
        - 改进路线图
        - 服务推荐
    """
    # 获取已保存的评测结果
    evaluation = evaluation_engine.get_evaluation(evaluation_id)
    if evaluation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到评测结果: {evaluation_id}"
        )
    
    try:
        # 生成AI诊断报告
        diagnosis = await generate_ai_diagnosis(evaluation)
        
        return AIDiagnosisResponse(
            success=True,
            data=diagnosis,
            message="AI诊断报告生成成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI诊断生成失败: {str(e)}"
        )


# ============================================================
# 评测结果查询接口
# ============================================================

@app.get("/api/v1/evaluation/{evaluation_id}", response_model=EvaluationResponse, tags=["评测"])
async def get_evaluation_result(evaluation_id: str):
    """获取已保存的评测结果
    
    Args:
        evaluation_id: 评测ID
        
    Returns:
        评测结果
    """
    evaluation = evaluation_engine.get_evaluation(evaluation_id)
    if evaluation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到评测结果: {evaluation_id}"
        )
    
    return EvaluationResponse(
        success=True,
        data=evaluation,
        message="查询成功"
    )


# ============================================================
# 维度定义接口
# ============================================================

@app.get("/api/v1/dimensions", response_model=DimensionsResponse, tags=["元数据"])
async def get_dimensions():
    """获取所有评测维度定义
    
    返回8个一级维度的完整定义，包括：
    - 维度名称和描述
    - 二级指标列表（含权重）
    - 三级指标列表（含评分标准）
    
    Returns:
        维度定义列表
    """
    dim_definitions = evaluation_engine.get_dimension_definitions()
    
    # 转换为Pydantic模型
    result = []
    for dim in dim_definitions:
        sub_indicators = []
        for sub in dim["sub_indicators"]:
            indicators = []
            for ind in sub["indicators"]:
                indicators.append(IndicatorDefinition(
                    indicator_id=ind["indicator_id"],
                    name=ind["name"],
                    description=ind.get("scoring_criteria", ""),
                    scoring_criteria=ind.get("scoring_criteria", ""),
                    default_score=ind.get("default_score", 50.0),
                    data_sources=[]
                ))
            sub_indicators.append(SubIndicatorDefinition(
                sub_indicator_id=sub["sub_indicator_id"],
                name=sub["name"],
                weight=sub["weight"],
                description=sub.get("description", ""),
                indicators=indicators
            ))
        result.append(DimensionDefinition(
            dimension_id=dim["dimension_id"],
            name=dim["name"],
            description=dim.get("description", ""),
            sub_indicators=sub_indicators
        ))
    
    return DimensionsResponse(
        success=True,
        data=result,
        message="查询成功"
    )


# ============================================================
# 发展阶段接口
# ============================================================

@app.get("/api/v1/stages", response_model=StagesResponse, tags=["元数据"])
async def get_stages():
    """获取发展阶段定义和权重
    
    返回4个发展阶段（种子/天使/Pre-A/A轮）的：
    - 阶段名称和描述
    - 各维度权重配置
    - 阶段特征
    
    Returns:
        阶段定义列表
    """
    stage_definitions = evaluation_engine.get_stage_definitions()
    
    result = []
    for stage in stage_definitions:
        result.append(StageDefinition(
            stage_id=stage["stage_id"],
            name=stage["name"],
            description=stage["description"],
            weights=stage["weights"],
            characteristics=stage["characteristics"]
        ))
    
    return StagesResponse(
        success=True,
        data=result,
        message="查询成功"
    )


# ============================================================
# 基准数据接口
# ============================================================

@app.get("/api/v1/benchmarks", response_model=BenchmarksResponse, tags=["元数据"])
async def get_benchmarks(stage: Optional[str] = None):
    """获取同阶段企业基准数据
    
    Args:
        stage: 可选，指定发展阶段筛选基准数据
               如不指定，返回所有阶段的基准数据
        
    Returns:
        基准数据列表
    """
    if stage:
        benchmarks = evaluation_engine.get_benchmarks(stage)
    else:
        benchmarks = evaluation_engine.get_all_benchmarks()
    
    # 转换为Pydantic模型
    result = []
    for bm in benchmarks:
        result.append(BenchmarkData(
            stage=bm["stage"],
            dimension_id=bm["dimension_id"],
            dimension_name=bm["dimension_name"],
            avg_score=bm["avg_score"],
            p75_score=bm["p75_score"],
            p90_score=bm["p90_score"],
            sample_size=bm["sample_size"]
        ))
    
    return BenchmarksResponse(
        success=True,
        data=result,
        message="查询成功"
    )


# ============================================================
# 全局异常处理
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """处理HTTP异常，返回统一格式的错误响应"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "data": None,
            "message": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """处理通用异常，返回统一格式的错误响应"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "data": None,
            "message": f"服务器内部错误: {str(exc)}"
        }
    )


# ============================================================
# 应用启动入口
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )
