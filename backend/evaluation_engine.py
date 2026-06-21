from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import uuid
import json

from models import (
    EvaluationRequest, EvaluationResult, DimensionScore, SubIndicatorScore,
    IndicatorItemScore, CompanyInfo, GradeSummary, SubIndicatorInput,
    DimensionInput, IndicatorItemInput, SimpleEvaluationRequest
)


# ============================================================
# 评分等级标准定义
# ============================================================

GRADE_STANDARDS = [
    {"grade": "S", "label": "卓越", "min_score": 90, "max_score": 100,
     "description": "远超同阶段企业平均水平，具备显著竞争优势"},
    {"grade": "A", "label": "优秀", "min_score": 80, "max_score": 89,
     "description": "高于同阶段企业平均水平，核心能力扎实"},
    {"grade": "B", "label": "良好", "min_score": 70, "max_score": 79,
     "description": "达到同阶段企业平均水平，存在改进空间"},
    {"grade": "C", "label": "合格", "min_score": 60, "max_score": 69,
     "description": "低于同阶段企业平均水平，需要重点关注"},
    {"grade": "D", "label": "待提升", "min_score": 0, "max_score": 59,
     "description": "严重低于同阶段企业水平，存在重大风险"},
]


# ============================================================
# 阶段权重体系
# ============================================================

STAGE_WEIGHTS = {
    "seed": {      # 种子期：生存底线
        "rd_innovation": 0.20,
        "ip_protection": 0.15,
        "qualification": 0.10,
        "financing": 0.10,
        "legal_governance": 0.20,
        "finance_tax": 0.15,
        "ipo_readiness": 0.05,
        "talent_resources": 0.05,
    },
    "angel": {     # 天使期：体系建设
        "rd_innovation": 0.20,
        "ip_protection": 0.15,
        "qualification": 0.15,
        "financing": 0.15,
        "legal_governance": 0.10,
        "finance_tax": 0.10,
        "ipo_readiness": 0.05,
        "talent_resources": 0.10,
    },
    "pre-a": {     # Pre-A：跃迁准备
        "rd_innovation": 0.15,
        "ip_protection": 0.15,
        "qualification": 0.15,
        "financing": 0.20,
        "legal_governance": 0.10,
        "finance_tax": 0.10,
        "ipo_readiness": 0.05,
        "talent_resources": 0.10,
    },
    "a-round": {   # A轮：资本对接
        "rd_innovation": 0.15,
        "ip_protection": 0.15,
        "qualification": 0.10,
        "financing": 0.15,
        "legal_governance": 0.10,
        "finance_tax": 0.10,
        "ipo_readiness": 0.15,
        "talent_resources": 0.10,
    },
}


# ============================================================
# 同阶段基准数据（模拟数据，实际可从数据库或外部服务获取）
# ============================================================

BENCHMARK_DATA = {
    "seed": {
        "rd_innovation": 55.0,
        "ip_protection": 40.0,
        "qualification": 35.0,
        "financing": 45.0,
        "legal_governance": 50.0,
        "finance_tax": 40.0,
        "ipo_readiness": 25.0,
        "talent_resources": 48.0,
    },
    "angel": {
        "rd_innovation": 65.0,
        "ip_protection": 55.0,
        "qualification": 50.0,
        "financing": 55.0,
        "legal_governance": 60.0,
        "finance_tax": 55.0,
        "ipo_readiness": 35.0,
        "talent_resources": 58.0,
    },
    "pre-a": {
        "rd_innovation": 72.0,
        "ip_protection": 65.0,
        "qualification": 62.0,
        "financing": 68.0,
        "legal_governance": 68.0,
        "finance_tax": 65.0,
        "ipo_readiness": 45.0,
        "talent_resources": 65.0,
    },
    "a-round": {
        "rd_innovation": 78.0,
        "ip_protection": 72.0,
        "qualification": 68.0,
        "financing": 72.0,
        "legal_governance": 75.0,
        "finance_tax": 72.0,
        "ipo_readiness": 55.0,
        "talent_resources": 72.0,
    },
}


# ============================================================
# 评测指标库定义
# 8个一级维度，每个维度包含5-8个二级指标，每个二级指标包含3-4个三级指标
# ============================================================

EVALUATION_INDICATORS = {
    "rd_innovation": {
        "name": "研发创新能力",
        "description": "评估企业研发体系的完整性、创新方法的先进性和技术规划的前瞻性",
        "sub_indicators": {
            "1.1": {
                "name": "研发投入强度",
                "weight": 0.22,
                "description": "评估企业在研发方面的人财物投入水平",
                "indicators": {
                    "1.1.1": {"name": "研发费用占比", "default_score": 50.0,
                               "scoring_criteria": "研发费用占营收比例：≥20%得100分，15-20%得80分，10-15%得60分，5-10%得40分，<5%得20分"},
                    "1.1.2": {"name": "研发人员占比", "default_score": 50.0,
                               "scoring_criteria": "研发人员占员工总数：≥30%得100分，20-30%得80分，10-20%得60分，5-10%得40分，<5%得20分"},
                    "1.1.3": {"name": "持续投入能力", "default_score": 50.0,
                               "scoring_criteria": "近3年研发投入复合增长率：≥30%得100分，20-30%得80分，10-20%得60分，0-10%得40分，下降得20分"},
                }
            },
            "1.2": {
                "name": "研发管理体系",
                "weight": 0.18,
                "description": "评估研发管理的规范化程度",
                "indicators": {
                    "1.2.1": {"name": "立项规范性", "default_score": 45.0,
                               "scoring_criteria": "项目立项流程完整度：有完整立项制度并执行得100分，有制度未完全执行得70分，制度不完善得40分，无制度得20分"},
                    "1.2.2": {"name": "过程管理能力", "default_score": 45.0,
                               "scoring_criteria": "研发过程管控水平：有PMO或等效管理得100分，有里程碑管理得70分，有简单跟踪得40分，无管理得20分"},
                    "1.2.3": {"name": "成果验收机制", "default_score": 45.0,
                               "scoring_criteria": "研发成果验收完善度：有完整验收标准和流程得100分，有验收但未标准化得70分，偶尔验收得40分，无验收得20分"},
                    "1.2.4": {"name": "研发辅助账体系", "default_score": 40.0,
                               "scoring_criteria": "辅助账建立情况：规范建立并独立核算得100分，有辅助账但不完整得70分，仅在财务账中体现得40分，无专门归集得20分"},
                }
            },
            "1.3": {
                "name": "技术路线规划",
                "weight": 0.20,
                "description": "评估技术战略的清晰度和可执行性",
                "indicators": {
                    "1.3.1": {"name": "技术路线清晰度", "default_score": 50.0,
                               "scoring_criteria": "技术路线图明确程度：有清晰3-5年技术规划并文档化得100分，有规划但未文档化得70分，有大致方向得40分，无明确规划得20分"},
                    "1.3.2": {"name": "竞品对标能力", "default_score": 50.0,
                               "scoring_criteria": "竞品技术跟踪分析：定期输出竞品分析报告并调整技术路线得100分，有竞品关注但不系统得70分，偶尔了解竞品得40分，无竞品分析得20分"},
                    "1.3.3": {"name": "迭代计划可执行性", "default_score": 50.0,
                               "scoring_criteria": "技术迭代计划执行情况：计划完成率≥90%得100分，70-90%得80分，50-70%得60分，30-50%得40分，<30%得20分"},
                }
            },
            "1.4": {
                "name": "创新方法论",
                "weight": 0.20,
                "description": "评估企业采用先进研发方法的能力",
                "indicators": {
                    "1.4.1": {"name": "敏捷/IPD融合", "default_score": 45.0,
                               "scoring_criteria": "研发方法体系成熟度：已融合敏捷或IPD并运行良好得100分，正在推行得70分，有了解但未实施得40分，传统瀑布模式得20分"},
                    "1.4.2": {"name": "需求管理能力", "default_score": 45.0,
                               "scoring_criteria": "需求管理流程完善度：有需求池、优先级管理和变更控制得100分，有需求跟踪但不完整得70分，有需求文档得40分，需求管理混乱得20分"},
                    "1.4.3": {"name": "MVP验证能力", "default_score": 50.0,
                               "scoring_criteria": "最小可行产品验证：有MVP方法论且快速迭代验证得100分，有原型验证得70分，直接开发完整产品得40分，无验证环节得20分"},
                }
            },
            "1.5": {
                "name": "技术情报能力",
                "weight": 0.20,
                "description": "评估技术信息获取和分析能力",
                "indicators": {
                    "1.5.1": {"name": "专利检索能力", "default_score": 40.0,
                               "scoring_criteria": "专利检索分析能力：有专业检索工具并定期分析得100分，使用免费工具检索得70分，偶尔检索得40分，不关注专利得20分"},
                    "1.5.2": {"name": "竞品监控机制", "default_score": 45.0,
                               "scoring_criteria": "竞品技术监控体系：有系统化监控和预警机制得100分，有关键竞品跟踪得70分，偶尔关注得40分，无监控得20分"},
                    "1.5.3": {"name": "趋势预判能力", "default_score": 45.0,
                               "scoring_criteria": "技术趋势预判准确性：有技术雷达并准确预判趋势得100分，关注行业趋势得70分，跟随技术潮流得40分，技术视野局限得20分"},
                }
            },
        }
    },
    "ip_protection": {
        "name": "知识产权实力",
        "description": "评估企业知识产权布局质量、运营能力和合规水平",
        "sub_indicators": {
            "2.1": {
                "name": "专利布局质量",
                "weight": 0.25,
                "description": "评估专利组合的战略价值",
                "indicators": {
                    "2.1.1": {"name": "发明专利占比", "default_score": 45.0,
                               "scoring_criteria": "发明专利占专利总数比例：≥60%得100分，40-60%得80分，20-40%得60分，<20%得40分，无发明专利得20分"},
                    "2.1.2": {"name": "核心技术覆盖度", "default_score": 45.0,
                               "scoring_criteria": "核心技术领域专利覆盖：完全覆盖核心技术和关键工艺得100分，主要技术有专利保护得70分，部分技术有专利得40分，核心技术无专利保护得20分"},
                    "2.1.3": {"name": "地域布局", "default_score": 40.0,
                               "scoring_criteria": "专利地域布局：有PCT或海外主要市场布局得100分，有国内多区域布局得70分，仅单一区域得40分，无布局考虑得20分"},
                }
            },
            "2.2": {
                "name": "知识产权数量",
                "weight": 0.20,
                "description": "评估知识产权资产规模",
                "indicators": {
                    "2.2.1": {"name": "专利数量", "default_score": 45.0,
                               "scoring_criteria": "有效专利数量：≥20件得100分，10-20件得80分，5-10件得60分，1-5件得40分，0件得20分"},
                    "2.2.2": {"name": "软件著作权", "default_score": 45.0,
                               "scoring_criteria": "软著数量：≥10件得100分，5-10件得80分，3-5件得60分，1-3件得40分，0件得20分"},
                    "2.2.3": {"name": "商标与集成电路", "default_score": 40.0,
                               "scoring_criteria": "商标/集成电路布图等：有核心品牌商标且域名保护得100分，有商标注册得70分，仅有基础申请得40分，无商标意识得20分"},
                }
            },
            "2.3": {
                "name": "知识产权运营",
                "weight": 0.15,
                "description": "评估知识产权商业化能力",
                "indicators": {
                    "2.3.1": {"name": "质押融资", "default_score": 40.0,
                               "scoring_criteria": "知识产权质押融资：有成功融资案例得100分，有尝试得70分，了解政策但未尝试得40分，无认知得20分"},
                    "2.3.2": {"name": "许可转让", "default_score": 40.0,
                               "scoring_criteria": "专利许可/转让收入：有稳定许可收入得100分，有转让/许可案例得70分，有考虑得40分，无运营意识得20分"},
                    "2.3.3": {"name": "价值评估", "default_score": 40.0,
                               "scoring_criteria": "知识产权价值评估：有第三方评估报告得100分，内部有估值方法得70分，有初步估算得40分，无价值概念得20分"},
                }
            },
            "2.4": {
                "name": "开源合规",
                "weight": 0.20,
                "description": "评估开源软件使用合规性",
                "indicators": {
                    "2.4.1": {"name": "开源许可证审查", "default_score": 45.0,
                               "scoring_criteria": "开源许可证合规审查：有完整的开源软件清单和许可证审查得100分，有主要组件审查得70分，有了解但未系统审查得40分，无审查得20分"},
                    "2.4.2": {"name": "合规管理制度", "default_score": 45.0,
                               "scoring_criteria": "开源合规管理制度：有明确的开源使用政策和审批流程得100分，有使用规范得70分，有口头要求得40分，无管理得20分"},
                }
            },
            "2.5": {
                "name": "商业秘密保护",
                "weight": 0.20,
                "description": "评估商业秘密保护体系",
                "indicators": {
                    "2.5.1": {"name": "保密制度", "default_score": 45.0,
                               "scoring_criteria": "保密制度完善度：有分级保密制度并严格执行得100分，有保密制度得70分，有保密意识得40分，无保密措施得20分"},
                    "2.5.2": {"name": "竞业限制", "default_score": 45.0,
                               "scoring_criteria": "竞业限制管理：核心人员均有竞业限制且补偿合理得100分，部分关键人员有竞业限制得70分，有竞业条款但执行不力得40分，无竞业限制得20分"},
                    "2.5.3": {"name": "文档管理", "default_score": 45.0,
                               "scoring_criteria": "技术文档管理：有文档分级管理和访问控制得100分，有集中存储得70分，文档分散但可找到得40分，文档管理混乱得20分"},
                }
            },
        }
    },
    "qualification": {
        "name": "资质培育进度",
        "description": "评估企业科技资质获取、规划和合规水平",
        "sub_indicators": {
            "3.1": {
                "name": "已获资质",
                "weight": 0.25,
                "description": "评估企业已获得的科技资质",
                "indicators": {
                    "3.1.1": {"name": "科技型中小企业", "default_score": 40.0,
                               "scoring_criteria": "科技型中小企业认定：已入库得100分，准备申请得60分，了解政策得40分，不了解得20分"},
                    "3.1.2": {"name": "高新技术企业", "default_score": 40.0,
                               "scoring_criteria": "高新技术企业认定：已认定且在有效期内得100分，曾认定过期得70分，准备申请得50分，不符合条件得30分"},
                    "3.1.3": {"name": "专精特新/小巨人", "default_score": 35.0,
                               "scoring_criteria": "专精特新认定：已获小巨人得100分，已获省级专精特新得80分，已获市级得60分，准备申请得40分，无计划得20分"},
                }
            },
            "3.2": {
                "name": "资质进阶规划",
                "weight": 0.20,
                "description": "评估资质培育的路线图和执行",
                "indicators": {
                    "3.2.1": {"name": "路线图清晰度", "default_score": 45.0,
                               "scoring_criteria": "资质进阶路线图：有明确3-5年资质规划得100分，有大致规划得70分，有目标但无路线图得40分，无规划得20分"},
                    "3.2.2": {"name": "时间节点", "default_score": 45.0,
                               "scoring_criteria": "关键时间节点把控：各资质申请时间节点明确且责任人清晰得100分，有时间节点得70分，有大致时间计划得40分，无时间管理得20分"},
                    "3.2.3": {"name": "里程碑管理", "default_score": 45.0,
                               "scoring_criteria": "里程碑完成率：按计划完成全部里程碑得100分，完成大部分得70分，完成部分得40分，无里程碑管理得20分"},
                }
            },
            "3.3": {
                "name": "研发投入合规",
                "weight": 0.25,
                "description": "评估研发投入的政策合规性",
                "indicators": {
                    "3.3.1": {"name": "加计扣除", "default_score": 45.0,
                               "scoring_criteria": "研发费用加计扣除：规范申报并享受优惠得100分，有申报但不规范得70分，有申报但金额偏低得40分，未申报得20分"},
                    "3.3.2": {"name": "高新收入占比", "default_score": 45.0,
                               "scoring_criteria": "高新技术产品收入占比：≥60%得100分，50-60%得80分，40-50%得60分，<40%得40分，无法区分得20分"},
                    "3.3.3": {"name": "研发辅助账", "default_score": 45.0,
                               "scoring_criteria": "研发费用辅助账：规范设立并独立核算得100分，有辅助账但需完善得70分，仅在财务账中归集得40分，无专门归集得20分"},
                }
            },
            "3.4": {
                "name": "政策匹配度",
                "weight": 0.30,
                "description": "评估政策资源的利用效率",
                "indicators": {
                    "3.4.1": {"name": "补贴申请", "default_score": 45.0,
                               "scoring_criteria": "政府补贴申请：近3年有补贴申请并获支持得100分，有申请但未获批得70分，有关注但未申请得40分，不关注政策得20分"},
                    "3.4.2": {"name": "税收优惠", "default_score": 45.0,
                               "scoring_criteria": "税收优惠享受：充分享受高企/研发等税收优惠得100分，享受部分优惠得70分，了解但未充分享受得40分，不了解得20分"},
                    "3.4.3": {"name": "政府项目", "default_score": 45.0,
                               "scoring_criteria": "政府项目参与：承担过省部级以上项目得100分，承担过市级项目得70分，有项目参与得40分，无参与得20分"},
                }
            },
        }
    },
    "financing": {
        "name": "融资与估值能力",
        "description": "评估企业融资能力、估值合理性和资本健康度",
        "sub_indicators": {
            "4.1": {
                "name": "融资历史",
                "weight": 0.25,
                "description": "评估过往融资质量和效率",
                "indicators": {
                    "4.1.1": {"name": "轮次与金额", "default_score": 45.0,
                               "scoring_criteria": "融资轮次与金额匹配：融资节奏与业务发展匹配得100分，有融资但节奏稍快/慢得70分，融资困难但金额不足得40分，无融资经历得20分"},
                    "4.1.2": {"name": "投资方质量", "default_score": 45.0,
                               "scoring_criteria": "投资方背景：有知名机构投资且产业协同得100分，有知名机构得70分，有产业投资得50分，仅有个人/政府投资得30分，无融资得20分"},
                    "4.1.3": {"name": "资金效率", "default_score": 45.0,
                               "scoring_criteria": "资金使用效率：资金用于核心业务且ROI清晰得100分，主要用于业务发展得70分，资金使用较分散得40分，资金效率低得20分"},
                }
            },
            "4.2": {
                "name": "估值合理性",
                "weight": 0.20,
                "description": "评估企业估值的逻辑和合理性",
                "indicators": {
                    "4.2.1": {"name": "同业对标", "default_score": 45.0,
                               "scoring_criteria": "估值同业对标：有清晰的同业估值对比且合理得100分，有简单对标得70分，有粗略了解得40分，无对标得20分"},
                    "4.2.2": {"name": "估值方法", "default_score": 45.0,
                               "scoring_criteria": "估值方法运用：使用多种估值方法并交叉验证得100分，使用主流方法得70分，有粗略估算得40分，无估值概念得20分"},
                    "4.2.3": {"name": "增长空间", "default_score": 50.0,
                               "scoring_criteria": "估值增长空间：有清晰的增长路径支撑估值得100分，增长预期合理得70分，增长预期模糊得40分，无增长规划得20分"},
                }
            },
            "4.3": {
                "name": "资本健康度",
                "weight": 0.20,
                "description": "评估企业资本结构和可持续性",
                "indicators": {
                    "4.3.1": {"name": "Runway月数", "default_score": 45.0,
                               "scoring_criteria": "现金runway：≥18个月得100分，12-18个月得80分，6-12个月得60分，3-6个月得40分，<3个月得20分"},
                    "4.3.2": {"name": "烧钱率", "default_score": 45.0,
                               "scoring_criteria": "月度烧钱率合理性：烧钱率与增长目标匹配得100分，可控范围内得70分，偏高但可接受得40分，过高且不可持续得20分"},
                    "4.3.3": {"name": "现金流管理", "default_score": 45.0,
                               "scoring_criteria": "现金流管理能力：有现金流预测和管控机制得100分，有现金流监控得70分，有基本财务管控得40分，现金流管理薄弱得20分"},
                }
            },
            "4.4": {
                "name": "融资准备度",
                "weight": 0.20,
                "description": "评估企业融资准备工作的完善程度",
                "indicators": {
                    "4.4.1": {"name": "BP质量", "default_score": 45.0,
                               "scoring_criteria": "商业计划书质量：BP逻辑清晰、数据详实、亮点突出得100分，BP基本完整得70分，BP粗糙得40分，无BP得20分"},
                    "4.4.2": {"name": "路演能力", "default_score": 45.0,
                               "scoring_criteria": "路演表达能力：有专业路演材料且表达清晰得100分，有路演经验得70分，有准备但未路演得40分，无路演准备得20分"},
                    "4.4.3": {"name": "尽调材料", "default_score": 45.0,
                               "scoring_criteria": "尽调材料准备：尽调材料包完整且随时可用得100分，主要材料齐全得70分，材料分散但可收集得40分，无准备得20分"},
                }
            },
            "4.5": {
                "name": "股权架构",
                "weight": 0.15,
                "description": "评估股权结构的健康度和风险",
                "indicators": {
                    "4.5.1": {"name": "创始人控股比例", "default_score": 50.0,
                               "scoring_criteria": "创始人控股比例：50%以上得100分，34-50%得80分，20-34%得60分，10-20%得40分，<10%得20分"},
                    "4.5.2": {"name": "期权池", "default_score": 45.0,
                               "scoring_criteria": "期权池设置：有预留期权池且制度完善得100分，有预留但制度待完善得70分，有考虑得40分，无期权池得20分"},
                    "4.5.3": {"name": "代持风险", "default_score": 45.0,
                               "scoring_criteria": "股权代持风险：无代持或代持已清理得100分，有代持但有清理计划得70分，有代持且无计划得40分，代持结构复杂得20分"},
                }
            },
        }
    },
    "legal_governance": {
        "name": "法律治理合规",
        "description": "评估企业法律合规和公司治理水平",
        "sub_indicators": {
            "5.1": {
                "name": "股权结构",
                "weight": 0.25,
                "description": "评估股权架构的清晰度和稳定性",
                "indicators": {
                    "5.1.1": {"name": "创始人控股", "default_score": 50.0,
                               "scoring_criteria": "创始人控股稳定性：创始人控股且股权清晰得100分，创始人相对控股得70分，股权分散但创始人控制得40分，控制权不明确得20分"},
                    "5.1.2": {"name": "股权分配", "default_score": 45.0,
                               "scoring_criteria": "股权分配合理性：股权与贡献匹配且无争议得100分，基本合理得70分，有隐患得40分，分配混乱得20分"},
                    "5.1.3": {"name": "Vesting条款", "default_score": 45.0,
                               "scoring_criteria": "股权兑现条款：有4年Vesting且条款合理得100分，有Vesting但条款待完善得70分，有Vesting意识得40分，无Vesting得20分"},
                }
            },
            "5.2": {
                "name": "公司治理",
                "weight": 0.20,
                "description": "评估公司治理结构规范性",
                "indicators": {
                    "5.2.1": {"name": "三会一层", "default_score": 45.0,
                               "scoring_criteria": "治理架构运行：三会一层运行规范且会议记录完整得100分，有治理架构得70分，架构不完整得40分，无治理架构得20分"},
                    "5.2.2": {"name": "章程规范", "default_score": 45.0,
                               "scoring_criteria": "公司章程完善度：章程符合公司法且保护创始人权益得100分，章程基本完善得70分，使用模板章程得40分，章程存在重大缺陷得20分"},
                    "5.2.3": {"name": "表决机制", "default_score": 45.0,
                               "scoring_criteria": "表决机制设计：有一致行动人协议或特殊表决机制得100分，有合理的表决权安排得70分，按出资比例表决得40分，表决机制混乱得20分"},
                }
            },
            "5.3": {
                "name": "合同管理",
                "weight": 0.20,
                "description": "评估合同管理的规范性",
                "indicators": {
                    "5.3.1": {"name": "核心合同", "default_score": 45.0,
                               "scoring_criteria": "核心合同管理：有模板库且合同审批规范得100分，主要合同有归档得70分，合同管理较随意得40分，无合同管理得20分"},
                    "5.3.2": {"name": "关联交易", "default_score": 40.0,
                               "scoring_criteria": "关联交易规范：有识别和审批机制且定价公允得100分，有识别机制得70分，有认知但无机制得40分，不关注关联交易得20分"},
                    "5.3.3": {"name": "对外担保", "default_score": 40.0,
                               "scoring_criteria": "对外担保管理：无对外担保或担保有充分反担保得100分，有担保但风险可控得70分，有担保且风险较高得40分，担保失控得20分"},
                }
            },
            "5.4": {
                "name": "劳动用工",
                "weight": 0.15,
                "description": "评估劳动用工合规性",
                "indicators": {
                    "5.4.1": {"name": "劳动合同", "default_score": 50.0,
                               "scoring_criteria": "劳动合同签署：全员签署且条款合法得100分，主要员工签署得70分，部分签署得40分，签署率低得20分"},
                    "5.4.2": {"name": "竞业限制", "default_score": 45.0,
                               "scoring_criteria": "竞业限制管理：核心人员有竞业限制且补偿合理得100分，有竞业限制得70分，有条款但执行不力得40分，无竞业限制得20分"},
                    "5.4.3": {"name": "保密协议", "default_score": 50.0,
                               "scoring_criteria": "保密协议签署：全员签署得100分，主要员工签署得70分，部分签署得40分，未签署得20分"},
                }
            },
            "5.5": {
                "name": "数据合规",
                "weight": 0.20,
                "description": "评估数据安全和隐私保护合规性",
                "indicators": {
                    "5.5.1": {"name": "网络安全", "default_score": 45.0,
                               "scoring_criteria": "网络安全合规：有等保备案且定期测评得100分，有安全防护措施得70分，有基础防护得40分，无防护得20分"},
                    "5.5.2": {"name": "数据安全", "default_score": 45.0,
                               "scoring_criteria": "数据安全管理：有数据分类分级和访问控制得100分，有数据备份和恢复得70分，有基础防护得40分，无数据安全意识得20分"},
                    "5.5.3": {"name": "个人信息保护", "default_score": 45.0,
                               "scoring_criteria": "个人信息保护：有隐私政策且处理合规得100分，有隐私政策得70分，有认知但不完整得40分，无保护意识得20分"},
                }
            },
        }
    },
    "finance_tax": {
        "name": "财务税务规范",
        "description": "评估企业财务管理和税务合规水平",
        "sub_indicators": {
            "6.1": {
                "name": "财务内控",
                "weight": 0.20,
                "description": "评估财务内部控制体系",
                "indicators": {
                    "6.1.1": {"name": "记账规范", "default_score": 50.0,
                               "scoring_criteria": "记账规范性：按会计准则规范记账得100分，记账基本规范得70分，记账有瑕疵得40分，记账混乱得20分"},
                    "6.1.2": {"name": "审批流程", "default_score": 45.0,
                               "scoring_criteria": "审批流程：有分级审批且执行严格得100分，有审批流程得70分，审批流程不完善得40分，无审批流程得20分"},
                    "6.1.3": {"name": "资金安全", "default_score": 50.0,
                               "scoring_criteria": "资金安全管理：有资金集中管理和监控得100分，有基本管控得70分，管控较弱得40分，无管控得20分"},
                }
            },
            "6.2": {
                "name": "研发费用归集",
                "weight": 0.20,
                "description": "评估研发费用归集的准确性和完整性",
                "indicators": {
                    "6.2.1": {"name": "辅助账", "default_score": 45.0,
                               "scoring_criteria": "研发费用辅助账：规范设立并独立核算得100分，有辅助账但需完善得70分，仅在财务账中归集得40分，无专门归集得20分"},
                    "6.2.2": {"name": "工时分配", "default_score": 45.0,
                               "scoring_criteria": "研发工时分配：有准确的工时记录和分配方法得100分，有工时记录得70分，有粗略估算得40分，无工时管理得20分"},
                    "6.2.3": {"name": "费用分摊", "default_score": 45.0,
                               "scoring_criteria": "费用分摊合理性：有合理的分摊标准并执行得100分，有分摊方法得70分，分摊较随意得40分，无分摊得20分"},
                }
            },
            "6.3": {
                "name": "税务合规",
                "weight": 0.20,
                "description": "评估税务合规管理水平",
                "indicators": {
                    "6.3.1": {"name": "纳税申报", "default_score": 50.0,
                               "scoring_criteria": "纳税申报及时准确：按时准确申报且无逾期得100分，偶有逾期得70分，经常逾期得40分，有欠税得20分"},
                    "6.3.2": {"name": "发票管理", "default_score": 50.0,
                               "scoring_criteria": "发票管理规范：发票管理严格且无虚开得100分，管理基本规范得70分，有管理但不够严格得40分，发票管理混乱得20分"},
                    "6.3.3": {"name": "金税四期应对", "default_score": 45.0,
                               "scoring_criteria": "金税四期应对：有系统应对方案且数据治理完成得100分，有认知并开始准备得70分，有了解但无行动得40分，不了解得20分"},
                }
            },
            "6.4": {
                "name": "财务透明度",
                "weight": 0.20,
                "description": "评估财务信息披露质量",
                "indicators": {
                    "6.4.1": {"name": "审计报告", "default_score": 45.0,
                               "scoring_criteria": "审计报告：有标准无保留意见审计报告得100分，有审计报告得70分，有账务但未审计得40分，账务不清得20分"},
                    "6.4.2": {"name": "财务报表", "default_score": 50.0,
                               "scoring_criteria": "财务报表质量：报表规范且能反映真实经营得100分，报表基本完整得70分，报表有瑕疵得40分，报表无法使用得20分"},
                    "6.4.3": {"name": "关联交易披露", "default_score": 45.0,
                               "scoring_criteria": "关联交易披露：完整披露且定价公允得100分，有披露得70分，披露不完整得40分，未披露得20分"},
                }
            },
            "6.5": {
                "name": "税收优化",
                "weight": 0.20,
                "description": "评估税收优惠政策利用程度",
                "indicators": {
                    "6.5.1": {"name": "加计扣除", "default_score": 50.0,
                               "scoring_criteria": "研发费用加计扣除：充分享受且申报规范得100分，有享受得70分，享受不充分得40分，未享受得20分"},
                    "6.5.2": {"name": "高新税率", "default_score": 50.0,
                               "scoring_criteria": "高新技术企业所得税优惠：享受15%税率且合规得100分，有享受得70分，不符合条件得40分，未申请得20分"},
                    "6.5.3": {"name": "政策红利获取", "default_score": 45.0,
                               "scoring_criteria": "政策红利获取：充分利用各项税收优惠政策得100分，主要政策有享受得70分，有享受但不够充分得40分，不了解政策得20分"},
                }
            },
        }
    },
    "ipo_readiness": {
        "name": "上市准备度",
        "description": "评估企业上市准备工作的完善程度",
        "sub_indicators": {
            "7.1": {
                "name": "板块适配性",
                "weight": 0.25,
                "description": "评估企业与各上市板块的匹配度",
                "indicators": {
                    "7.1.1": {"name": "科创板匹配度", "default_score": 40.0,
                               "scoring_criteria": "科创板匹配度：完全符合科创属性要求得100分，基本符合得70分，部分符合得40分，不符合得20分"},
                    "7.1.2": {"name": "创业板匹配度", "default_score": 40.0,
                               "scoring_criteria": "创业板匹配度：完全符合三创四新要求得100分，基本符合得70分，部分符合得40分，不符合得20分"},
                    "7.1.3": {"name": "北交所/主板匹配度", "default_score": 40.0,
                               "scoring_criteria": "北交所/主板匹配度：符合板块定位得100分，基本符合得70分，部分符合得40分，不符合得20分"},
                }
            },
            "7.2": {
                "name": "合规差距",
                "weight": 0.25,
                "description": "评估与上市合规要求的差距",
                "indicators": {
                    "7.2.1": {"name": "财务差距", "default_score": 45.0,
                               "scoring_criteria": "财务合规差距：财务规范距离上市要求差距小得100分，差距可控得70分，差距较大得40分，差距巨大得20分"},
                    "7.2.2": {"name": "法律差距", "default_score": 45.0,
                               "scoring_criteria": "法律合规差距：法律合规距离上市要求差距小得100分，差距可控得70分，差距较大得40分，差距巨大得20分"},
                    "7.2.3": {"name": "治理差距", "default_score": 45.0,
                               "scoring_criteria": "治理合规差距：治理规范距离上市要求差距小得100分，差距可控得70分，差距较大得40分，差距巨大得20分"},
                    "7.2.4": {"name": "知识产权差距", "default_score": 45.0,
                               "scoring_criteria": "知识产权合规差距：知识产权距离上市要求差距小得100分，差距可控得70分，差距较大得40分，差距巨大得20分"},
                }
            },
            "7.3": {
                "name": "时间规划",
                "weight": 0.20,
                "description": "评估上市时间规划的合理性",
                "indicators": {
                    "7.3.1": {"name": "3-5年路线图", "default_score": 45.0,
                               "scoring_criteria": "上市路线图：有清晰的3-5年上市规划得100分，有大致规划得70分，有目标但无路线图得40分，无上市计划得20分"},
                    "7.3.2": {"name": "里程碑", "default_score": 45.0,
                               "scoring_criteria": "里程碑设定：关键里程碑明确且可衡量得100分，有里程碑得70分，里程碑模糊得40分，无里程碑得20分"},
                    "7.3.3": {"name": "关键节点", "default_score": 45.0,
                               "scoring_criteria": "关键节点把控：关键节点有明确时间表和责任人得100分，有节点管理得70分，节点模糊得40分，无节点管理得20分"},
                }
            },
            "7.4": {
                "name": "中介机构准备",
                "weight": 0.15,
                "description": "评估中介机构对接情况",
                "indicators": {
                    "7.4.1": {"name": "券商/律所/会所对接", "default_score": 40.0,
                               "scoring_criteria": "中介机构对接：已签约头部中介机构得100分，已接触并确定合作意向得70分，有接触得40分，无接触得20分"},
                    "7.4.2": {"name": "辅导期管理", "default_score": 40.0,
                               "scoring_criteria": "辅导期管理：已启动辅导且进展顺利得100分，已启动辅导得70分，有辅导计划得40分，无辅导计划得20分"},
                }
            },
            "7.5": {
                "name": "科创属性",
                "weight": 0.15,
                "description": "评估科创板要求的科创属性",
                "indicators": {
                    "7.5.1": {"name": "研发投入占比", "default_score": 45.0,
                               "scoring_criteria": "研发投入占比：≥5%或绝对额高得100分，3-5%得80分，符合基本要求得60分，接近要求得40分，不满足得20分"},
                    "7.5.2": {"name": "发明专利", "default_score": 45.0,
                               "scoring_criteria": "发明专利数量：≥5项且形成主营业务收入得100分，3-5项得80分，有发明专利得60分，发明专利少得40分，无发明专利得20分"},
                    "7.5.3": {"name": "营收增长率", "default_score": 45.0,
                               "scoring_criteria": "营收复合增长率：≥20%得100分，10-20%得80分，符合要求得60分，增长缓慢得40分，下滑得20分"},
                }
            },
        }
    },
    "talent_resources": {
        "name": "人才与资源",
        "description": "评估企业人才团队建设和资源整合能力",
        "sub_indicators": {
            "8.1": {
                "name": "核心团队",
                "weight": 0.25,
                "description": "评估核心团队质量",
                "indicators": {
                    "8.1.1": {"name": "创始人背景", "default_score": 50.0,
                               "scoring_criteria": "创始人背景与能力：有成功创业经历或顶级行业背景得100分，有丰富行业经验得70分，有技术背景但商业经验不足得40分，背景一般得20分"},
                    "8.1.2": {"name": "团队稳定性", "default_score": 50.0,
                               "scoring_criteria": "核心团队稳定性：核心团队完整且稳定≥3年得100分，有流失但关键岗位稳定得70分，有流失得40分，团队频繁变动得20分"},
                    "8.1.3": {"name": "关键人才", "default_score": 50.0,
                               "scoring_criteria": "关键人才引进：关键岗位人才齐备且胜任得100分，主要岗位有人得70分，有关键岗位空缺得40分，人才短缺严重得20分"},
                }
            },
            "8.2": {
                "name": "人才激励",
                "weight": 0.20,
                "description": "评估人才激励体系",
                "indicators": {
                    "8.2.1": {"name": "股权激励", "default_score": 45.0,
                               "scoring_criteria": "股权激励体系：有完善的股权激励计划且覆盖核心员工得100分，有股权激励得70分，有计划但未实施得40分，无激励得20分"},
                    "8.2.2": {"name": "薪酬竞争力", "default_score": 50.0,
                               "scoring_criteria": "薪酬市场竞争力：薪酬处于行业75分位以上得100分，50-75分位得70分，行业平均得40分，低于行业平均得20分"},
                    "8.2.3": {"name": "职业发展", "default_score": 45.0,
                               "scoring_criteria": "职业发展通道：有清晰的职业发展路径和晋升机制得100分，有通道得70分，有初步规划得40分，无规划得20分"},
                }
            },
            "8.3": {
                "name": "产学研合作",
                "weight": 0.20,
                "description": "评估产学研合作深度",
                "indicators": {
                    "8.3.1": {"name": "高校合作", "default_score": 45.0,
                               "scoring_criteria": "高校合作深度：有实质性合作（联合项目/成果转化）得100分，有合作协议得70分，有联系得40分，无合作得20分"},
                    "8.3.2": {"name": "成果转化", "default_score": 45.0,
                               "scoring_criteria": "科技成果转化：有成功转化案例且产生效益得100分，有转化尝试得70分，有认知得40分，无转化得20分"},
                    "8.3.3": {"name": "联合实验室", "default_score": 40.0,
                               "scoring_criteria": "联合实验室：有共建实验室且运行良好得100分，有共建实验室得70分，有合作意向得40分，无联合实验室得20分"},
                }
            },
            "8.4": {
                "name": "人才政策",
                "weight": 0.15,
                "description": "评估人才政策利用程度",
                "indicators": {
                    "8.4.1": {"name": "落户/补贴", "default_score": 45.0,
                               "scoring_criteria": "人才落户和补贴：核心团队享受人才政策得100分，有员工享受得70分，有申请得40分，不了解得20分"},
                    "8.4.2": {"name": "人才称号", "default_score": 40.0,
                               "scoring_criteria": "人才称号获取：有国家级/省级人才称号得100分，有市级人才称号得70分，有区级得40分，无称号得20分"},
                    "8.4.3": {"name": "科研人才", "default_score": 45.0,
                               "scoring_criteria": "科研人才引进：有高层次科研人才全职加入得100分，有合作科研人才得70分，有招聘计划得40分，无科研人才得20分"},
                }
            },
            "8.5": {
                "name": "技术经理人",
                "weight": 0.20,
                "description": "评估外部专家资源",
                "indicators": {
                    "8.5.1": {"name": "外部专家", "default_score": 45.0,
                               "scoring_criteria": "外部专家顾问：有行业顶级专家顾问团队得100分，有专家顾问得70分，有临时咨询得40分，无外部专家得20分"},
                    "8.5.2": {"name": "顾问团队", "default_score": 45.0,
                               "scoring_criteria": "顾问团队建设：有完善的顾问委员会且定期活动得100分，有顾问得70分，有联系得40分，无顾问得20分"},
                    "8.5.3": {"name": "产业资源", "default_score": 45.0,
                               "scoring_criteria": "产业资源整合：有深度产业合作资源得100分，有产业联系得70分，有初步接触得40分，无产业资源得20分"},
                }
            },
        }
    },
}


