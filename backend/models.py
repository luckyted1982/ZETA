from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# ============================================================
# 企业基本信息模型
# ============================================================

class CompanyInfo(BaseModel):
    """企业基本信息"""
    name: str = Field(..., description="企业名称", min_length=1, max_length=200)
    stage: str = Field(..., description="发展阶段", pattern="^(seed|angel|pre-a|a-round)$")
    industry: Optional[str] = Field(None, description="所属行业")
    founded_year: Optional[int] = Field(None, description="成立年份", ge=1990, le=2030)
    employees: Optional[int] = Field(None, description="员工人数", ge=0)
    location: Optional[str] = Field(None, description="所在地区")
    description: Optional[str] = Field(None, description="企业简介", max_length=2000)
    
    @field_validator('stage')
    @classmethod
    def validate_stage(cls, v):
        """验证发展阶段是否合法"""
        valid_stages = ['seed', 'angel', 'pre-a', 'a-round']
        if v not in valid_stages:
            raise ValueError(f"stage必须是以下之一: {', '.join(valid_stages)}")
        return v


# ============================================================
# 三级指标评分输入模型
# ============================================================

class IndicatorItemInput(BaseModel):
    """单个三级指标评分输入"""
    indicator_id: str = Field(..., description="指标唯一标识")
    score: Optional[float] = Field(None, description="评分(0-100)", ge=0, le=100)
    evidence: Optional[str] = Field(None, description="评分依据/证据材料")
    notes: Optional[str] = Field(None, description="备注说明")


class SubIndicatorInput(BaseModel):
    """二级指标输入（包含多个三级指标）"""
    sub_indicator_id: str = Field(..., description="二级指标ID")
    items: List[IndicatorItemInput] = Field(default_factory=list, description="三级指标评分列表")
    notes: Optional[str] = Field(None, description="备注")


class DimensionInput(BaseModel):
    """一级维度输入数据"""
    dimension_id: str = Field(..., description="维度ID")
    sub_indicators: List[SubIndicatorInput] = Field(default_factory=list, description="二级指标评分数据")
    notes: Optional[str] = Field(None, description="维度备注")


class EvaluationRequest(BaseModel):
    """评测请求模型"""
    company: CompanyInfo = Field(..., description="企业基本信息")
    dimensions: List[DimensionInput] = Field(default_factory=list, description="各维度评测数据")
    evaluator: Optional[str] = Field(None, description="评测人")
    evaluation_date: Optional[datetime] = Field(None, description="评测日期")


# ============================================================
# 三级指标评分结果模型
# ============================================================

class IndicatorItemScore(BaseModel):
    """单个三级指标评分结果"""
    indicator_id: str = Field(..., description="指标唯一标识")
    name: str = Field(..., description="指标名称")
    score: float = Field(..., description="评分(0-100)", ge=0, le=100)
    max_score: float = Field(100, description="满分")
    evidence: Optional[str] = Field(None, description="评分依据")
    notes: Optional[str] = Field(None, description="备注")
    is_default: bool = Field(False, description="是否为默认值（数据缺失时使用）")


class SubIndicatorScore(BaseModel):
    """二级指标评分结果"""
    sub_indicator_id: str = Field(..., description="二级指标ID")
    name: str = Field(..., description="二级指标名称")
    weight: float = Field(..., description="在维度内的权重", ge=0, le=1)
    score: float = Field(..., description="得分(0-100)", ge=0, le=100)
    raw_score: float = Field(..., description="原始平均分")
    item_count: int = Field(..., description="有效评分项数量")
    default_count: int = Field(0, description="使用默认值的项数量")
    items: List[IndicatorItemScore] = Field(default_factory=list, description="三级指标详情")
    notes: Optional[str] = Field(None, description="备注")


class DimensionScore(BaseModel):
    """一级维度评分结果"""
    dimension_id: str = Field(..., description="维度ID")
    name: str = Field(..., description="维度名称")
    weight: float = Field(..., description="阶段权重", ge=0, le=1)
    score: float = Field(..., description="加权得分(0-100)", ge=0, le=100)
    raw_score: float = Field(..., description="原始平均分")
    sub_indicators: List[SubIndicatorScore] = Field(default_factory=list, description="二级指标详情")
    grade: str = Field(..., description="评级")
    grade_label: str = Field(..., description="评级标签")
    benchmark: Optional[float] = Field(None, description="同阶段基准值")
    gap: Optional[float] = Field(None, description="与基准的差距")


# ============================================================
# 评测结果与报告模型
# ============================================================

class GradeSummary(BaseModel):
    """等级分布摘要"""
    grade: str = Field(..., description="等级代码")
    label: str = Field(..., description="等级名称")
    min_score: int = Field(..., description="最低分")
    max_score: int = Field(..., description="最高分")
    description: str = Field(..., description="等级说明")


class EvaluationResult(BaseModel):
    """完整评测结果"""
    evaluation_id: str = Field(..., description="评测唯一ID")
    company: CompanyInfo = Field(..., description="企业信息")
    total_score: float = Field(..., description="综合得分(0-100)", ge=0, le=100)
    overall_grade: str = Field(..., description="综合评级")
    overall_grade_label: str = Field(..., description="综合评级标签")
    stage_weights: Dict[str, float] = Field(default_factory=dict, description="使用的阶段权重")
    dimensions: List[DimensionScore] = Field(default_factory=list, description="维度得分详情")
    strengths: List[str] = Field(default_factory=list, description="优势维度")
    weaknesses: List[str] = Field(default_factory=list, description="劣势维度")
    risks: List[str] = Field(default_factory=list, description="风险预警")
    evaluator: Optional[str] = Field(None, description="评测人")
    evaluation_date: datetime = Field(default_factory=datetime.now, description="评测时间")
    scoring_explanation: str = Field("", description="评分逻辑说明")


