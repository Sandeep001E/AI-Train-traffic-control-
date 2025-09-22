from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class ScheduleStatus(enum.Enum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)

    train_id = Column(Integer, ForeignKey("trains.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)

    planned_entry = Column(DateTime, nullable=False)
    planned_exit = Column(DateTime, nullable=False)

    actual_entry = Column(DateTime)
    actual_exit = Column(DateTime)

    platform = Column(String(10))
    track = Column(String(10))

    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.PLANNED)

    dwell_time_minutes = Column(Float, default=0.0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    train = relationship("Train", back_populates="schedules")
    section = relationship("Section", back_populates="schedules")

    def __repr__(self):
        return f"<Schedule Train {self.train_id} Section {self.section_id} {self.planned_entry} -> {self.planned_exit}>"
