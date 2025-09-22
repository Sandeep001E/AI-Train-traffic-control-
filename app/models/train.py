from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class TrainType(enum.Enum):
    PASSENGER = "passenger"
    EXPRESS = "express"
    SUPERFAST = "superfast"
    FREIGHT = "freight"
    SPECIAL = "special"

class TrainStatus(enum.Enum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Priority(enum.Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class Train(Base):
    __tablename__ = "trains"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), unique=True, index=True, nullable=False)
    train_name = Column(String(100), nullable=False)
    train_type = Column(Enum(TrainType), nullable=False)
    
    # Current status and location
    status = Column(Enum(TrainStatus), default=TrainStatus.SCHEDULED)
    current_section_id = Column(Integer, ForeignKey("sections.id"))
    current_position_km = Column(Float, default=0.0)
    
    # Scheduling information
    scheduled_departure = Column(DateTime)
    actual_departure = Column(DateTime)
    scheduled_arrival = Column(DateTime)
    actual_arrival = Column(DateTime)
    
    # Priority and operational data
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    max_speed = Column(Integer, default=100)  # km/h
    length = Column(Float, default=0.0)  # meters
    weight = Column(Float, default=0.0)  # tonnes
    
    # Route information
    origin_station = Column(String(50))
    destination_station = Column(String(50))
    route_description = Column(Text)
    
    # Operational constraints
    is_passenger_train = Column(Boolean, default=True)
    requires_platform = Column(Boolean, default=True)
    can_use_loop_line = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    current_section = relationship("Section", back_populates="trains")
    schedules = relationship("Schedule", back_populates="train")
    decisions = relationship("Decision", back_populates="train")
    
    def __repr__(self):
        return f"<Train {self.train_number}: {self.train_name}>"
    
    @property
    def is_delayed(self):
        """Check if train is currently delayed"""
        return self.status == TrainStatus.DELAYED
    
    @property
    def delay_minutes(self):
        """Calculate delay in minutes"""
        if self.scheduled_arrival and self.actual_arrival:
            delta = self.actual_arrival - self.scheduled_arrival
            return int(delta.total_seconds() / 60)
        return 0
    
    def get_priority_score(self):
        """Get numerical priority score for optimization"""
        base_score = self.priority.value * 100
        
        # Adjust based on train type
        type_multiplier = {
            TrainType.PASSENGER: 1.5,
            TrainType.EXPRESS: 1.3,
            TrainType.SUPERFAST: 1.2,
            TrainType.FREIGHT: 0.8,
            TrainType.SPECIAL: 2.0
        }
        
        return base_score * type_multiplier.get(self.train_type, 1.0)
