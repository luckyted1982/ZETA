# AI驱动的科创企业评测系统 - FastAPI后端

## 项目概述

为科创企业提供多维度评测、AI深度诊断和基准对比服务的FastAPI后端系统。

## 文件结构

```
backend/
├── .env                    # 环境变量（需手动创建，见下方说明）
├── .env.example            # 环境变量模板
├── config.py               # 配置管理
├── evaluation_engine.py    # 评测引擎核心
├── main.py                 # FastAPI主应用
├── models.py               # Pydantic数据模型
├── requirements.txt        # 依赖列表
└── README.md               # 本文件
```

## 环境变量配置

**重要**：`.env` 文件无法通过代码自动创建，请手动在项目根目录创建 `.env` 文件，内容如下：

```env
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true
```

> **注意**：请将 `your-api-key-here` 替换为你的真实 DeepSeek API Key。

## 快速启动

### 1. 安装依赖

```bash
cd "D:\工作\AI Infra产业创新中心\嘉创\科技服务产品体系\ai-evaluation-platform\backend"
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动，API文档访问：`http://localhost:8000/docs`

## API接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/evaluate` | 提交评测问卷，返回评测结果 |
| POST | `/api/v1/evaluate/{id}/ai-diagnosis` | 基于评测结果生成AI深度诊断报告 |
| GET | `/api/v1/evaluation/{id}` | 获取评测结果 |
| GET | `/api/v1/dimensions` | 获取所有评测维度定义 |
| GET | `/api/v1/stages` | 获取发展阶段定义和权重 |
| GET | `/api/v1/benchmarks` | 获取同阶段企业基准数据 |
| GET | `/health` | 健康检查 |

## 评测示例

### 提交评测请求

```bash
curl -X POST "http://localhost:8000/api/v1/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "company": {
      "name": "示例科技有限公司",
      "stage": "seed",
      "industry": "人工智能",
      "founded_year": 2023,
      "employees": 15,
      "location": "北京",
      "description": "专注于AI视觉识别技术的初创企业"
    },
    "dimensions": [
      {
        "dimension_id": "rd_innovation",
        "sub_indicators": [
          {
            "sub_indicator_id": "1.1",
            "items": [
              {"indicator_id": "1.1.1", "score": 75, "evidence": "研发费用占营收25%"},
              {"indicator_id": "1.1.2", "score": 80, "evidence": "研发人员占40%"}
            ]
          }
        ]
      }
    ],
    "evaluator": "评测专员"
  }'
```

### 生成AI诊断报告

```bash
curl -X POST "http://localhost:8000/api/v1/evaluate/{evaluation_id}/ai-diagnosis"
```

将 `{evaluation_id}` 替换为上一步返回的评测ID。

## 核心特性

- **8大维度评测**：研发创新、知识产权、资质培育、融资估值、法律治理、财务税务、上市准备、人才资源
- **阶段权重体系**：种子/天使/Pre-A/A轮差异化权重
- **数据贫乏处理**：支持A轮前企业部分指标缺失，自动使用默认值
- **评分透明可解释**：每个分数都有明确的评分依据和评分标准
- **动态权重调整**：支持运行时修改阶段权重配置
- **同阶段基准对比**：自动对比同阶段企业平均水平
- **AI深度诊断**：集成DeepSeek API，生成5000字个性化诊断报告

## 技术栈

- FastAPI 0.104.1
- Pydantic v2
- Uvicorn
- httpx（DeepSeek API调用）
- python-dotenv
