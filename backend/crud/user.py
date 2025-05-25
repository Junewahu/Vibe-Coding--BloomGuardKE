from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from .. import models, schemas
from ..auth import get_password_hash, verify_password

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get a user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a user by email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[str] = None
) -> List[models.User]:
    """Get all users with optional filters"""
    query = db.query(models.User)
    
    if search:
        search = f"%{search}%"
        query = query.filter(
            or_(
                models.User.first_name.ilike(search),
                models.User.last_name.ilike(search),
                models.User.email.ilike(search)
            )
        )
    
    if role:
        query = query.filter(models.User.role == role)
    
    return query.offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        metadata=user.metadata
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(
    db: Session,
    user_id: int,
    user: schemas.UserUpdate
) -> Optional[models.User]:
    """Update a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.dict(exclude_unset=True)
    
    # Handle password update separately
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True

def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> Optional[models.User]:
    """Authenticate a user"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_users_by_role(
    db: Session,
    role: str,
    skip: int = 0,
    limit: int = 100
) -> List[models.User]:
    """Get users by role"""
    return db.query(models.User)\
        .filter(models.User.role == role)\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_active_users(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[models.User]:
    """Get all active users"""
    return db.query(models.User)\
        .filter(models.User.is_active == True)\
        .offset(skip)\
        .limit(limit)\
        .all()

def deactivate_user(
    db: Session,
    user_id: int
) -> Optional[models.User]:
    """Deactivate a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.is_active = False
    db.commit()
    db.refresh(db_user)
    return db_user

def activate_user(
    db: Session,
    user_id: int
) -> Optional[models.User]:
    """Activate a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.is_active = True
    db.commit()
    db.refresh(db_user)
    return db_user

def change_user_password(
    db: Session,
    user_id: int,
    new_password: str
) -> Optional[models.User]:
    """Change a user's password"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_user_password(
    db: Session,
    user_id: int,
    password: str
) -> bool:
    """Verify a user's password"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    return verify_password(password, db_user.hashed_password) 