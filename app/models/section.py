from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import enum
from app.core.database import Base

class SectionType(enum.Enum):
    SINGLE_LINE = "single_line"
    DOUBLE_LINE = "double_line"
    MULTIPLE_LINE = "multiple_line"

class Section(Base):
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True, index=True)
    section_code = Column(String(20), unique=True, index=True, nullable=False)
    section_name = Column(String(100), nullable=False)
    section_type = Column(String(20), default="single_line")
    
    # Geographic information
    start_station = Column(String(50), nullable=False)
    end_station = Column(String(50), nullable=False)
    length_km = Column(Float, nullable=False)
    
    # Operational parameters
    max_speed_limit = Column(Integer, default=100)  # km/h
    signal_spacing_km = Column(Float, default=2.0)
    has_automatic_signaling = Column(Boolean, default=False)
    
    # Capacity information
    max_trains_per_hour = Column(Integer, default=6)
    has_crossing_station = Column(Boolean, default=True)
    crossing_station_name = Column(String(50))
    
    # Infrastructure details
    electrified = Column(Boolean, default=True)
    gauge_type = Column(String(20), default="broad_gauge")  # broad_gauge, meter_gauge, narrow_gauge
    
    # Operational constraints
    maintenance_windows = Column(JSON)  # Store maintenance time windows
    weather_restrictions = Column(JSON)  # Weather-based speed restrictions
    
    # Status
    is_active = Column(Boolean, default=True)
    current_occupancy = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    trains = relationship("Train", back_populates="current_section")
    schedules = relationship("Schedule", back_populates="section")
    
    def __repr__(self):
        return f"<Section {self.section_code}: {self.start_station} - {self.end_station}>"
    
    @property
    def is_congested(self):
        """Check if section is at or near capacity"""
        return self.current_occupancy >= self.max_trains_per_hour * 0.8
    
    @property
    def utilization_percentage(self):
        """Calculate current utilization percentage"""
        if self.max_trains_per_hour == 0:
            return 0
        return (self.current_occupancy / self.max_trains_per_hour) * 100
    
    def can_accommodate_train(self, train_type="passenger"):
        """Check if section can accommodate another train"""
        if not self.is_active:
            return False
        
        # Check basic capacity
        if self.current_occupancy >= self.max_trains_per_hour:
            return False
        
        # Additional checks based on train type
        if train_type == "freight" and not self.electrified:
            return False
            
        return True
    
    def get_travel_time_minutes(self, train_speed_kmh=None):
        """Calculate estimated travel time through section"""
        if train_speed_kmh is None:
            train_speed_kmh = self.max_speed_limit
        
        # Use the minimum of train speed and section speed limit
        effective_speed = min(train_speed_kmh, self.max_speed_limit)
        
        if effective_speed == 0:
            return float('inf')
        
        # Time = Distance / Speed (in hours), convert to minutes
        travel_time_hours = self.length_km / effective_speed
        return travel_time_hours * 60
