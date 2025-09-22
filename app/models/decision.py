from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class DecisionType(enum.Enum):
    PRECEDENCE = "precedence"
    CROSSING = "crossing"
    HOLD = "hold"
    REROUTE = "reroute"

class DecisionStatus(enum.Enum):
    RECOMMENDED = "recommended"
    APPROVED = "approved"
    OVERRIDDEN = "overridden"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)

    decision_type = Column(Enum(DecisionType), nullable=False)
    status = Column(Enum(DecisionStatus), default=DecisionStatus.RECOMMENDED)

    train_id = Column(Integer, ForeignKey("trains.id"), nullable=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=True)

    details = Column(JSON)  # e.g., precedence order, crossing plan, hold durations
    explanation = Column(Text)

    recommended_by = Column(String(50), default="AI")
    approved_by = Column(String(50))

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    train = relationship("Train", back_populates="decisions")

    def __repr__(self):
        return f"<Decision {self.decision_type} status={self.status}>"
