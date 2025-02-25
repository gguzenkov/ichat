from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class AttachmentBase(BaseModel):
    file_path: str
    file_name: str
    file_size: int
    file_type: str

class MessageBase(BaseModel):
    content: str
    user_id: int

class MessageCreate(BaseModel):
    content: str = ''
    user_id: int
    attachments: List[AttachmentBase] = []

class Message(MessageCreate):
    id: int
    created_at: datetime
    username: str

    class Config:
        orm_mode = True 