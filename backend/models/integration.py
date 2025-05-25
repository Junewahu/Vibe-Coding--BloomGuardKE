from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Boolean, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel
from ..database import Base

class IntegrationType(str, enum.Enum):
    PAYMENT = "payment"
    LABORATORY = "laboratory"
    PHARMACY = "pharmacy"
    INSURANCE = "insurance"
    REFERRAL = "referral"
    CUSTOM = "custom"

class IntegrationStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    FAILED = "failed"

class IntegrationAuthType(str, enum.Enum):
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC = "basic"
    JWT = "jwt"
    CUSTOM = "custom"

class Integration(Base):
    """Model for third-party integrations"""
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    integration_type = Column(Enum(IntegrationType), nullable=False)
    description = Column(Text, nullable=True)
    base_url = Column(String(500), nullable=False)
    auth_type = Column(Enum(IntegrationAuthType), nullable=False)
    auth_config = Column(JSON, nullable=True)  # Store auth credentials securely
    headers = Column(JSON, nullable=True)  # Default headers
    status = Column(Enum(IntegrationStatus), default=IntegrationStatus.PENDING)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class APIRoute(Base):
    """Model for API routes"""
    __tablename__ = "api_routes"

    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)
    path = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE, etc.
    description = Column(Text, nullable=True)
    request_schema = Column(JSON, nullable=True)  # Request validation schema
    response_schema = Column(JSON, nullable=True)  # Response validation schema
    rate_limit = Column(Integer, nullable=True)  # Requests per minute
    timeout = Column(Integer, nullable=True)  # Request timeout in seconds
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    integration = relationship("Integration", back_populates="routes")

class APIRateLimit(Base):
    """Model for API rate limiting"""
    __tablename__ = "api_rate_limits"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("api_routes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional user-specific limits
    ip_address = Column(String(50), nullable=True)  # Optional IP-specific limits
    requests_count = Column(Integer, default=0)
    window_start = Column(DateTime, nullable=False)
    window_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    route = relationship("APIRoute", back_populates="rate_limits")

class APILog(Base):
    """Model for API request/response logging"""
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("api_routes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    request_id = Column(String(100), nullable=False)  # Unique request identifier
    method = Column(String(10), nullable=False)
    path = Column(String(500), nullable=False)
    request_headers = Column(JSON, nullable=True)
    request_body = Column(JSON, nullable=True)
    response_status = Column(Integer, nullable=True)
    response_headers = Column(JSON, nullable=True)
    response_body = Column(JSON, nullable=True)
    duration = Column(Float, nullable=True)  # Request duration in milliseconds
    error_message = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    route = relationship("APIRoute", back_populates="logs")

class APITransformation(Base):
    """Model for request/response transformations"""
    __tablename__ = "api_transformations"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("api_routes.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    transformation_type = Column(String(50), nullable=False)  # request/response
    transformation_script = Column(Text, nullable=False)  # JavaScript/JSON transformation
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    route = relationship("APIRoute", back_populates="transformations")

# Add relationships to Integration model
Integration.routes = relationship("APIRoute", back_populates="integration")

# Add relationships to APIRoute model
APIRoute.rate_limits = relationship("APIRateLimit", back_populates="route")
APIRoute.logs = relationship("APILog", back_populates="route")
APIRoute.transformations = relationship("APITransformation", back_populates="route") 