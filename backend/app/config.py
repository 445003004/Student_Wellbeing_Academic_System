from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # 项目基础信息
    PROJECT_NAME: str = "Student Wellbeing and Academic System"
    VERSION: str = "1.0.0"
    
    # 数据库配置 (默认为当前目录下的 sqlite 文件)
    DATABASE_URL: str = "qlite:///./student_system.db"
    
    # 安全配置 (JWT Token)
    SECRET_KEY: str = "CHANGE_THIS_TO_A_SUPER_SECRET_KEY_FOR_ASSESSMENT"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Token 有效期 60 分钟

    # 允许跨域的源 (Frontend URL)
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8081", "http://localhost:8080"]

    # 自动加载 .env 文件
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

# 使用 lru_cache 缓存配置，避免每次请求都读取文件
@lru_cache()
def get_settings():
    return Settings()