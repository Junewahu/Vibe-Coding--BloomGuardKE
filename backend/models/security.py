from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Boolean, Text, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel
from ..database import Base

# Association tables for many-to-many relationships
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class PermissionType(str, enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    MANAGE = "manage"
    APPROVE = "approve"
    EXPORT = "export"
    IMPORT = "import"
    CUSTOM = "custom"

class ResourceType(str, enum.Enum):
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    API_KEY = "api_key"
    INTEGRATION = "integration"
    REPORT = "report"
    DASHBOARD = "dashboard"
    EXPORT = "export"
    NOTIFICATION = "notification"
    AUDIT_LOG = "audit_log"
    CUSTOM = "custom"

class Role(Base):
    """Model for user roles"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False)  # System roles cannot be modified
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", secondary=user_roles, back_populates="roles")

class Permission(Base):
    """Model for permissions"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    permission_type = Column(Enum(PermissionType), nullable=False)
    resource_type = Column(Enum(ResourceType), nullable=False)
    resource_id = Column(Integer, nullable=True)  # Optional specific resource
    is_system = Column(Boolean, default=False)  # System permissions cannot be modified
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class APIKey(Base):
    """Model for API keys"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    key = Column(String(100), unique=True, nullable=False)  # Hashed API key
    secret = Column(String(100), nullable=False)  # Hashed secret
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    ip_whitelist = Column(JSON, nullable=True)  # List of allowed IP addresses
    rate_limit = Column(Integer, nullable=True)  # Requests per minute
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="api_keys")

class AuditLog(Base):
    """Model for audit logs"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=True)
    action = Column(String(100), nullable=False)  # e.g., "login", "create_user", "update_role"
    resource_type = Column(Enum(ResourceType), nullable=False)
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)  # Additional action details
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False)  # "success", "failure", "error"
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
    api_key = relationship("APIKey", back_populates="audit_logs")

class SecurityPolicy(Base):
    """Model for security policies"""
    __tablename__ = "security_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    policy_type = Column(String(50), nullable=False)  # e.g., "password", "session", "api"
    rules = Column(JSON, nullable=False)  # Policy rules and configurations
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Add relationships to User model
from .user import User
User.roles = relationship("Role", secondary=user_roles, back_populates="users")
User.api_keys = relationship("APIKey", back_populates="user")
User.audit_logs = relationship("AuditLog", back_populates="user")

# Add relationships to APIKey model
APIKey.audit_logs = relationship("AuditLog", back_populates="api_key") 