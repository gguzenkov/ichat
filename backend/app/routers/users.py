from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from datetime import datetime, timedelta
import shutil
import os
from pathlib import Path

router = APIRouter()

ACTIVE_TIMEOUT = 300  # 5 минут неактивности для выхода из списка активных

@router.get("/users/me")
def read_user_me():
    return {"message": "Текущий пользователь"}

@router.get("/users")
def read_users():
    return {"message": "Список пользователей"}

@router.get("/users/active")
async def get_active_users(db: Session = Depends(get_db)):
    try:
        # Уменьшим таймаут до 2 минут для тестирования
        cutoff_time = datetime.utcnow() - timedelta(seconds=120)
        active_users = db.query(User).filter(User.last_active > cutoff_time).all()
        
        print(f"Active users found: {len(active_users)}")  # Для отладки
        for user in active_users:
            print(f"User {user.username} last active: {user.last_active}")  # Для отладки
        
        return [
            {
                "id": user.id,
                "username": user.username,
                "avatar_url": user.avatar_url,
                "last_active": user.last_active.isoformat()
            }
            for user in active_users
        ]
    except Exception as e:
        print(f"Ошибка при получении активных пользователей: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при получении списка пользователей")

@router.post("/users/{user_id}/heartbeat")
async def update_user_activity(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
            
        user.last_active = datetime.utcnow()
        db.commit()
        
        return {"status": "ok"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Ошибка при обновлении активности пользователя: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при обновлении активности")

@router.get("/users/{user_id}")
async def get_user_info(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar_url": user.avatar_url
    }

@router.post("/users/{user_id}/avatar")
async def upload_avatar(
    user_id: int,
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Проверяем расширение файла
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
        file_ext = Path(avatar.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Неподдерживаемый формат файла")
        
        # Путь к директории с аватарами (относительно корня проекта)
        avatar_dir = Path(__file__).parent.parent.parent / "uploads" / "avatars"
        avatar_dir.mkdir(parents=True, exist_ok=True)
        
        # Генерируем имя файла
        avatar_name = f"avatar_{user_id}{file_ext}"
        avatar_path = avatar_dir / avatar_name
        
        # Сохраняем файл
        with avatar_path.open("wb") as buffer:
            content = await avatar.read()
            buffer.write(content)
        
        # Обновляем путь к аватару в БД (используем URL путь)
        user.avatar_url = f"/avatars/{avatar_name}"
        db.commit()
        
        return {"avatar_url": user.avatar_url}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error uploading avatar: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при загрузке аватара")

@router.post("/users/{user_id}/change-password")
async def change_password(
    user_id: int,
    password_data: dict,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Проверяем текущий пароль
    if not verify_password(password_data["current_password"], user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный текущий пароль")
    
    # Обновляем пароль
    user.hashed_password = get_password_hash(password_data["new_password"])
    db.commit()
    
    return {"message": "Пароль успешно изменен"} 