from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.message import Message
from ..models.user import User
from ..schemas import message as message_schemas
from typing import List
from datetime import datetime
import pytz  # Добавим для работы с часовыми поясами
import os
import uuid
from fastapi.responses import FileResponse
from ..models.message_attachment import MessageAttachment

router = APIRouter()

# Перемещаем функцию в начало, до её использования
async def get_current_user_id(request: Request) -> int:
    return request.state.current_user_id

# Создаем функцию для конвертации времени в московский часовой пояс
def convert_to_moscow_time(dt):
    moscow_tz = pytz.timezone('Europe/Moscow')
    if dt.tzinfo is None:  # Если время без часового пояса
        dt = pytz.UTC.localize(dt)
    return dt.astimezone(moscow_tz)

# Добавим конфигурацию для загрузки файлов
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/messages")
async def create_message(message: message_schemas.MessageCreate, db: Session = Depends(get_db)):
    try:
        print(f"Получено сообщение: {message}")  # Для отладки
        user = db.query(User).filter(User.id == message.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Обновляем время последней активности пользователя
        user.last_active = datetime.utcnow()
        
        # Создаем сообщение
        db_message = Message(
            content=message.content,
            user_id=message.user_id
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)

        # Добавляем вложения, если они есть
        attachments_data = []
        for attachment in message.attachments:
            db_attachment = MessageAttachment(
                message_id=db_message.id,
                file_path=attachment.file_path,
                file_name=attachment.file_name,
                file_size=attachment.file_size,
                file_type=attachment.file_type
            )
            db.add(db_attachment)
            attachments_data.append(attachment)
        
        db.commit()
        
        # Конвертируем время в московское
        moscow_time = convert_to_moscow_time(db_message.created_at)
        
        return {
            "id": db_message.id,
            "content": db_message.content,
            "user_id": db_message.user_id,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "created_at": moscow_time.isoformat(),
            "attachments": attachments_data
        }
    except Exception as e:
        print(f"Ошибка при создании сообщения: {str(e)}")  # Для отладки
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages")
async def get_messages(db: Session = Depends(get_db)):
    try:
        messages = db.query(Message).order_by(Message.created_at.desc()).all()
        result = []
        for msg in messages:
            message_data = {
                "id": msg.id,
                "content": msg.content,
                "user_id": msg.user_id,
                "username": msg.user.username,
                "avatar_url": msg.user.avatar_url,
                "created_at": convert_to_moscow_time(msg.created_at).isoformat(),
                "attachments": [
                    {
                        "file_path": attachment.file_path,
                        "file_name": attachment.file_name,
                        "file_size": attachment.file_size,
                        "file_type": attachment.file_type
                    }
                    for attachment in msg.attachments
                ] if msg.attachments else []
            }
            result.append(message_data)
        return result
    except Exception as e:
        print(f"Ошибка при получении сообщений: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int, 
    current_user_id: int = Query(..., description="ID текущего пользователя"),
    db: Session = Depends(get_db)
):
    try:
        # Находим сообщение
        message = db.query(Message).filter(Message.id == message_id).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="Сообщение не найдено")
            
        # Проверяем, является ли пользователь автором сообщения
        if message.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Нет прав для удаления этого сообщения")
            
        # Удаляем сообщение
        db.delete(message)
        db.commit()
        
        return {"message": "Сообщение успешно удалено"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при удалении сообщения")

@router.post("/messages/attachments")
async def upload_attachments(
    files: List[UploadFile] = File(...),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        if len(files) > 3:
            raise HTTPException(status_code=400, detail="Максимум 3 файла")

        attachments = []
        for file in files:
            try:
                content = await file.read()
                file_size = len(content)
                
                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Файл {file.filename} превышает максимальный размер 10MB"
                    )

                file_ext = os.path.splitext(file.filename)[1]
                unique_filename = f"{uuid.uuid4()}{file_ext}"
                file_path = os.path.join(UPLOAD_DIR, unique_filename)

                with open(file_path, "wb") as f:
                    f.write(content)

                relative_path = f"/uploads/{unique_filename}"
                
                attachments.append({
                    "file_path": relative_path,
                    "file_name": file.filename,
                    "file_size": file_size,
                    "file_type": file.content_type
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Ошибка при обработке файла {file.filename}")

        return {"attachments": attachments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages/{message_id}/attachments/{file_name}")
async def get_attachment(message_id: int, file_name: str):
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(file_path) 