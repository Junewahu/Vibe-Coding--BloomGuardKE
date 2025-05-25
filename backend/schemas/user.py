from pydantic import BaseModel, Field, EmailStr, constr
from typing import Optional, List, Dict, Any
from .base import BaseSchema

class UserBase(BaseModel):
    """Base user schema with common fields"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    role: str = Field(..., min_length=1, max_length=20)
    specialization: Optional[str] = Field(None, max_length=100)
    license_number: Optional[str] = Field(None, max_length=50)
    qualifications: Optional[List[str]] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    working_hours: Optional[Dict[str, Any]] = None
    language_preference: str = Field(default="en", min_length=2, max_length=10)

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100)

class UserUpdate(BaseModel):
    """Schema for updating an existing user"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    role: Optional[str] = Field(None, min_length=1, max_length=20)
    specialization: Optional[str] = Field(None, max_length=100)
    license_number: Optional[str] = Field(None, max_length=50)
    qualifications: Optional[List[str]] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    working_hours: Optional[Dict[str, Any]] = None
    language_preference: Optional[str] = Field(None, min_length=2, max_length=10)
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)

class UserInDB(UserBase, BaseSchema):
    """Schema for user data in database"""
    hashed_password: str
    is_active: bool = True

class User(UserInDB):
    """Schema for user response"""
    full_name: str
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None
    role: Optional[str] = None 