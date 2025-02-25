from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models.private_message import PrivateMessage
from ..models.user import User
from ..models.private_message_attachment import PrivateMessageAttachment
from ..schemas import private_message as pm_schemas
from typing import List
from datetime import datetime
import pytz

router = APIRouter()

async def get_current_user_id(request: Request) -> int:
    return request.state.current_user_id

@router.get("/pm-chats")
async def get_private_chats(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        # Получаем всех пользователей, с которыми есть переписка
        chat_users_ids = db.query(PrivateMessage.sender_id, PrivateMessage.receiver_id).filter(
            (PrivateMessage.sender_id == current_user_id) | 
            (PrivateMessage.receiver_id == current_user_id)
        ).distinct().all()

        # Собираем уникальные ID пользователей
        user_ids = set()
        for sender_id, receiver_id in chat_users_ids:
            if sender_id != current_user_id:
                user_ids.add(sender_id)
            if receiver_id != current_user_id:
                user_ids.add(receiver_id)

        if not user_ids:
            return []

        # Получаем информацию о пользователях
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        
        chats = []
        for user in users:
            # Получаем последнее сообщение
            last_message = db.query(PrivateMessage).filter(
                ((PrivateMessage.sender_id == current_user_id) & 
                 (PrivateMessage.receiver_id == user.id)) |
                ((PrivateMessage.sender_id == user.id) & 
                 (PrivateMessage.receiver_id == current_user_id))
            ).order_by(PrivateMessage.created_at.desc()).first()

            if not last_message:
                continue

            # Получаем количество непрочитанных сообщений
            unread_count = db.query(PrivateMessage).filter(
                PrivateMessage.sender_id == user.id,
                PrivateMessage.receiver_id == current_user_id,
                PrivateMessage.is_read == False
            ).count()

            chats.append({
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "avatar_url": user.avatar_url
                },
                "lastMessage": {
                    "content": last_message.content,
                    "created_at": last_message.created_at.isoformat()
                },
                "unreadCount": unread_count
            })

        # Сортируем чаты по времени последнего сообщения
        chats.sort(key=lambda x: x["lastMessage"]["created_at"], reverse=True)
        return chats

    except Exception as e:
        print("Error in get_private_chats:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/private-messages-unread")
async def get_unread_messages_count(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        unread_counts = db.query(
            PrivateMessage.sender_id,
            func.count(PrivateMessage.id).label('count')
        ).filter(
            PrivateMessage.receiver_id == current_user_id,
            PrivateMessage.is_read == False
        ).group_by(PrivateMessage.sender_id).all()
        
        return {
            str(sender_id): count 
            for sender_id, count in unread_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/private-messages")
async def create_private_message(
    message: pm_schemas.PrivateMessageCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        # Проверяем существование получателя
        receiver = db.query(User).filter(User.id == message.receiver_id).first()
        if not receiver:
            raise HTTPException(status_code=404, detail="Получатель не найден")

        db_message = PrivateMessage(
            content=message.content,
            sender_id=current_user_id,
            receiver_id=message.receiver_id
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)

        # Добавляем вложения
        for attachment in message.attachments:
            db_attachment = PrivateMessageAttachment(
                message_id=db_message.id,
                file_path=attachment.file_path,
                file_name=attachment.file_name,
                file_size=attachment.file_size,
                file_type=attachment.file_type
            )
            db.add(db_attachment)
        
        db.commit()

        return {
            "id": db_message.id,
            "content": db_message.content,
            "sender_id": db_message.sender_id,
            "receiver_id": db_message.receiver_id,
            "created_at": db_message.created_at,
            "is_read": db_message.is_read,
            "attachments": message.attachments
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/private-messages/{user_id}")
async def get_private_messages(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    messages = db.query(PrivateMessage).filter(
        ((PrivateMessage.sender_id == current_user_id) & 
         (PrivateMessage.receiver_id == user_id)) |
        ((PrivateMessage.sender_id == user_id) & 
         (PrivateMessage.receiver_id == current_user_id))
    ).order_by(PrivateMessage.created_at).all()

    return [
        {
            "id": msg.id,
            "content": msg.content,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "created_at": msg.created_at,
            "is_read": msg.is_read,
            "attachments": [
                {
                    "file_path": attachment.file_path,
                    "file_name": attachment.file_name,
                    "file_size": attachment.file_size,
                    "file_type": attachment.file_type
                }
                for attachment in msg.attachments
            ]
        }
        for msg in messages
    ]

@router.put("/private-messages/{message_id}/read")
async def mark_message_as_read(
    message_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        message = db.query(PrivateMessage).filter(
            PrivateMessage.id == message_id,
            PrivateMessage.receiver_id == current_user_id
        ).first()

        if not message:
            raise HTTPException(status_code=404, detail="Сообщение не найдено")

        message.is_read = True
        db.commit()

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/private-messages/{message_id}")
async def delete_private_message(
    message_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        message = db.query(PrivateMessage).filter(
            PrivateMessage.id == message_id,
            # Проверяем, что пользователь является отправителем или получателем
            ((PrivateMessage.sender_id == current_user_id) | 
             (PrivateMessage.receiver_id == current_user_id))
        ).first()

        if not message:
            raise HTTPException(status_code=404, detail="Сообщение не найдено")

        db.delete(message)
        db.commit()

        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))