from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas

# 获取所有课程列表
def get_all_courses(db: Session):
    return db.query(models.Course).all()

# 获取单门课程的详细信息
def get_course_by_id(db: Session, course_id: int):
    return db.query(models.Course).filter(models.Course.id == course_id).first()

# 获取课程的统计数据 (Dashboard 数据)
def get_course_analytics(db: Session, course_id: int):
    # 计算平均分
    # 查询该课程下所有 Grade 的平均 score
    avg_grade = db.query(func.avg(models.Grade.score))\
                  .filter(models.Grade.course_id == course_id)\
                  .scalar()

    # 计算出勤率
    # 总记录数
    total_attendance = db.query(models.Attendance)\
                         .filter(models.Attendance.course_id == course_id)\
                         .count()
    
    # 出勤(Present)的记录数
    present_count = db.query(models.Attendance)\
                      .filter(models.Attendance.course_id == course_id, 
                              models.Attendance.status == models.AttendanceStatus.PRESENT)\
                      .count()
    
    # 防止除以零
    attendance_rate = 0.0
    if total_attendance > 0:
        attendance_rate = (present_count / total_attendance) * 100

    student_count = db.query(models.Student)\
                      .join(models.student_courses)\
                      .filter(models.student_courses.c.course_id == course_id)\
                      .count()

    return {
        "average_grade": round(avg_grade, 2) if avg_grade else 0.0,
        "attendance_rate": round(attendance_rate, 1),
        "total_students_enrolled": student_count
    }

# 获取某门课的所有学生成绩 (用于列表展示)
def get_course_grades(db: Session, course_id: int):
    return db.query(models.Grade).filter(models.Grade.course_id == course_id).all()