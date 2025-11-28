import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 导入你的应用和数据库设置 (稍后我们会创建这些文件)
from app.main import app
from app.database import Base, get_db

# 1. 使用内存数据库 SQLite (速度快，测试完自动清空)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. 定义 Fixture：每次测试前建表，测试后删表
@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine) # 建表
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine) # 删表

# 3. 覆盖 FastAPI 的依赖项，使用测试数据库
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client