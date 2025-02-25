from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class PrivateMessageAttachment(Base):
    __tablename__ = "private_message_attachments"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("private_messages.id", ondelete="CASCADE"))
    file_path = Column(String)
    file_name = Column(String)
    file_size = Column(Integer)
    file_type = Column(String)

    message = relationship("PrivateMessage", back_populates="attachments") 