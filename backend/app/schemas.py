from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Token Schemas ---
# 返回给前端的 响应模型
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str
# 后端验证 JWT 时使用的 内部数据模型
class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# --- Course Schemas ---
class CourseBase(BaseModel):
    code: str
    name: str

class CourseOut(CourseBase):
    id: int
    class Config:
        from_attributes = True

# --- Grade Schemas ---
class GradeOut(BaseModel):
    # course_name: str
    # student_name: str
    id: int
    student_id: int
    assignment_title: str
    score: float
    submission_date: datetime
    
    class Config:
        from_attributes = True

# 基础字段
class WellbeingSurveyBase(BaseModel):
    week_number: int
    stress_level: int
    hours_slept: float

# 创建时需要的字段 (输入)
class WellbeingSurveyCreate(WellbeingSurveyBase):
    student_number: str

# 返回给前端的字段 (输出)
class WellbeingSurveyOut(WellbeingSurveyBase):
    id: int
    recorded_at: datetime
    
    class Config:
        from_attributes = True

# Student Schemas
class StudentBasic(BaseModel):
    full_name: str
    student_number: str
    email: str
    
    class Config:
        from_attributes = True

# Risk Alert Schema (预警名单专用)
class WellbeingRiskOut(WellbeingSurveyOut):
    # 继承自 SurveyOut，并增加 student 信息
    student: StudentBasic