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

# 根据学号获取详细学术信息 (成绩 + 出勤)
def get_student_academic_details(db: Session, student_number: str):
    # 查找学生
    student = db.query(models.Student).filter(models.Student.student_number == student_number).first()
    if not student:
        return None
    
    # 获取成绩 (关联课程信息)
    grades = db.query(models.Grade)\
        .join(models.Course)\
        .filter(models.Grade.student_id == student.id)\
        .order_by(models.Grade.submission_date.desc())\
        .all()
        
    # 获取出勤 (关联课程信息)
    attendances = db.query(models.Attendance)\
        .join(models.Course)\
        .filter(models.Attendance.student_id == student.id)\
        .order_by(models.Attendance.date.desc())\
        .all()

    # 格式化数据以符合 Schema (因为 ORM 对象直接转 Pydantic 有时需要手动处理关联字段的扁平化)
    formatted_grades = []
    for g in grades:
        # 确保 Course 已加载
        formatted_grades.append({
            "id": g.id,
            "student_id": g.student_id,
            "assignment_title": g.assignment_title,
            "score": g.score,
            "submission_date": g.submission_date,
            "course_name": g.course.name,
            "course_code": g.course.code
        })

    formatted_attendances = []
    for a in attendances:
        formatted_attendances.append({
            "id": a.id,
            "date": a.date,
            "status": a.status,
            "course_name": a.course.name,
            "course_code": a.course.code
        })

    return {
        "student": student,
        "grades": formatted_grades,
        "attendances": formatted_attendances
    }

# 获取成绩不达标的学生 (预警名单)
def get_academic_at_risk_students(db: Session):
    """
    筛选规则: 存在任意一门课程成绩 < 50 的学生
    """
    PASS_MARK = 50.0

    # 1. 找出所有有挂科记录的学生 ID (去重)
    failing_student_ids = db.query(models.Grade.student_id)\
        .filter(models.Grade.score < PASS_MARK)\
        .distinct()

    # 2. 查询这些学生的基础信息
    # 使用 in_ 操作符筛选
    at_risk_students = db.query(models.Student)\
        .filter(models.Student.id.in_(failing_student_ids))\
        .all()
    
    risk_list = []
    for student in at_risk_students:
        # 补充计算：平均分
        avg_score = db.query(func.avg(models.Grade.score))\
            .filter(models.Grade.student_id == student.id)\
            .scalar()
            
        # 补充计算：挂科数量
        fail_count = db.query(models.Grade)\
            .filter(models.Grade.student_id == student.id, models.Grade.score < PASS_MARK)\
            .count()
            
        risk_list.append({
            "student": student,
            "average_score": round(avg_score, 1) if avg_score else 0.0,
            "failed_courses_count": fail_count
        })
        
    # 按挂科数量降序排列，挂科越多的排越前
    risk_list.sort(key=lambda x: x['failed_courses_count'], reverse=True)
    
    return risk_list