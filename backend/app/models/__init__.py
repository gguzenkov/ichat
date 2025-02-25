from sqlalchemy.orm import relationship
from .user import User
from .message import Message
from .private_message import PrivateMessage
from .message_attachment import MessageAttachment
from .private_message_attachment import PrivateMessageAttachment

__all__ = [
    'User', 
    'Message', 
    'PrivateMessage',
    'MessageAttachment',
    'PrivateMessageAttachment'
]

# Устанавливаем отношения после определения всех классов
User.sent_messages = relationship(
    "PrivateMessage",
    foreign_keys="[PrivateMessage.sender_id]",
    back_populates="sender"
)
User.received_messages = relationship(
    "PrivateMessage",
    foreign_keys="[PrivateMessage.receiver_id]",
    back_populates="receiver"
) 