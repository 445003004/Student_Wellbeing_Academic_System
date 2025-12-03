from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io

from app import models, schemas
from app.database import get_db
# 引入权限依赖
from app.dependencies import require_wellbeing_officer
# 引入 CRUD
from app.crud import crud_wellbeing

router = APIRouter()

# --- 1. 获取仪表盘趋势数据 ---
@router.get("/dashboard/trends")
def read_wellbeing_trends(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_wellbeing_officer)
):
    """
    获取每周的平均压力和睡眠数据。
    前端可以用这个数据绘制 'Week 1-10' 的双折线图。
    """
    stats = crud_wellbeing.get_weekly_analytics(db)
    
    # 格式化返回数据以适配前端图表库
    return [
        {
            "week": r.week_number,
            "average_stress": round(r.avg_stress, 2),
            "average_sleep": round(r.avg_sleep, 2)
        }
        for r in stats
    ]

# 获取风险预警名单
@router.get("/dashboard/alerts", response_model=List[schemas.WellbeingRiskOut])
def read_at_risk_students(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_wellbeing_officer)
):
    """
    获取最近触发 '高压力' 或 '低睡眠' 警报的学生名单。
    """
    return crud_wellbeing.get_at_risk_students(db)

# 查询学生的调查数据
@router.get("/students/{student_number}/history")
def get_survey(
    student_number : str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_wellbeing_officer)
):
    """
    福利官用excel表收集学生一周的数据,导出csv文件
    用csv文件导入到数据库中
    """
    result = crud_wellbeing.get_surveys_by_student_number(db, student_number)
    if not result:
        raise HTTPException(status_code=404, detail="Student number not found")
    return result

# 录入新的调查数据
@router.post("/surveys", response_model=schemas.WellbeingSurveyOut)
def create_survey_entry(
    survey: schemas.WellbeingSurveyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_wellbeing_officer)
):
    """
    福利官手动录入学生的一条调查结果
    """
    result = crud_wellbeing.create_survey(db, survey)
    if not result:
        raise HTTPException(status_code=404, detail="Student number not found")
    return result

# CSV 批量导入
@router.post("/upload_csv")
def upload_surveys_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_wellbeing_officer)
):
    """
    允许 Welfare Officer 上传 CSV 文件批量导入数据。
    CSV 必须包含列: student_number, week_number, stress_level, hours_slept
    """
    # 1. 验证文件格式
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    try:
        # 2. 读取 CSV 内容
        contents = file.file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # 3. 验证必要的列是否存在
        required_columns = ['student_number', 'week_number', 'stress_level', 'hours_slept']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail=f"CSV must contain columns: {required_columns}")

        success_count = 0
        errors = []

        # 4. 遍历每一行并存入数据库
        for index, row in df.iterrows():
            # 构建 schema 对象
            survey_data = schemas.WellbeingSurveyCreate(
                student_number=str(row['student_number']), # 确保转为字符串
                week_number=int(row['week_number']),
                stress_level=int(row['stress_level']),
                hours_slept=float(row['hours_slept'])
            )
            
            # 调用之前的 CRUD 函数保存
            result = crud_wellbeing.create_survey(db, survey_data)
            
            if result:
                success_count += 1
            else:
                errors.append(f"Row {index+1}: Student {row['student_number']} not found.")

        return {
            "message": "Upload processed",
            "success_count": success_count,
            "errors": errors
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")