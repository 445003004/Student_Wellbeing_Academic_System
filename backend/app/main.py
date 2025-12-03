from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, academic, wellbeing
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Assessment Project for PAI",
    version=settings.VERSION
)

# CORS 配置 (允许 Vue 前端访问)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(academic.router, prefix="/academic", tags=["Academic (Director)"])
app.include_router(wellbeing.router, prefix="/wellbeing", tags=["Wellbeing (Officer)"])

@app.get("/")
def read_root():
    return {"message": "System is running"}

