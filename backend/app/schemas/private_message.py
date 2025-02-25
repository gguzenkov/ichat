from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .message import AttachmentBase

class PrivateMessageBase(BaseModel):
    content: str

class PrivateMessageCreate(PrivateMessageBase):
    receiver_id: int
    attachments: List[AttachmentBase] = []

class PrivateMessage(PrivateMessageBase):
    id: int
    sender_id: int
    receiver_id: int
    created_at: datetime
    is_read: bool
    attachments: List[AttachmentBase] = []
    sender_username: Optional[str]
    receiver_username: Optional[str]
    sender_avatar: Optional[str]
    receiver_avatar: Optional[str]

    class Config:
        orm_mode = True 