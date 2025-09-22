from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=True)
    details = Column(JSON)

    ip_address = Column(String(45))
    user_agent = Column(String(255))

    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<AuditLog action={self.action} entity={self.entity_type}:{self.entity_id}>"
