from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base


class Company(Base):
    """企业信息表"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="企业名称")
    industry = Column(String(100), comment="所属行业")
    stage = Column(String(50), nullable=False, comment="发展阶段")  # seed/angel/pre-a/a-round
    founded_year = Column(Integer, comment="成立年份")
    employees = Column(Integer, comment="员工人数")
    location = Column(String(200), comment="所在地区")
    description = Column(Text, comment="企业简介")
    tech_direction = Column(String(500), comment="核心技术方向")
    qualifications = Column(JSON, default=list, comment="已获资质列表")
    funding_status = Column(String(100), comment="融资状态")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联：一家企业可有多条评测记录和多个文档，级联删除
    evaluations = relationship(
        "EvaluationRecord", back_populates="company", cascade="all, delete-orphan"
    )
    documents = relationship(
        "Document", back_populates="company", cascade="all, delete-orphan"
    )


class EvaluationRecord(Base):
    """评测记录表"""
    __tablename__ = "evaluation_records"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(
        Integer, ForeignKey("companies.id"), nullable=False, comment="所属企业ID"
    )
    evaluation_id = Column(
        String(100), unique=True, index=True, comment="评测唯一编号"
    )  # UUID
    dimension_scores = Column(
        JSON, default=dict, comment="各维度评分"
    )  # {dim_id: score}
    total_score = Column(Float, comment="综合总分")
    overall_grade = Column(String(10), comment="综合等级")  # A/B/C/D/E
    overall_grade_label = Column(String(20), comment="综合等级标签")  # 优秀/良好/合格/关注/风险
    stage_weights = Column(
        JSON, default=dict, comment="阶段权重配置"
    )  # {dim_id: weight}
    strengths = Column(JSON, default=list, comment="优势项列表")
    weaknesses = Column(JSON, default=list, comment="劣势项列表")
    risks = Column(JSON, default=list, comment="风险点列表")
    ai_diagnosis = Column(Text, comment="AI深度诊断报告内容")
    scoring_explanation = Column(Text, comment="评分说明")
    evaluator = Column(String(200), comment="评测人/机构")
    evaluation_date = Column(
        DateTime, default=datetime.now, comment="评测日期"
    )
    created_at = Column(DateTime, default=datetime.now, comment="记录创建时间")
    
    # 反向关联：评测记录属于一家企业
    company = relationship("Company", back_populates="evaluations")


class Conversation(Base):
    """AI评测助手对话记录表"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        String(100), unique=True, index=True, comment="会话唯一编号"
    )  # UUID
    title = Column(
        String(200), comment="对话标题（如：企业名+时间）"
    )
    messages = Column(
        JSON, default=list, comment="对话消息列表"
    )  # [{role, content, timestamp}]
    current_task = Column(
        String(50), default="chat", comment="当前任务类型"
    )  # chat/research/report/review
    status = Column(
        String(50), default="active", comment="会话状态"
    )  # active/complete/error
    generated_report = Column(Text, comment="AI生成的调研报告全文")
    extracted_scores = Column(
        JSON, default=dict, comment="从报告提取的8维度分数"
    )  # {dim_id: score}
    company_info = Column(
        JSON, default=dict, comment="企业基本信息快照"
    )  # {name, industry, stage...}
    documents = Column(
        JSON, default=list, comment="关联文档ID列表"
    )
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )


class Document(Base):
    """上传文档表"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(
        Integer, ForeignKey("companies.id"), nullable=True, comment="所属企业ID"
    )
    conversation_id = Column(
        Integer, ForeignKey("conversations.id"), nullable=True, comment="所属会话ID"
    )
    filename = Column(String(500), nullable=False, comment="文件名")
    original_path = Column(String(1000), comment="原始存储路径")
    file_type = Column(
        String(50), comment="文件类型"
    )  # pdf/docx/xlsx/txt/md
    file_size = Column(Integer, comment="文件大小（字节）")
    parsed_text = Column(Text, comment="解析后的纯文本内容")
    parsed_summary = Column(Text, comment="文本摘要（前500字）")
    status = Column(
        String(50), default="pending", comment="解析状态"
    )  # pending/parsing/parsed/error
    upload_date = Column(DateTime, default=datetime.now, comment="上传时间")
    
    # 反向关联：文档归属企业（可为空，表示仅属于会话）
    company = relationship("Company", back_populates="documents")


class KnowledgeDoc(Base):
    """知识库文档表（法规、政策、研报、白皮书等）"""
    __tablename__ = "knowledge_docs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, comment="文档标题")
    doc_type = Column(
        String(50), nullable=False, comment="文档类型"
    )  # law/policy/report/standard/whitepaper
    category = Column(String(100), comment="细分分类")
    content = Column(Text, nullable=False, comment="完整内容")
    content_summary = Column(Text, comment="内容摘要")
    source_url = Column(String(1000), comment="来源链接")
    tags = Column(JSON, default=list, comment="标签列表")
    is_active = Column(
        Boolean, default=True, comment="是否启用"
    )
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )


class Standard(Base):
    """评测标准解释表（8维度55指标详细说明）"""
    __tablename__ = "standards"
    
    id = Column(Integer, primary_key=True, index=True)
    dimension_id = Column(
        String(100), nullable=False, index=True, comment="维度标识"
    )  # rd_innovation等
    sub_indicator_id = Column(
        String(100), nullable=True, comment="二级指标标识"
    )
    indicator_id = Column(
        String(100), nullable=True, comment="三级指标标识"
    )
    name = Column(String(200), nullable=False, comment="指标名称")
    description = Column(Text, comment="指标说明")
    scoring_criteria = Column(
        Text, comment="评分标准详细说明"
    )  # 各等级对应的判定条件
    scoring_examples = Column(
        Text, comment="评分示例"
    )  # 实际企业的评分示例
    ai_enhanced_explanation = Column(
        Text, comment="AI增强的深度解释"
    )  # 由AI生成的通俗解释
    references = Column(
        JSON, default=list, comment="参考法规/文献列表"
    )
    importance_level = Column(
        String(20), comment="重要程度"
    )  # high/medium/low
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )
