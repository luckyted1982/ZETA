"""
评测标准数据初始化
预先录入8维度55指标的评测标准解释数据
"""

import sys
import os

# 添加backend目录到路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from database.db import SessionLocal
from database.models import Standard

STANDARDS_DATA = [
    # ========== 维度1: 研发创新能力 ==========
    {
        "dimension_id": "rd_innovation",
        "sub_indicator_id": "1.1",
        "indicator_id": "1.1.1",
        "name": "研发费用占比",
        "description": "企业研发费用占营业收入的比例",
        "scoring_criteria": "≥20%得100分；15-20%得80分；10-15%得60分；5-10%得40分；<5%得20分",
        "scoring_examples": "例：A企业年营收5000万，研发投入1200万，占比24%，得分100分。例：B企业年营收3000万，研发投入200万，占比6.7%，得分40分。",
        "importance_level": "high",
    },
    {
        "dimension_id": "rd_innovation",
        "sub_indicator_id": "1.1",
        "indicator_id": "1.1.2",
        "name": "研发人员占比",
        "description": "研发人员占总员工人数的比例",
        "scoring_criteria": "≥30%得100分；20-30%得80分；10-20%得60分；5-10%得40分；<5%得20分",
        "scoring_examples": "高新技术企业认定要求研发人员占比≥10%。",
        "importance_level": "high",
    },
    {
        "dimension_id": "rd_innovation",
        "sub_indicator_id": "1.2",
        "indicator_id": "1.2.1",
        "name": "立项规范性",
        "description": "研发项目的立项是否规范，是否有明确的立项报告和审批流程",
        "scoring_criteria": "有完整立项制度和执行记录得100分；有制度未完全执行得70分；制度不完整得40分；无制度得20分",
        "scoring_examples": "",
        "importance_level": "medium",
    },
    {
        "dimension_id": "rd_innovation",
        "sub_indicator_id": "1.3",
        "indicator_id": "1.3.1",
        "name": "技术路线清晰度",
        "description": "企业是否有明确的技术路线图，包括3-5年技术规划",
        "scoring_criteria": "有清晰技术路线图且文档化得100分；有规划未文档化得70分；有大致方向得40分；无明确规划得20分",
        "scoring_examples": "",
        "importance_level": "high",
    },
    {
        "dimension_id": "rd_innovation",
        "sub_indicator_id": "1.4",
        "indicator_id": "1.4.1",
        "name": "敏捷/IPD融合",
        "description": "研发管理体系是否融合了敏捷开发或IPD等先进方法论",
        "scoring_criteria": "深度融合且有效运行得100分；初步运用得70分；了解但未实施得40分；传统瀑布模式得20分",
        "scoring_examples": "",
        "importance_level": "medium",
    },
    {
        "dimension_id": "rd_innovation",
        "sub_indicator_id": "1.5",
        "indicator_id": "1.5.1",
        "name": "专利检索能力",
        "description": "企业是否具备专利检索和分析能力，是否使用专业工具",
        "scoring_criteria": "有专业检索能力并使用工具得100分；使用免费工具得70分；偶尔检索得40分；从不关注得20分",
        "scoring_examples": "",
        "importance_level": "medium",
    },
    # ========== 维度2: 知识产权实力 ==========
    {
        "dimension_id": "ip_protection",
        "sub_indicator_id": "2.1",
        "indicator_id": "2.1.1",
        "name": "发明专利占比",
        "description": "发明专利占全部专利的比例",
        "scoring_criteria": "≥60%得100分；40-60%得80分；20-40%得60分；10-20%得40分；<10%得20分",
        "scoring_examples": "发明专利技术含量更高，保护期限20年。实用新型和外观设计的保护期限仅10年。",
        "importance_level": "high",
    },
    {
        "dimension_id": "ip_protection",
        "sub_indicator_id": "2.2",
        "indicator_id": "2.2.1",
        "name": "专利数量",
        "description": "企业拥有的专利总数（包括申请中和已授权）",
        "scoring_criteria": "≥50件得100分；20-50件得80分；10-20件得60分；5-10件得40分；<5件得20分",
        "scoring_examples": "高新技术企业认定要求：发明专利1件以上或实用新型/软著6件以上。",
        "importance_level": "high",
    },
    {
        "dimension_id": "ip_protection",
        "sub_indicator_id": "2.3",
        "indicator_id": "2.3.1",
        "name": "质押融资",
        "description": "是否利用知识产权进行质押融资",
        "scoring_criteria": "已进行质押融资得100分；已评估但未融资得70分；有意向得40分；无考虑得20分",
        "scoring_examples": "",
        "importance_level": "medium",
    },
    {
        "dimension_id": "ip_protection",
        "sub_indicator_id": "2.4",
        "indicator_id": "2.4.1",
        "name": "开源许可证审查",
        "description": "是否对使用的开源组件进行许可证合规审查",
        "scoring_criteria": "有完整审查制度和工具得100分；有制度得70分；了解但未实施得40分；无关注得20分",
        "scoring_examples": "GPL许可证具有传染性，使用GPL代码可能导致整个产品需要开源。",
        "importance_level": "high",
    },
    {
        "dimension_id": "ip_protection",
        "sub_indicator_id": "2.5",
        "indicator_id": "2.5.1",
        "name": "保密制度",
        "description": "是否建立完善的商业秘密保护制度",
        "scoring_criteria": "有完善制度且执行得100分；有制度得70分；初步建立得40分；无制度得20分",
        "scoring_examples": "",
        "importance_level": "medium",
    },
    # ========== 维度3: 资质培育进度 ==========
    {
        "dimension_id": "qualification_progress",
        "sub_indicator_id": "3.1",
        "indicator_id": "3.1.1",
        "name": "科技型中小企业",
        "description": "是否获得科技型中小企业认定",
        "scoring_criteria": "已获认定得100分；已申请待审批得70分；准备申请得40分；未考虑得20分",
        "scoring_examples": "科技型中小企业可享受研发费用加计扣除比例提高到100%的税收优惠。",
        "importance_level": "high",
    },
    {
        "dimension_id": "qualification_progress",
        "sub_indicator_id": "3.1",
        "indicator_id": "3.1.2",
        "name": "高新技术企业",
        "description": "是否获得高新技术企业认定",
        "scoring_criteria": "已获认定得100分；已申请待审批得70分；准备申请得40分；未考虑得20分",
        "scoring_examples": "高新技术企业可享受15%企业所得税优惠税率（正常为25%）。",
        "importance_level": "high",
    },
    {
        "dimension_id": "qualification_progress",
        "sub_indicator_id": "3.2",
        "indicator_id": "3.2.1",
        "name": "路线图清晰度",
        "description": "资质进阶路线图是否清晰",
        "scoring_criteria": "有清晰路线图和明确计划得100分；有大致规划得70分；了解但不系统得40分；无规划得20分",
        "scoring_examples": "典型路径：科技型中小企业 → 高新技术企业 → 专精特新 → 小巨人 → 单项冠军。",
        "importance_level": "high",
    },
    {
        "dimension_id": "qualification_progress",
        "sub_indicator_id": "3.3",
        "indicator_id": "3.3.1",
        "name": "加计扣除",
        "description": "是否正确享受研发费用加计扣除政策",
        "scoring_criteria": "正确享受且全额得100分；部分享受得70分；了解但未申请得40分；不了解得20分",
        "scoring_examples": "科技型中小企业：研发费用按100%加计扣除。其他企业：按75%加计扣除。",
        "importance_level": "high",
    },
    {
        "dimension_id": "qualification_progress",
        "sub_indicator_id": "3.4",
        "indicator_id": "3.4.1",
        "name": "补贴申请",
        "description": "是否积极申请政府各类补贴",
        "scoring_criteria": "积极申请且获得多项得100分；偶尔申请得70分；了解但未申请得40分；不了解得20分",
        "scoring_examples": "常见补贴：研发补贴、人才补贴、房租补贴、设备补贴、贷款贴息等。",
        "importance_level": "medium",
    },
    # ========== 维度4: 融资与估值能力 ==========
    {
        "dimension_id": "financing_valuation",
        "sub_indicator_id": "4.1",
        "indicator_id": "4.1.1",
        "name": "轮次与金额",
        "description": "已完成融资的轮次和金额",
        "scoring_criteria": "已完成B轮以上且金额充足得100分；完成A轮得80分；完成天使轮得60分；种子轮得40分；未融资得20分",
        "scoring_examples": "",
        "importance_level": "high",
    },
    {
        "dimension_id": "financing_valuation",
        "sub_indicator_id": "4.2",
        "indicator_id": "4.2.1",
        "name": "同业对标",
        "description": "估值是否与同行业可比公司合理对标",
        "scoring_criteria": "估值合理且有对标分析得100分；大致合理得70分；偏高或偏低得40分；无概念得20分",
        "scoring_examples": "",
        "importance_level": "high",
    },
    {
        "dimension_id": "financing_valuation",
        "sub_indicator_id": "4.3",
        "indicator_id": "4.3.1",
        "name": "Runway月数",
        "description": "当前现金可支撑运营的月数",
        "scoring_criteria": "≥18个月得100分；12-18个月得80分；6-12个月得60分；3-6个月得40分；<3个月得20分",
        "scoring_examples": "Runway = 现金余额 / 月度烧钱率。建议保持至少12个月以上。",
        "importance_level": "high",
    },
    {
        "dimension_id": "financing_valuation",
        "sub_indicator_id": "4.4",
        "indicator_id": "4.4.1",
        "name": "BP质量",
        "description": "商业计划书的质量",
        "scoring_criteria": "专业且数据详实得100分；基本完整得70分；有但粗糙得40分；无BP得20分",
        "scoring_examples": "高质量BP应包含：市场分析、商业模式、竞争分析、财务预测、团队介绍、融资需求。",
        "importance_level": "high",
    },
    {
        "dimension_id": "financing_valuation",
        "sub_indicator_id": "4.5",
        "indicator_id": "4.5.1",
        "name": "创始人控股比例",
        "description": "创始人团队合计持股比例",
        "scoring_criteria": "≥50%得100分；34-50%得80分；20-34%得60分；10-20%得40分；<10%得20分",
        "scoring_examples": "建议创始人保持至少34%的持股比例（一票否决权线）。",
        "importance_level": "high",
    },
    # ========== 维度5: 法律治理合规 ==========
    {
        "dimension_id": "legal_governance",
        "sub_indicator_id": "5.1",
        "indicator_id": "5.1.1",
        "name": "公司治理结构",
        "description": "是否建立完善的公司治理结构（董事会、监事会、股东会）",
        "scoring_criteria": "治理完善且运行有效得100分；有基本结构得70分；结构不完整得40分；无治理结构得20分",
        "scoring_examples": "",
        "importance_level": "high",
    },
    {
        "dimension_id": "legal_governance",
        "sub_indicator_id": "5.2",
        "indicator_id": "5.2.1",
        "name": "合同管理制度",
        "description": "是否有完善的合同管理制度",
        "scoring_criteria": "有完善制度且执行得100分；有制度得70分；初步建立得40分；无制度得20分",
        "scoring_examples": "",
        "importance_level": "medium",
    },
    {
        "dimension_id": "legal_governance",
        "sub_indicator_id": "5.3",
        "indicator_id": "5.3.1",
        "name": "劳动法合规",
        "description": "劳动用工是否符合法律法规",
        "scoring_criteria": "完全合规得100分；基本合规得70分；有小问题得40分；存在风险得20分",
        "scoring_examples": "常见问题：未签劳动合同、社保公积金不足额缴纳、加班未支付加班费。",
        "importance_level": "high",
    },
    {
        "dimension_id": "legal_governance",
        "sub_indicator_id": "5.4",
        "indicator_id": "5.4.1",
        "name": "数据合规",
        "description": "是否建立数据安全和隐私保护合规体系",
        "scoring_criteria": "有完善体系且通过认证得100分；有制度得70分；了解但未实施得40分；无关注得20分",
        "scoring_examples": "",
        "importance_level": "high",
    },
    {
        "dimension_id": "legal_governance",
        "sub_indicator_id": "5.5",
        "indicator_id": "5.5.1",
        "name": "知识产权法务",
        "description": "知识产权法律风险管理",
        "scoring_criteria": "有完善法务体系得100分；有外部顾问得70分；有风险意识得40分；无关注得20分",
        "scoring_examples": "",
        "importance_level": "medium",
    },
    # ========== 维度6: 财务税务能力 ==========
    {
        "dimension_id": "financial_tax",
        "sub_indicator_id": "6.1",
        "indicator_id": "6.1.1",
        "name": "财务规范性",
        "description": "财务核算是否规范，是否使用专业财务软件",
        "scoring_criteria": "规范且使用专业软件得100分；基本规范得70分；有小问题得40分；混乱得20分",
        "scoring_examples": "",
        "importance_level": "high",
    },
    {
        "dimension_id": "financial_tax",
        "sub_indicator_id": "6.2",
        "indicator_id": "6.2.1",
        "name": "税务筹划",
        "description": "是否进行合理的税务筹划",
        "scoring_criteria": "有专业筹划且合规得100分；有基本筹划得70分；了解但未实施得40分；无关注得20分",
        "scoring_examples": "常见筹划：高新技术企业15%税率、研发费用加计扣除、小微企业优惠、留抵退税。",
        "importance_level": "high",
    },
    {
        "dimension_id": "financial_tax",
        "sub_indicator_id": "6.3",
        "indicator_id": "6.3.1",
        "name": "成本管理",
        "description": "是否有系统的成本管控体系",
        "scoring_criteria": "有完善体系且执行有效得100分；有基本管控得70分；初步建立得40分；无体系得20分",
        "scoring_examples": "",
        "importance_level": "medium",
    },
    {
        "dimension_id": "financial_tax",
        "sub_indicator_id": "6.4",
        "indicator_id": "6.4.1",
        "name": "财务预测",
        "description": "是否有财务预测和预算体系",
        "scoring_criteria": "有3年以上预测且定期更新得100分；有年度预算得70分；有粗略预测得40分；无预测得20分",
        "scoring_examples": "",
        "importance_level": "high",
    },
    # ========== 维度7: 上市准备度 ==========
    {
        "dimension_id": "ipo_readiness",
        "sub_indicator_id": "7.1",
        "indicator_id": "7.1.1",
        "name": "资本市场认知",
        "description": "对资本市场规则、流程、要求的了解程度",
        "scoring_criteria": "深入理解并有明确上市规划得100分；基本了解得70分；初步了解得40分；不了解得20分",
        "scoring_examples": "",
        "importance_level": "high",
    },
    {
        "dimension_id": "ipo_readiness",
        "sub_indicator_id": "7.2",
        "indicator_id": "7.2.1",
        "name": "合规基础",
        "description": "是否具备上市所需的基本合规条件",
        "scoring_criteria": "完全具备得100分；基本具备得70分；部分具备得40分；差距较大得20分",
        "scoring_examples": "上市基本要求：持续经营3年以上、主营业务清晰、无重大违法违规、财务规范。",
        "importance_level": "high",
    },
    {
        "dimension_id": "ipo_readiness",
        "sub_indicator_id": "7.3",
        "indicator_id": "7.3.1",
        "name": "中介机构",
        "description": "是否已聘请或接触保荐人、律师、会计师",
        "scoring_criteria": "已聘请且合作良好得100分；已接触得70分；有意向得40分；无考虑得20分",
        "scoring_examples": "",
        "importance_level": "medium",
    },
    {
        "dimension_id": "ipo_readiness",
        "sub_indicator_id": "7.4",
        "indicator_id": "7.4.1",
        "name": "时间规划",
        "description": "是否有明确的上市时间表和里程碑",
        "scoring_criteria": "有明确时间表且按计划推进得100分；有大致规划得70分；有意向但无计划得40分；无考虑得20分",
        "scoring_examples": "科创板/创业板IPO周期通常18-24个月。",
        "importance_level": "high",
    },
    # ========== 维度8: 人才资源 ==========
    {
        "dimension_id": "talent_resources",
        "sub_indicator_id": "8.1",
        "indicator_id": "8.1.1",
        "name": "创始人团队",
        "description": "创始人团队的背景、经验和互补性",
        "scoring_criteria": "顶尖背景且互补性强得100分；背景良好得80分；有基本经验得60分；背景较弱得40分；有明显短板得20分",
        "scoring_examples": "",
        "importance_level": "high",
    },
    {
        "dimension_id": "talent_resources",
        "sub_indicator_id": "8.2",
        "indicator_id": "8.2.1",
        "name": "核心人才",
        "description": "核心技术/业务人才的稳定性和竞争力",
        "scoring_criteria": "核心团队稳定且行业领先得100分；基本稳定得80分；有小流动得60分；流失严重得40分；核心人才缺失得20分",
        "scoring_examples": "",
        "importance_level": "high",
    },
    {
        "dimension_id": "talent_resources",
        "sub_indicator_id": "8.3",
        "indicator_id": "8.3.1",
        "name": "招聘体系",
        "description": "是否有系统的人才招聘和选拔体系",
        "scoring_criteria": "有完善体系且高效得100分；有基本流程得70分；初步建立得40分；无体系得20分",
        "scoring_examples": "",
        "importance_level": "medium",
    },
    {
        "dimension_id": "talent_resources",
        "sub_indicator_id": "8.4",
        "indicator_id": "8.4.1",
        "name": "激励机制",
        "description": "是否有有效的薪酬和股权激励机制",
        "scoring_criteria": "有完善激励体系且执行得100分；有股权激励得70分；有基本薪酬体系得40分；无激励得20分",
        "scoring_examples": "股权激励常见方式：期权池（通常10-15%）、限制性股票、虚拟股权。",
        "importance_level": "high",
    },
    {
        "dimension_id": "talent_resources",
        "sub_indicator_id": "8.5",
        "indicator_id": "8.5.1",
        "name": "组织文化",
        "description": "是否有积极的组织文化和价值观",
        "scoring_criteria": "文化鲜明且员工认同得100分；有基本文化得70分；初步建立得40分；无文化得20分",
        "scoring_examples": "",
        "importance_level": "medium",
    },
]


def init_standards():
    """初始化评测标准数据"""
    db = SessionLocal()
    try:
        # 检查是否已初始化
        count = db.query(Standard).count()
        if count > 0:
            print(f"评测标准数据已存在（{count}条），跳过初始化")
            return
        
        for data in STANDARDS_DATA:
            standard = Standard(**data)
            db.add(standard)
        
        db.commit()
        print(f"成功初始化 {len(STANDARDS_DATA)} 条评测标准数据")
    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_standards()
