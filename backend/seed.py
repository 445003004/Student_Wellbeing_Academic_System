import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# 导入你的应用模块
# 确保你在 backend/ 目录下运行此脚本，否则可能会报 ModuleNotFoundError
from app.database import SessionLocal, engine, Base
from app import models

# 初始化 Faker 和 密码加密器
fake = Faker()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def init_db():
    # 1. 创建数据库表 (如果不存在)
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 2. 清理旧数据 (为了避免重复运行导致数据堆积，先清空)
        print("Cleaning up old data...")
        db.query(models.WellbeingSurvey).delete()
        db.query(models.Grade).delete()
        db.query(models.Attendance).delete()
        db.execute(models.student_courses.delete()) # 清空多对多关联表
        db.query(models.Student).delete()
        db.query(models.Course).delete()
        db.query(models.User).delete()
        db.commit()

        # 3. 创建系统用户 (工作人员)
        print("Creating System Users (Staff)...")
        
        # Course Director 账号
        director = models.User(
            username="director",
            hashed_password=get_password_hash("director123"), # 演示用密码
            full_name="Dr. Alice Director",
            role=models.Role.COURSE_DIRECTOR
        )
        
        # Wellbeing Officer 账号
        officer = models.User(
            username="officer",
            hashed_password=get_password_hash("officer123"), # 演示用密码
            full_name="Mr. Bob Wellbeing",
            role=models.Role.WELLBEING_OFFICER
        )
        
        db.add(director)
        db.add(officer)
        db.commit()

        # 4. 创建课程 (Courses)
        print("Creating Courses...")
        courses_data = [
            {"code": "WM9QF", "name": "Programming for Artificial Intelligence"},
            {"code": "WM913", "name": "Data Science & Machine Learning"},
            {"code": "WM920", "name": "Software Engineering Principles"}
        ]
        
        courses = []
        for c_data in courses_data:
            course = models.Course(code=c_data["code"], name=c_data["name"])
            db.add(course)
            courses.append(course)
        db.commit()

        # 5. 创建学生 (Students)
        print("Creating 50 Students...")
        students = []
        for _ in range(50):
            student = models.Student(
                student_number=f"u{fake.unique.random_number(digits=7)}",
                full_name=fake.name(),
                email=fake.unique.email()
            )
            db.add(student)
            students.append(student)
        db.commit()

        # 6. 模拟选课、学术数据和健康数据
        print("Generating Analytics Data (Attendance, Grades, Wellbeing)...")
        
        # 配置: 生成过去 10 周的数据
        weeks = 10
        base_date = datetime.utcnow() - timedelta(weeks=weeks)

        for student in students:
            # --- A. 选课 (每个学生随机选 1-3 门课) ---
            num_courses = random.randint(1, 3)
            enrolled_courses = random.sample(courses, num_courses)
            student.enrolled_courses.extend(enrolled_courses)
            
            # --- B. 生成健康数据 (Wellbeing Officer 专属) ---
            # 模拟：有些学生压力大 (random high stress)，有些正常
            is_stressed_student = random.choice([True, False, False]) # 1/3 概率是压力生
            
            for w in range(weeks):
                week_date = base_date + timedelta(weeks=w)
                
                # 压力值逻辑: 压力生倾向于 4-5，普通生倾向于 1-3
                if is_stressed_student:
                    stress = random.choice([3, 4, 5, 5])
                    sleep = random.uniform(4.0, 6.5) # 睡得少
                else:
                    stress = random.choice([1, 2, 3])
                    sleep = random.uniform(6.5, 9.0) # 睡得好

                survey = models.WellbeingSurvey(
                    student_id=student.id,
                    week_number=w + 1,
                    stress_level=stress,
                    hours_slept=round(sleep, 1),
                    recorded_at=week_date
                )
                db.add(survey)

            # --- C. 生成学术数据 (Course Director 专属) ---
            for course in enrolled_courses:
                # 1. 出勤记录 (每门课过去 10 次课)
                # 模拟: 压力大的学生更容易缺勤
                attendance_prob = 0.7 if is_stressed_student else 0.95
                
                for w in range(weeks):
                    class_date = base_date + timedelta(weeks=w)
                    
                    rand_val = random.random()
                    if rand_val < attendance_prob:
                        status = models.AttendanceStatus.PRESENT
                    elif rand_val < attendance_prob + 0.05:
                        status = models.AttendanceStatus.LATE
                    else:
                        status = models.AttendanceStatus.ABSENT

                    att = models.Attendance(
                        student_id=student.id,
                        course_id=course.id,
                        date=class_date,
                        status=status
                    )
                    db.add(att)
                
                # 2. 成绩记录 (每门课 2 个 Assignment)
                # 模拟: 成绩波动
                base_score = random.randint(50, 90)
                if is_stressed_student: base_score -= 10 # 压力影响成绩
                
                for i in range(1, 3):
                    score = min(100, max(0, base_score + random.randint(-5, 10)))
                    grade = models.Grade(
                        student_id=student.id,
                        course_id=course.id,
                        assignment_title=f"Assignment {i}",
                        score=score,
                        submission_date=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                    )
                    db.add(grade)

        db.commit()
        print("✅ Database seeded successfully!")
        print("Login Credentials:")
        print(" -> Course Director:   username='director', password='director123'")
        print(" -> Wellbeing Officer: username='officer',  password='officer123'")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()