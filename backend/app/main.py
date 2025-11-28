from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, academic, wellbeing
from fastapi.middleware.cors import CORSMiddleware

# 自动创建表 (生产环境通常用 Alembic，原型可用这个)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Wellbeing & Academic System",
    description="Assessment Project for PAI",
    version="0.1.0"
)

# CORS 配置 (允许 Vue 前端访问)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vue 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(academic.router, prefix="/academic", tags=["Academic (Director)"])
app.include_router(wellbeing.router, prefix="/wellbeing", tags=["Wellbeing (Officer)"])
# app.include_router(students.router, prefix="/students", tags=["Student Management"])

@app.get("/")
def read_root():
    return {"message": "System is running"}