class AIDiagnosisReport(BaseModel):
    """AI深度诊断报告"""
    diagnosis_id: str = Field(..., description="诊断ID")
    evaluation_id: str = Field(..., description="关联评测ID")
    company_name: str = Field(..., description="企业名称")
    stage: str = Field(..., description="发展阶段")
    total_score: float = Field(..., description="综合得分")
    overall_grade: str = Field(..., description="综合评级")
    report_content: str = Field(..., description="完整诊断报告内容")
    strengths_analysis: List[str] = Field(default_factory=list, description="优势分析")
    weaknesses_analysis: List[str] = Field(default_factory=list, description="劣势分析")
    risk_warnings: List[str] = Field(default_factory=list, description="风险预警")
    improvement_roadmap: List[str] = Field(default_factory=list, description="改进路线图")
    service_recommendations: List[str] = Field(default_factory=list, description="服务推荐")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")
    model_used: str = Field("deepseek-chat", description="使用的AI模型")


# ============================================================
# 基准数据与维度定义模型
# ============================================================

class BenchmarkData(BaseModel):
    """同阶段基准数据"""
    stage: str = Field(..., description="发展阶段")
    dimension_id: str = Field(..., description="维度ID")
    dimension_name: str = Field(..., description="维度名称")
    avg_score: float = Field(..., description="平均得分")
    p75_score: float = Field(..., description="75分位得分")
    p90_score: float = Field(..., description="90分位得分")
    sample_size: int = Field(..., description="样本量")


class StageDefinition(BaseModel):
    """发展阶段定义"""
    stage_id: str = Field(..., description="阶段ID")
    name: str = Field(..., description="阶段名称")
    description: str = Field(..., description="阶段描述")
    weights: Dict[str, float] = Field(default_factory=dict, description="维度权重")
    characteristics: List[str] = Field(default_factory=list, description="阶段特征")


class IndicatorDefinition(BaseModel):
    """三级指标定义"""
    indicator_id: str = Field(..., description="指标ID")
    name: str = Field(..., description="指标名称")
    description: str = Field(..., description="指标说明")
    scoring_criteria: str = Field(..., description="评分标准")
    default_score: float = Field(50.0, description="数据缺失时的默认得分")
    data_sources: List[str] = Field(default_factory=list, description="数据来源建议")


class SubIndicatorDefinition(BaseModel):
    """二级指标定义"""
    sub_indicator_id: str = Field(..., description="二级指标ID")
    name: str = Field(..., description="指标名称")
    weight: float = Field(..., description="在维度内的权重", ge=0, le=1)
    description: str = Field(..., description="指标说明")
    indicators: List[IndicatorDefinition] = Field(default_factory=list, description="三级指标列表")


class DimensionDefinition(BaseModel):
    """一级维度定义"""
    dimension_id: str = Field(..., description="维度ID")
    name: str = Field(..., description="维度名称")
    description: str = Field(..., description="维度说明")
    sub_indicators: List[SubIndicatorDefinition] = Field(default_factory=list, description="二级指标列表")


# ============================================================
# 简化评测请求模型（每个维度一个总分数）
# ============================================================

class SimpleEvaluationRequest(BaseModel):
    """简化评测请求：每个维度提供一个总分数，自动分配到所有三级指标"""
    company: CompanyInfo = Field(..., description="企业基本信息")
    dimension_scores: Dict[str, float] = Field(
        default_factory=dict, 
        description="各维度总分数，如 {'rd_innovation': 75.0}，范围0-100"
    )
    evaluator: Optional[str] = Field(None, description="评测人")
    
    @field_validator('dimension_scores')
    @classmethod
    def validate_scores(cls, v):
        """验证分数在0-100范围内"""
        for dim_id, score in v.items():
            if score < 0 or score > 100:
                raise ValueError(f"维度 {dim_id} 的分数 {score} 超出范围，必须在 0-100 之间")
        return v

class EvaluationResponse(BaseModel):
    """评测接口响应"""
    success: bool = Field(True, description="是否成功")
    data: Optional[EvaluationResult] = Field(None, description="评测结果")
    message: str = Field("操作成功", description="提示信息")


class AIDiagnosisResponse(BaseModel):
    """AI诊断接口响应"""
    success: bool = Field(True, description="是否成功")
    data: Optional[AIDiagnosisReport] = Field(None, description="诊断报告")
    message: str = Field("操作成功", description="提示信息")


class DimensionsResponse(BaseModel):
    """维度定义接口响应"""
    success: bool = Field(True, description="是否成功")
    data: List[DimensionDefinition] = Field(default_factory=list, description="维度定义列表")
    message: str = Field("操作成功", description="提示信息")


class StagesResponse(BaseModel):
    """发展阶段接口响应"""
    success: bool = Field(True, description="是否成功")
    data: List[StageDefinition] = Field(default_factory=list, description="阶段定义列表")
    message: str = Field("操作成功", description="提示信息")


class BenchmarksResponse(BaseModel):
    """基准数据接口响应"""
    success: bool = Field(True, description="是否成功")
    data: List[BenchmarkData] = Field(default_factory=list, description="基准数据列表")
    message: str = Field("操作成功", description="提示信息")