# ============================================================
# 评测引擎核心类
# ============================================================

class EvaluationEngine:
    """科创企业评测引擎
    
    提供完整的评测计算逻辑，包括：
    - 指标定义管理
    - 评分计算（支持空值处理）
    - 加权计算（支持动态权重调整）
    - 等级判定
    - 与基准数据对比
    - 优势/劣势/风险识别
    """
    
    def __init__(self):
        """初始化评测引擎，加载指标定义和权重配置"""
        self.indicators = EVALUATION_INDICATORS
        self.stage_weights = STAGE_WEIGHTS
        self.benchmarks = BENCHMARK_DATA
        self.grades = GRADE_STANDARDS
    
    # ============================================================
    # 阶段权重管理
    # ============================================================
    
    def get_stage_weights(self, stage: str) -> Dict[str, float]:
        """获取指定发展阶段的权重配置
        
        Args:
            stage: 发展阶段（seed/angel/pre-a/a-round）
            
        Returns:
            各维度权重字典
        """
        if stage not in self.stage_weights:
            raise ValueError(f"未知的发展阶段: {stage}，合法值为: {list(self.stage_weights.keys())}")
        return self.stage_weights[stage].copy()
    
    def update_stage_weights(self, stage: str, weights: Dict[str, float]) -> None:
        """动态更新指定阶段的权重配置
        
        支持运行时动态调整权重，用于个性化评测场景。
        
        Args:
            stage: 发展阶段
            weights: 新的权重字典，权重之和应接近1.0
        """
        # 验证权重合法性
        if stage not in self.stage_weights:
            raise ValueError(f"未知的发展阶段: {stage}")
        
        total_weight = sum(weights.values())
        if not 0.95 <= total_weight <= 1.05:
            raise ValueError(f"权重之和必须在0.95-1.05之间，当前为: {total_weight}")
        
        self.stage_weights[stage] = weights.copy()
    
    def get_all_stage_weights(self) -> Dict[str, Dict[str, float]]:
        """获取所有阶段的权重配置"""
        return {k: v.copy() for k, v in self.stage_weights.items()}
    
    # ============================================================
    # 指标定义管理
    # ============================================================
    
    def get_dimension_definitions(self) -> List[Dict[str, Any]]:
        """获取所有评测维度定义（用于API响应）"""
        result = []
        for dim_id, dim_data in self.indicators.items():
            dim_def = {
                "dimension_id": dim_id,
                "name": dim_data["name"],
                "description": dim_data["description"],
                "sub_indicators": []
            }
            for sub_id, sub_data in dim_data["sub_indicators"].items():
                sub_def = {
                    "sub_indicator_id": sub_id,
                    "name": sub_data["name"],
                    "weight": sub_data["weight"],
                    "description": sub_data["description"],
                    "indicators": []
                }
                for ind_id, ind_data in sub_data["indicators"].items():
                    sub_def["indicators"].append({
                        "indicator_id": ind_id,
                        "name": ind_data["name"],
                        "default_score": ind_data["default_score"],
                        "scoring_criteria": ind_data["scoring_criteria"],
                    })
                dim_def["sub_indicators"].append(sub_def)
            result.append(dim_def)
        return result
    
    def get_dimension_definition(self, dimension_id: str) -> Optional[Dict[str, Any]]:
        """获取指定维度的定义"""
        if dimension_id not in self.indicators:
            return None
        return self.indicators[dimension_id].copy()
    
    # ============================================================
    # 评分计算核心逻辑
    # ============================================================
    
    def _get_grade(self, score: float) -> Tuple[str, str]:
        """根据得分判定等级
        
        Args:
            score: 得分（0-100）
            
        Returns:
            (等级代码, 等级标签) 元组
        """
        for grade in self.grades:
            if grade["min_score"] <= score <= grade["max_score"]:
                return grade["grade"], grade["label"]
        return "D", "待提升"
    
    def _calculate_sub_indicator_score(
        self, 
        sub_id: str, 
        sub_data: Dict[str, Any], 
        input_items: List[IndicatorItemInput]
    ) -> SubIndicatorScore:
        """计算单个二级指标的得分
        
        处理数据贫乏情况：对于未提供的三级指标，使用默认值。
        确保评分逻辑透明，记录每个分数的来源。
        
        Args:
            sub_id: 二级指标ID
            sub_data: 二级指标定义数据
            input_items: 用户输入的三级指标评分
            
        Returns:
            二级指标评分结果
        """
        # 构建输入项的快速查找字典
        input_dict = {item.indicator_id: item for item in input_items}
        
        items_result = []
        total_score = 0.0
        valid_count = 0
        default_count = 0
        
        # 遍历该二级指标下的所有三级指标定义
        for ind_id, ind_def in sub_data["indicators"].items():
            if ind_id in input_dict and input_dict[ind_id].score is not None:
                # 用户提供了评分，使用用户评分
                score = input_dict[ind_id].score
                is_default = False
                evidence = input_dict[ind_id].evidence or "用户提供评分"
            else:
                # 用户未提供评分，使用默认值（数据贫乏处理）
                score = ind_def["default_score"]
                is_default = True
                evidence = f"数据未提供，使用默认值({ind_def['default_score']})"
                default_count += 1
            
            total_score += score
            valid_count += 1
            
            items_result.append(IndicatorItemScore(
                indicator_id=ind_id,
                name=ind_def["name"],
                score=score,
                max_score=100.0,
                evidence=evidence,
                notes=input_dict.get(ind_id, IndicatorItemInput(indicator_id=ind_id)).notes,
                is_default=is_default
            ))
        
        # 计算二级指标平均分
        raw_score = total_score / valid_count if valid_count > 0 else 0.0
        
        return SubIndicatorScore(
            sub_indicator_id=sub_id,
            name=sub_data["name"],
            weight=sub_data["weight"],
            score=raw_score,  # 二级指标得分即为其下三级指标的简单平均
            raw_score=raw_score,
            item_count=valid_count,
            default_count=default_count,
            items=items_result
        )
    
    def _calculate_dimension_score(
        self, 
        dim_id: str, 
        dim_data: Dict[str, Any], 
        sub_inputs: List[SubIndicatorInput],
        stage_weight: float
    ) -> DimensionScore:
        """计算单个一级维度的得分
        
        使用二级指标权重进行加权平均。
        
        Args:
            dim_id: 维度ID
            dim_data: 维度定义数据
            sub_inputs: 用户输入的二级指标数据
            stage_weight: 该维度在当前阶段的权重
            
        Returns:
            维度评分结果
        """
        # 构建输入项的快速查找字典
        input_dict = {sub.sub_indicator_id: sub for sub in sub_inputs}
        
        sub_results = []
        weighted_sum = 0.0
        total_weight = 0.0
        total_raw_score = 0.0
        sub_count = 0
        
        # 遍历该维度下的所有二级指标定义
        for sub_id, sub_def in dim_data["sub_indicators"].items():
            input_items = []
            if sub_id in input_dict:
                input_items = input_dict[sub_id].items
            
            # 计算二级指标得分
            sub_score = self._calculate_sub_indicator_score(sub_id, sub_def, input_items)
            sub_results.append(sub_score)
            
            # 加权累加（权重为二级指标在维度内的权重）
            weighted_sum += sub_score.score * sub_def["weight"]
            total_weight += sub_def["weight"]
            total_raw_score += sub_score.score
            sub_count += 1
        
        # 计算维度加权得分（如果权重和不等于1，进行归一化）
        if total_weight > 0:
            dim_score = weighted_sum / total_weight
        else:
            dim_score = 0.0
        
        raw_avg = total_raw_score / sub_count if sub_count > 0 else 0.0
        grade, grade_label = self._get_grade(dim_score)
        
        return DimensionScore(
            dimension_id=dim_id,
            name=dim_data["name"],
            weight=stage_weight,
            score=dim_score,
            raw_score=raw_avg,
            sub_indicators=sub_results,
            grade=grade,
            grade_label=grade_label,
            benchmark=None,
            gap=None
        )
    
    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        """执行完整的企业评测
        
        这是评测的核心入口方法，处理完整的评测流程：
        1. 验证企业阶段合法性
        2. 获取阶段权重
        3. 计算各维度得分
        4. 计算综合得分
        5. 判定综合等级
        6. 识别优势、劣势和风险
        7. 对比同阶段基准数据
        
        Args:
            request: 评测请求，包含企业信息和各维度评分数据
            
        Returns:
            完整评测结果
        """
        company = request.company
        stage = company.stage
        
        # 获取阶段权重
        weights = self.get_stage_weights(stage)
        
        # 构建输入维度的快速查找字典
        dim_input_dict = {dim.dimension_id: dim for dim in request.dimensions}
        
        # 计算各维度得分
        dimensions_result = []
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for dim_id, dim_data in self.indicators.items():
            sub_inputs = []
            if dim_id in dim_input_dict:
                sub_inputs = dim_input_dict[dim_id].sub_indicators
            
            dim_weight = weights.get(dim_id, 0.0)
            dim_score = self._calculate_dimension_score(dim_id, dim_data, sub_inputs, dim_weight)
            
            # 补充基准数据对比
            benchmark = self.benchmarks.get(stage, {}).get(dim_id)
            dim_score.benchmark = benchmark
            if benchmark is not None:
                dim_score.gap = round(dim_score.score - benchmark, 2)
            
            dimensions_result.append(dim_score)
            total_weighted_score += dim_score.score * dim_weight
            total_weight += dim_weight
        
        # 计算综合得分（归一化）
        if total_weight > 0:
            total_score = total_weighted_score / total_weight
        else:
            total_score = 0.0
        
        total_score = round(total_score, 2)
        overall_grade, overall_grade_label = self._get_grade(total_score)
        
        # 识别优势（得分≥80 或 高于基准10分以上）
        strengths = []
        # 识别劣势（得分<60 或 低于基准10分以上）
        weaknesses = []
        # 识别风险（得分<50 或 等级为D）
        risks = []
        
        for dim in dimensions_result:
            if dim.score >= 80 or (dim.gap is not None and dim.gap >= 10):
                strengths.append(f"{dim.name}({dim.score}分，{dim.grade_label})")
            if dim.score < 60 or (dim.gap is not None and dim.gap <= -10):
                weaknesses.append(f"{dim.name}({dim.score}分，{dim.grade_label})")
            if dim.score < 50 or dim.grade == "D":
                risks.append(f"{dim.name}得分较低({dim.score}分)，存在{dim.grade_label}风险")
        
        # 生成评分逻辑说明（透明性）
        explanation_parts = [
            f"综合得分采用加权平均法计算，当前阶段({stage})各维度权重如下：",
        ]
        for dim in dimensions_result:
            explanation_parts.append(
                f"  - {dim.name}：权重{dim.weight:.0%}，得分{dim.score}分"
            )
        explanation_parts.append(f"\n评分过程中，对于未提供数据的指标采用默认值，已明确标注。")
        explanation_parts.append(f"综合得分 = {' + '.join([f'{d.score}×{d.weight:.2f}' for d in dimensions_result])} = {total_score}分")
        
        scoring_explanation = "\n".join(explanation_parts)
        
        return EvaluationResult(
            evaluation_id=str(uuid.uuid4()),
            company=company,
            total_score=total_score,
            overall_grade=overall_grade,
            overall_grade_label=overall_grade_label,
            stage_weights=weights,
            dimensions=dimensions_result,
            strengths=strengths,
            weaknesses=weaknesses,
            risks=risks,
            evaluator=request.evaluator,
            evaluation_date=request.evaluation_date or datetime.now(),
            scoring_explanation=scoring_explanation
        )
    
    def evaluate_simple(self, request: SimpleEvaluationRequest) -> EvaluationResult:
        """简化版评测：每个维度提供一个总分数，自动分配到所有三级指标
        
        将简化请求转换为完整的 EvaluationRequest，复用现有的 evaluate 逻辑。
        
        Args:
            request: 简化评测请求
            
        Returns:
            完整评测结果
        """
        # 构建完整的 dimensions 结构
        dimensions = []
        
        for dim_id, score in request.dimension_scores.items():
            dim_data = self.indicators.get(dim_id)
            if not dim_data:
                continue
            
            sub_indicators = []
            for sub_id, sub_def in dim_data["sub_indicators"].items():
                items = []
                for ind_id, ind_def in sub_def["indicators"].items():
                    items.append(IndicatorItemInput(
                        indicator_id=ind_id,
                        score=score,  # 将该维度分数分配给所有三级指标
                        notes="简化评测自动分配"
                    ))
                sub_indicators.append(SubIndicatorInput(
                    sub_indicator_id=sub_id,
                    items=items
                ))
            
            dimensions.append(DimensionInput(
                dimension_id=dim_id,
                sub_indicators=sub_indicators
            ))
        
        # 对未评分的维度自动使用默认值（不添加到 dimensions 中）
        full_request = EvaluationRequest(
            company=request.company,
            dimensions=dimensions,
            evaluator=request.evaluator
        )
        
        return self.evaluate(full_request)
    
    # ============================================================
    # 基准数据与辅助方法
    # ============================================================
    
    def get_benchmarks(self, stage: str) -> List[Dict[str, Any]]:
        """获取同阶段基准数据
        
        Args:
            stage: 发展阶段
            
        Returns:
            基准数据列表
        """
        if stage not in self.benchmarks:
            return []
        
        benchmarks = []
        for dim_id, score in self.benchmarks[stage].items():
            dim_data = self.indicators.get(dim_id, {})
            benchmarks.append({
                "stage": stage,
                "dimension_id": dim_id,
                "dimension_name": dim_data.get("name", ""),
                "avg_score": score,
                "p75_score": round(score + 10, 2),
                "p90_score": round(score + 20, 2),
                "sample_size": 100,  # 模拟样本量
            })
        return benchmarks
    
    def get_all_benchmarks(self) -> List[Dict[str, Any]]:
        """获取所有阶段的基准数据"""
        all_benchmarks = []
        for stage in self.benchmarks:
            all_benchmarks.extend(self.get_benchmarks(stage))
        return all_benchmarks
    
    def get_stage_definitions(self) -> List[Dict[str, Any]]:
        """获取发展阶段定义列表"""
        stage_names = {
            "seed": "种子期",
            "angel": "天使期",
            "pre-a": "Pre-A轮",
            "a-round": "A轮"
        }
        stage_descriptions = {
            "seed": "企业处于初创阶段，核心任务是验证商业模式和构建核心团队",
            "angel": "企业已验证商业模式，正在建立基础管理体系",
            "pre-a": "企业业务快速增长，需要为A轮融资做充分准备",
            "a-round": "企业已具备一定规模，开始对接资本市场"
        }
        stage_characteristics = {
            "seed": ["生存底线", "产品验证", "核心团队组建"],
            "angel": ["体系建设", "初步规模化", "管理规范化"],
            "pre-a": ["跃迁准备", "高速增长", "融资准备"],
            "a-round": ["资本对接", "规模扩张", "治理完善"]
        }
        
        result = []
        for stage_id, weights in self.stage_weights.items():
            result.append({
                "stage_id": stage_id,
                "name": stage_names.get(stage_id, stage_id),
                "description": stage_descriptions.get(stage_id, ""),
                "weights": weights,
                "characteristics": stage_characteristics.get(stage_id, [])
            })
        return result
    
    # ============================================================
    # 评测结果查询（模拟数据库存储）
    # ============================================================
    
    _evaluation_results: Dict[str, EvaluationResult] = {}
    
    def save_evaluation(self, result: EvaluationResult) -> str:
        """保存评测结果到内存存储
        
        实际生产环境应持久化到数据库。
        
        Args:
            result: 评测结果
            
        Returns:
            评测ID
        """
        self._evaluation_results[result.evaluation_id] = result
        return result.evaluation_id
    
    def get_evaluation(self, evaluation_id: str) -> Optional[EvaluationResult]:
        """获取已保存的评测结果
        
        Args:
            evaluation_id: 评测ID
            
        Returns:
            评测结果，不存在则返回None
        """
        return self._evaluation_results.get(evaluation_id)
