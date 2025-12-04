from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user, require_course_director
from app.crud import crud_academic

router = APIRouter()

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

# 预警名单接口
@router.get("/dashboard/alerts", response_model=List[schemas.AcademicRiskOut])
def read_academic_alerts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_course_director)
):
    """
    获取学术预警名单：只要有挂科记录的学生都会显示
    """
    # 不再需要传递 threshold=50.0，逻辑已在 CRUD 内部写死为检测挂科
    return crud_academic.get_academic_at_risk_students(db)

# 学生详情查询接口
@router.get("/students/{student_number}/details", response_model=schemas.StudentAcademicReport)
def read_student_details(
    student_number: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_course_director)
):
    """
    根据学号查询该学生的完整学术档案（所有课程成绩 + 出勤）
    """
    report = crud_academic.get_student_academic_details(db, student_number)
    if not report:
        raise HTTPException(status_code=404, detail="Student not found")
    return report