from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# 数据库文件路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'evaluation.db')}"

# 确保数据目录存在
os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)

# 创建引擎（启用外键约束）
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基类
Base = declarative_base()


def get_db():
    """获取数据库会话（FastAPI依赖用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库，创建所有表"""
    from database.models import Company, EvaluationRecord, Conversation, Document, KnowledgeDoc, Standard  # noqa
    Base.metadata.create_all(bind=engine)
