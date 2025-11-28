from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.config import get_settings

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """
    解码 JWT Token 并从数据库中查找当前用户。
    如果 Token 无效、过期或用户不存在，抛出 401 错误。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码 Token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # 获取用户名 (我们在 auth.py 中把 username 放入了 'sub' 字段)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        # 可选: 获取角色 (虽然我们主要靠数据库查，但也可以校验 Token 里的角色)
        # token_role: str = payload.get("role")
            
    except JWTError:
        # 如果 Token 过期或被篡改，decode 会抛出 JWTError
        raise credentials_exception

    # 从数据库查找用户
    user = db.query(models.User).filter(models.User.username == username).first()
    
    if user is None:
        raise credentials_exception
        
    return user

def require_course_director(current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.Role.COURSE_DIRECTOR:
        raise HTTPException(status_code=403, detail="Access forbidden: Course Directors only")
    return current_user

def require_wellbeing_officer(current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.Role.WELLBEING_OFFICER:
        raise HTTPException(status_code=403, detail="Access forbidden: Wellbeing Officers only")
    return current_user