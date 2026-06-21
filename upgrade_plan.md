# AI科创企业评测系统 - 第二阶段升级计划

## 目标
在现有8维度评测系统基础上，增加AI赋能功能，建设总体工作台、企业库、知识库、评测标准解释四大模块。

## 架构设计

### 后端架构
```
backend/
├── database/              # 数据库层
│   ├── db.py              # SQLAlchemy引擎和会话管理
│   ├── models.py          # 数据库模型（企业、评测、报告、文档、知识库）
│   └── migrations/        # Alembic迁移
├── ai/                    # AI模块
│   ├── deepseek_client.py # DeepSeek API客户端封装
│   ├── prompts.py         # Prompt模板（调研报告、文档解析、知识库RAG）
│   ├── conversation.py    # 对话状态管理
│   └── document_parser.py # 文档解析（PDF/DOC/Excel/TXT）
├── knowledge_base/        # 知识库模块
│   ├── vector_store.py    # 向量数据库（ChromaDB）
│   ├── rag_engine.py      # RAG检索引擎
│   └── document_loader.py # 文档加载和分块
├── services/              # 业务服务层
│   ├── company_service.py # 企业库CRUD
│   ├── evaluation_service.py # 评测服务
│   └── report_service.py # 报告导出
├── routers/               # API路由
│   ├── companies.py       # 企业库路由
│   ├── ai_assistant.py    # AI评测助手路由
│   ├── knowledge_base.py  # 知识库路由
│   ├── standards.py       # 评测标准解释路由
│   └── documents.py       # 文档上传路由
├── main.py                # 主入口
└── config.py              # 配置
```

### 数据库模型
```sql
-- 企业表
companies: id, name, industry, stage, founded_year, employees, location, 
           description, qualifications, tech_direction, funding_status,
           created_at, updated_at

-- 评测记录表
evaluations: id, company_id, dimension_scores, total_score, overall_grade,
             stage_weights, strengths, weaknesses, risks, ai_diagnosis,
             evaluation_date, created_at

-- 对话记录表
conversations: id, session_id, messages, current_task, status, 
               generated_report, extracted_scores, created_at

-- 文档表
documents: id, filename, original_path, parsed_text, file_type, 
           company_id, upload_date, status

-- 知识库文档表
knowledge_docs: id, title, doc_type, category, content, vector_id,
                source_url, created_at, updated_at

-- 评测标准解释表
standards: id, dimension_id, indicator_id, name, description, 
           scoring_criteria, examples, references, created_at
```

### 前端架构
```
frontend/src/
├── pages/                 # 页面路由
│   ├── Dashboard.jsx      # 总体工作台（首页）
│   ├── AIAssistant.jsx    # AI评测助手对话页
│   ├── CompanyLibrary.jsx # 企业库
│   ├── KnowledgeBase.jsx  # 知识库
│   └── Standards.jsx      # 评测标准解释
├── components/            # 组件
│   ├── AIChatWindow.jsx   # AI对话窗
│   ├── ReportPreview.jsx  # 报告预览（支持导出）
│   ├── ScoreImportModal.jsx # 导入评分弹窗
│   ├── FileUploadZone.jsx # 文件上传区
│   ├── CompanyCard.jsx    # 企业卡片
│   ├── KnowledgeCard.jsx  # 知识卡片
│   ├── StandardDetail.jsx # 标准详情
│   └── Sidebar.jsx        # 侧边导航
└── services/
    ├── aiService.js       # AI对话API
    ├── companyService.js  # 企业库API
    ├── knowledgeService.js # 知识库API
    └── standardsService.js # 标准API
```

## 实施阶段

### Stage 1: 基础设施（数据库+AI客户端）
- 安装依赖：SQLAlchemy, Alembic, ChromaDB, PyPDF2, python-docx, openpyxl
- 创建数据库模型和迁移
- 封装DeepSeek API客户端（支持流式输出）
- 创建Prompt模板

### Stage 2: AI评测助手（核心功能）
- 对话管理API（会话创建、消息发送、状态管理）
- 企业调研报告生成Prompt（8维度深度分析）
- 评分自动提取和导入
- 文件上传和解析（PDF/DOC/Excel/TXT）
- 基于文档的8维度分析报告
- 报告导出（Markdown → PDF）

### Stage 3: 企业库
- 企业CRUD API
- 评测历史记录
- 报告导出功能
- 基于历史修改再评测

### Stage 4: 知识库
- 知识库文档上传和管理
- 向量存储（ChromaDB）
- RAG检索引擎
- 接入AI问答（基于知识库）

### Stage 5: 评测标准解释
- 8维度标准数据录入
- AI增强的标准解释（大模型生成示例和深度说明）
- 标准搜索和浏览

### Stage 6: 前端页面
- 总体工作台Dashboard
- AI评测助手对话页
- 企业库页面
- 知识库页面
- 评测标准解释页
- 侧边导航和路由

### Stage 7: 联调与部署
- 前后端联调
- 测试脚本
- 启动脚本更新
- Demo部署

## 关键技术决策

### 数据库
- SQLite（开发阶段，足够简单，后续可迁移到PostgreSQL）
- SQLAlchemy ORM + Alembic迁移

### 向量数据库
- ChromaDB（轻量，Python原生，无需额外服务）

### 文档解析
- PyPDF2 / pdfplumber → PDF
- python-docx → DOCX
- openpyxl → Excel
- 纯文本 → TXT/Markdown

### AI流式输出
- FastAPI SSE (Server-Sent Events) 流式返回AI响应
- 前端 EventSource 接收流式数据

### 报告导出
- 前端浏览器打印（当前）
- 后端生成PDF（reportlab，后续）
- Markdown导出（当前优先）

## 预估工时
- Stage 1: 2h
- Stage 2: 4h
- Stage 3: 2h
- Stage 4: 3h
- Stage 5: 2h
- Stage 6: 5h
- Stage 7: 2h
- Total: ~20h

## 风险点
- 大模型API调用成本（每次调研报告约4000 tokens，需控制）
- 文档解析质量（PDF扫描件需要OCR，暂不支持）
- 向量数据库数据量（初期控制在1000条以内，ChromaDB可处理）
