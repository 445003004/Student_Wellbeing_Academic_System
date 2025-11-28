from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user, require_course_director
from app.crud import crud_academic

router = APIRouter()

# --- 路由配置 ---
# 所有接口都需要: 1. 登录 2. 角色必须是 Course Director
@router.get("/courses", response_model=List[schemas.CourseOut]) # 需要在 schemas.py 定义 CourseOut
def read_courses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_course_director)
):
    """
    获取主管负责的所有课程列表
    """
    courses = crud_academic.get_all_courses(db)
    return courses

@router.get("/courses/{course_id}/dashboard")
def read_course_dashboard(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_course_director)
):
    """
    获取某门课程的仪表盘数据 (平均分、出勤率)
    用于前端绘制图表
    """
    course = crud_academic.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    analytics = crud_academic.get_course_analytics(db, course_id)
    
    return {
        "course_name": course.name,
        "course_code": course.code,
        "analytics": analytics
    }

@router.get("/courses/{course_id}/grades")
def read_grades(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_course_director)
):
    """
    查看该课程所有学生的详细成绩单
    """
    grades = crud_academic.get_course_grades(db, course_id)
    return grades