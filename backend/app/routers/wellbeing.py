from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

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

# --- 2. 获取风险预警名单 ---
@router.get("/dashboard/alerts", response_model=List[schemas.WellbeingRiskOut])
def read_at_risk_students(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_wellbeing_officer)
):
    """
    获取最近触发 '高压力' 或 '低睡眠' 警报的学生名单。
    """
    return crud_wellbeing.get_at_risk_students(db)

# --- 3. 录入新的调查数据 ---
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