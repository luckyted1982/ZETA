"""
AI Prompt 模板库
所有 Prompt 使用中文，针对 8 维度 55 指标评测体系设计
"""

# =============== 调研报告生成 ===============

RESEARCH_REPORT_PROMPT = """请为以下科创企业生成一份深度调研报告。

## 企业信息
- 企业名称: {company_name}
- 所属行业: {industry}
- 发展阶段: {stage}
- 核心技术方向: {tech_direction}
- 企业简介: {description}

## 任务要求
请基于公开信息和行业知识，生成一份包含以下 8 个维度的深度调研报告：

1. **研发创新能力**（研发投入、管理体系、技术路线、创新方法论、情报能力）
2. **知识产权实力**（专利布局、知识产权数量、运营、开源合规、商业秘密）
3. **资质培育进度**（已获资质、进阶规划、合规性、政策匹配）
4. **融资与估值能力**（融资历史、估值合理性、资本健康度、融资准备度、股权架构）
5. **法律治理合规**（公司治理、合同管理、劳动法合规、数据合规、知识产权法务）
6. **财务税务能力**（财务规范、税务筹划、成本管理、财务预测）
7. **上市准备度**（资本市场认知、合规基础、中介机构、时间规划）
8. **人才资源**（创始人团队、核心人才、招聘体系、激励机制、组织文化）

每个维度请包含：
- 现状分析（基于企业信息的合理推断）
- 与同阶段企业的对比
- 关键风险点
- 改进建议

最后，请在报告末尾**严格按以下纯文本格式**输出8维度评分表（每个维度0-100分，不要使用Markdown表格，使用纯文本格式）：

【8 维度评分】
研发创新能力: 75 分
知识产权实力: 80 分
资质培育进度: 65 分
融资与估值能力: 90 分
法律治理合规: 70 分
财务税务能力: 60 分
上市准备度: 85 分
人才资源: 75 分

注意：
1. 必须使用纯文本格式，不要输出Markdown表格
2. 每个维度必须有明确的数字分数
3. 格式统一为"维度名称: 数字 分"（冒号后有空格，数字后有空格和"分"字）
4. 不要省略任何维度的评分
请确保报告专业、客观、有深度，总字数控制在 3000-5000 字。
"""

# =============== 文档解析 ===============

DOCUMENT_ANALYSIS_PROMPT = """请分析以下企业文档，并按照 8 个维度提取关键信息。

## 文档内容
{document_text}

## 任务要求
1. 首先生成文档摘要（300 字以内）
2. 按照 8 个维度提取关键信息：
   - 研发创新能力
   - 知识产权实力
   - 资质培育进度
   - 融资与估值能力
   - 法律治理合规
   - 财务税务能力
   - 上市准备度
   - 人才资源
3. 基于提取的信息，生成每个维度的评分（0-100 分）
4. 指出文档中缺失的关键信息

请确保分析准确、提取的信息有依据。

输出格式：
【文档摘要】
...

【维度分析】
1. 研发创新能力: ... (评分: XX 分)
...

【8 维度评分】
研发创新能力: XX 分
...
"""

# =============== 知识库问答 ===============

KNOWLEDGE_QA_PROMPT = """你是科技政策法规和行业研究专家。请基于以下知识库内容，回答用户问题。

## 相关知识
{context}

## 用户问题
{question}

请提供专业、准确的回答。如果知识库内容不足以回答，请明确说明，并基于你的专业知识给出补充建议。

回答要求：
1. 引用相关法规或政策的具体条款（如有）
2. 说明政策适用条件和有效期
3. 给出实操建议
"""

# =============== 标准解释 ===============

STANDARD_EXPLAIN_PROMPT = """你是企业评测标准专家。请解释以下评测标准，并给出专业说明。

## 评测维度
维度名称: {dimension_name}
维度说明: {dimension_description}

## 指标信息
指标名称: {indicator_name}
指标说明: {indicator_description}
评分标准: {scoring_criteria}

## 任务要求
请用通俗易懂的语言解释该指标：
1. 这个指标为什么重要？
2. 不同分数代表什么水平？
3. 企业如何提升该指标？
4. 给出 1-2 个实际案例说明
5. 指出常见的误区

请确保解释专业但易懂，适合非专业人士阅读。
"""

# =============== 对话助手 ===============

ASSISTANT_SYSTEM_PROMPT = """你是 AI 科创企业评测助手。你的职责是：

1. 通过与用户对话，收集企业信息
2. 当信息足够时，调用调研能力生成 8 维度报告
3. 帮助用户理解评测标准和改进方向
4. 支持文件上传后的文档分析

你可以：
- 询问用户企业名称、行业、阶段、核心技术等基本信息
- 引导用户补充缺失的信息
- 在信息足够时生成调研报告
- 将报告中的评分导入到评测系统

请保持专业、友好、高效的对话风格。使用中文回复。
"""


def format_research_prompt(company_info: dict) -> str:
    """格式化调研报告 Prompt

    Args:
        company_info: 企业信息字典，包含 name、industry、stage、tech_direction、description 等字段

    Returns:
        填充后的完整 Prompt 字符串
    """
    return RESEARCH_REPORT_PROMPT.format(
        company_name=company_info.get("name", "未命名"),
        industry=company_info.get("industry", "未提供"),
        stage=company_info.get("stage", "未提供"),
        tech_direction=company_info.get("tech_direction", "未提供"),
        description=company_info.get("description", "未提供"),
    )


def format_document_prompt(doc_text: str) -> str:
    """格式化文档分析 Prompt

    Args:
        doc_text: 文档解析后的纯文本内容

    Returns:
        填充后的完整 Prompt 字符串（长度限制在 15000 字符以内，避免超出模型上下文）
    """
    return DOCUMENT_ANALYSIS_PROMPT.format(document_text=doc_text[:15000])


def format_knowledge_qa_prompt(context: str, question: str) -> str:
    """格式化知识库问答 Prompt

    Args:
        context: 从知识库检索到的相关文本片段
        question: 用户原始问题

    Returns:
        填充后的完整 Prompt 字符串（上下文限制在 10000 字符以内）
    """
    return KNOWLEDGE_QA_PROMPT.format(context=context[:10000], question=question)


def format_standard_explain_prompt(standard: dict) -> str:
    """格式化标准解释 Prompt

    Args:
        standard: 标准信息字典，包含 dimension_name、dimension_description、indicator_name、
                  indicator_description、scoring_criteria 等字段

    Returns:
        填充后的完整 Prompt 字符串
    """
    return STANDARD_EXPLAIN_PROMPT.format(
        dimension_name=standard.get("dimension_name", ""),
        dimension_description=standard.get("dimension_description", ""),
        indicator_name=standard.get("indicator_name", ""),
        indicator_description=standard.get("indicator_description", ""),
        scoring_criteria=standard.get("scoring_criteria", ""),
    )
