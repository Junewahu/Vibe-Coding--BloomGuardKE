from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
import secrets
import hashlib
import json
from ..models.security import (
    Role, Permission, APIKey, AuditLog, SecurityPolicy,
    PermissionType, ResourceType
)
from ..schemas.security import (
    RoleCreate, RoleUpdate,
    PermissionCreate, PermissionUpdate,
    APIKeyCreate, APIKeyUpdate,
    AuditLogCreate, SecurityPolicyCreate,
    SecurityPolicyUpdate
)

logger = logging.getLogger(__name__)

class SecurityService:
    async def create_role(
        self,
        db: Session,
        role_data: Dict[str, Any]
    ) -> Role:
        """Create a new role."""
        try:
            role = Role(**role_data)
            db.add(role)
            db.commit()
            db.refresh(role)
            return role
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating role: {str(e)}")
            raise

    async def get_role(
        self,
        db: Session,
        role_id: int
    ) -> Optional[Role]:
        """Get a role by ID."""
        return db.query(Role).filter(Role.id == role_id).first()

    async def get_roles(
        self,
        db: Session,
        is_active: Optional[bool] = None,
        is_system: Optional[bool] = None
    ) -> List[Role]:
        """Get roles with optional filters."""
        query = db.query(Role)
        if is_active is not None:
            query = query.filter(Role.is_active == is_active)
        if is_system is not None:
            query = query.filter(Role.is_system == is_system)
        return query.all()

    async def update_role(
        self,
        db: Session,
        role_id: int,
        role_data: Dict[str, Any]
    ) -> Optional[Role]:
        """Update a role."""
        try:
            role = await self.get_role(db, role_id)
            if role and not role.is_system:
                for key, value in role_data.items():
                    setattr(role, key, value)
                db.commit()
                db.refresh(role)
            return role
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating role: {str(e)}")
            raise

    async def create_permission(
        self,
        db: Session,
        permission_data: Dict[str, Any]
    ) -> Permission:
        """Create a new permission."""
        try:
            permission = Permission(**permission_data)
            db.add(permission)
            db.commit()
            db.refresh(permission)
            return permission
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating permission: {str(e)}")
            raise

    async def get_permission(
        self,
        db: Session,
        permission_id: int
    ) -> Optional[Permission]:
        """Get a permission by ID."""
        return db.query(Permission).filter(Permission.id == permission_id).first()

    async def get_permissions(
        self,
        db: Session,
        permission_type: Optional[PermissionType] = None,
        resource_type: Optional[ResourceType] = None,
        is_active: Optional[bool] = None
    ) -> List[Permission]:
        """Get permissions with optional filters."""
        query = db.query(Permission)
        if permission_type:
            query = query.filter(Permission.permission_type == permission_type)
        if resource_type:
            query = query.filter(Permission.resource_type == resource_type)
        if is_active is not None:
            query = query.filter(Permission.is_active == is_active)
        return query.all()

    async def update_permission(
        self,
        db: Session,
        permission_id: int,
        permission_data: Dict[str, Any]
    ) -> Optional[Permission]:
        """Update a permission."""
        try:
            permission = await self.get_permission(db, permission_id)
            if permission and not permission.is_system:
                for key, value in permission_data.items():
                    setattr(permission, key, value)
                db.commit()
                db.refresh(permission)
            return permission
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating permission: {str(e)}")
            raise

    async def create_api_key(
        self,
        db: Session,
        user_id: int,
        api_key_data: Dict[str, Any]
    ) -> APIKey:
        """Create a new API key."""
        try:
            # Generate API key and secret
            key = secrets.token_urlsafe(32)
            secret = secrets.token_urlsafe(32)
            
            # Hash the key and secret
            hashed_key = hashlib.sha256(key.encode()).hexdigest()
            hashed_secret = hashlib.sha256(secret.encode()).hexdigest()
            
            # Create API key
            api_key = APIKey(
                user_id=user_id,
                key=hashed_key,
                secret=hashed_secret,
                **api_key_data
            )
            db.add(api_key)
            db.commit()
            db.refresh(api_key)
            
            # Add the original key and secret to the response
            api_key.key = key
            api_key.secret = secret
            return api_key
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating API key: {str(e)}")
            raise

    async def get_api_key(
        self,
        db: Session,
        api_key_id: int
    ) -> Optional[APIKey]:
        """Get an API key by ID."""
        return db.query(APIKey).filter(APIKey.id == api_key_id).first()

    async def get_user_api_keys(
        self,
        db: Session,
        user_id: int,
        is_active: Optional[bool] = None
    ) -> List[APIKey]:
        """Get API keys for a user."""
        query = db.query(APIKey).filter(APIKey.user_id == user_id)
        if is_active is not None:
            query = query.filter(APIKey.is_active == is_active)
        return query.all()

    async def update_api_key(
        self,
        db: Session,
        api_key_id: int,
        api_key_data: Dict[str, Any]
    ) -> Optional[APIKey]:
        """Update an API key."""
        try:
            api_key = await self.get_api_key(db, api_key_id)
            if api_key:
                for key, value in api_key_data.items():
                    setattr(api_key, key, value)
                db.commit()
                db.refresh(api_key)
            return api_key
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating API key: {str(e)}")
            raise

    async def validate_api_key(
        self,
        db: Session,
        key: str,
        secret: str,
        ip_address: Optional[str] = None
    ) -> Optional[APIKey]:
        """Validate an API key."""
        hashed_key = hashlib.sha256(key.encode()).hexdigest()
        hashed_secret = hashlib.sha256(secret.encode()).hexdigest()
        
        api_key = db.query(APIKey).filter(
            APIKey.key == hashed_key,
            APIKey.secret == hashed_secret,
            APIKey.is_active == True
        ).first()
        
        if not api_key:
            return None
            
        # Check expiration
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return None
            
        # Check IP whitelist
        if api_key.ip_whitelist and ip_address and ip_address not in api_key.ip_whitelist:
            return None
            
        # Update last used timestamp
        api_key.last_used_at = datetime.utcnow()
        db.commit()
        
        return api_key

    async def create_audit_log(
        self,
        db: Session,
        audit_log_data: Dict[str, Any]
    ) -> AuditLog:
        """Create a new audit log entry."""
        try:
            audit_log = AuditLog(**audit_log_data)
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            return audit_log
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating audit log: {str(e)}")
            raise

    async def get_audit_logs(
        self,
        db: Session,
        user_id: Optional[int] = None,
        api_key_id: Optional[int] = None,
        resource_type: Optional[ResourceType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs with optional filters."""
        query = db.query(AuditLog)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if api_key_id:
            query = query.filter(AuditLog.api_key_id == api_key_id)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()

    async def create_security_policy(
        self,
        db: Session,
        policy_data: Dict[str, Any]
    ) -> SecurityPolicy:
        """Create a new security policy."""
        try:
            policy = SecurityPolicy(**policy_data)
            db.add(policy)
            db.commit()
            db.refresh(policy)
            return policy
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating security policy: {str(e)}")
            raise

    async def get_security_policy(
        self,
        db: Session,
        policy_id: int
    ) -> Optional[SecurityPolicy]:
        """Get a security policy by ID."""
        return db.query(SecurityPolicy).filter(SecurityPolicy.id == policy_id).first()

    async def get_security_policies(
        self,
        db: Session,
        policy_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[SecurityPolicy]:
        """Get security policies with optional filters."""
        query = db.query(SecurityPolicy)
        if policy_type:
            query = query.filter(SecurityPolicy.policy_type == policy_type)
        if is_active is not None:
            query = query.filter(SecurityPolicy.is_active == is_active)
        return query.all()

    async def update_security_policy(
        self,
        db: Session,
        policy_id: int,
        policy_data: Dict[str, Any]
    ) -> Optional[SecurityPolicy]:
        """Update a security policy."""
        try:
            policy = await self.get_security_policy(db, policy_id)
            if policy:
                for key, value in policy_data.items():
                    setattr(policy, key, value)
                db.commit()
                db.refresh(policy)
            return policy
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating security policy: {str(e)}")
            raise

    async def get_security_stats(
        self,
        db: Session
    ) -> Dict[str, Any]:
        """Get comprehensive security statistics."""
        try:
            # Get role statistics
            total_roles = db.query(Role).count()
            role_distribution = {}
            for role in db.query(Role).all():
                count = db.query(func.count(user_roles.c.user_id)).filter(
                    user_roles.c.role_id == role.id
                ).scalar()
                role_distribution[role.name] = count

            # Get permission statistics
            total_permissions = db.query(Permission).count()
            permission_distribution = {}
            for permission in db.query(Permission).all():
                count = db.query(func.count(role_permissions.c.role_id)).filter(
                    role_permissions.c.permission_id == permission.id
                ).scalar()
                permission_distribution[permission.name] = count

            # Get API key statistics
            total_api_keys = db.query(APIKey).count()
            active_api_keys = db.query(APIKey).filter(APIKey.is_active == True).count()

            # Get audit log statistics
            total_audit_logs = db.query(AuditLog).count()
            audit_logs_by_action = {}
            audit_logs_by_status = {}
            
            for log in db.query(AuditLog).all():
                audit_logs_by_action[log.action] = audit_logs_by_action.get(log.action, 0) + 1
                audit_logs_by_status[log.status] = audit_logs_by_status.get(log.status, 0) + 1

            # Get recent audit logs
            recent_logs = db.query(AuditLog).order_by(
                AuditLog.created_at.desc()
            ).limit(10).all()

            # Get active security policies
            security_policies = db.query(SecurityPolicy).filter(
                SecurityPolicy.is_active == True
            ).all()

            return {
                "total_roles": total_roles,
                "total_permissions": total_permissions,
                "total_api_keys": total_api_keys,
                "active_api_keys": active_api_keys,
                "total_audit_logs": total_audit_logs,
                "audit_logs_by_action": audit_logs_by_action,
                "audit_logs_by_status": audit_logs_by_status,
                "recent_audit_logs": recent_logs,
                "security_policies": security_policies,
                "role_distribution": role_distribution,
                "permission_distribution": permission_distribution
            }
        except Exception as e:
            logger.error(f"Error getting security stats: {str(e)}")
            raise

# Create singleton instance
security_service = SecurityService() 