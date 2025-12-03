from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app import models, schemas

# 创建/录入一条健康调查记录
def create_survey(db: Session, survey: schemas.WellbeingSurveyCreate):
    student = db.query(models.Student).filter(models.Student.student_number == survey.student_number).first()
    if not student:
        return None
    
    db_survey = models.WellbeingSurvey(
        student_id=student.id,
        week_number=survey.week_number,
        stress_level=survey.stress_level,
        hours_slept=survey.hours_slept
    )
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return db_survey

# 获取每周的平均健康数据 (用于趋势图)
def get_weekly_analytics(db: Session):
    """
    返回: List of {week_number, avg_stress, avg_sleep}
    """
    results = db.query(
        models.WellbeingSurvey.week_number,
        func.avg(models.WellbeingSurvey.stress_level).label("avg_stress"),
        func.avg(models.WellbeingSurvey.hours_slept).label("avg_sleep")
    ).group_by(models.WellbeingSurvey.week_number)\
     .order_by(models.WellbeingSurvey.week_number)\
     .all()
    
    return results

# 获取处于“风险”状态的学生
def get_at_risk_students(db: Session, stress_threshold: int = 4, sleep_threshold: float = 5.0):
    """
    筛选规则: 压力 >= 4 OR 睡眠 < 5小时
    仅返回最近一周的数据，或者所有历史高危数据
    """
    # 查找所有符合风险阈值的记录，并关联出学生信息
    risky_records = db.query(models.WellbeingSurvey)\
        .join(models.Student)\
        .filter(
            (models.WellbeingSurvey.stress_level >= stress_threshold) | 
            (models.WellbeingSurvey.hours_slept < sleep_threshold)
        )\
        .order_by(desc(models.WellbeingSurvey.week_number))\
        .all()
        
    return risky_records

# 根据学号查询
def get_surveys_by_student_number(db: Session, student_number: str):
    return db.query(models.WellbeingSurvey)\
        .join(models.Student)\
        .filter(models.Student.student_number == student_number)\
        .order_by(models.WellbeingSurvey.week_number)\
        .all()