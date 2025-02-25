from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class MessageAttachment(Base):
    __tablename__ = "message_attachments"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"))
    file_path = Column(String)
    file_name = Column(String)
    file_size = Column(Integer)
    file_type = Column(String)

    message = relationship("Message", back_populates="attachments") 