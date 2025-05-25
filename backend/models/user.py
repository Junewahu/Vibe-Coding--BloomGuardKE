from sqlalchemy import Column, String, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel
from ..database import Base

class UserRole(enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    RECEPTIONIST = "receptionist"
    CHW = "chw"  # Community Health Worker

class User(Base, BaseModel):
    """User model for managing staff and doctors"""
    
    # Basic Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(20))
    
    # Authentication
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), nullable=False)
    
    # Professional Information
    specialization = Column(String(100))  # For doctors
    license_number = Column(String(50))  # Medical license
    qualifications = Column(JSON)  # List of qualifications
    
    # Preferences
    notification_preferences = Column(JSON)  # Email, SMS, etc.
    working_hours = Column(JSON)  # Weekly schedule
    language_preference = Column(String(10), default="en")
    
    # Relationships
    appointments = relationship("Appointment", back_populates="doctor")
    
    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        data = super().to_dict()
        data["role"] = self.role.value
        # Remove sensitive information
        data.pop("hashed_password", None)
        return data 