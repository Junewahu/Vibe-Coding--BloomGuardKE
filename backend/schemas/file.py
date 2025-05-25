from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from ..models.file import FileType, FileStatus, FileAccessLevel

# File schemas
class FileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    file_type: FileType
    mime_type: str
    size: int
    is_public: bool = False
    metadata: Optional[Dict[str, Any]] = None

class FileCreate(FileBase):
    folder_id: Optional[int] = None

class FileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_public: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    folder_id: Optional[int] = None

class FileResponse(FileBase):
    id: int
    original_name: str
    path: str
    status: FileStatus
    user_id: int
    folder_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        orm_mode = True

# File Version schemas
class FileVersionBase(BaseModel):
    version_number: int
    size: int
    metadata: Optional[Dict[str, Any]] = None

class FileVersionCreate(FileVersionBase):
    pass

class FileVersionResponse(FileVersionBase):
    id: int
    file_id: int
    user_id: int
    path: str
    created_at: datetime

    class Config:
        orm_mode = True

# File Share schemas
class FileShareBase(BaseModel):
    access_level: FileAccessLevel = FileAccessLevel.READ
    expires_at: Optional[datetime] = None
    is_active: bool = True

class FileShareCreate(FileShareBase):
    user_id: int

class FileShareUpdate(BaseModel):
    access_level: Optional[FileAccessLevel] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class FileShareResponse(FileShareBase):
    id: int
    file_id: int
    user_id: int
    shared_by_id: int
    share_token: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# File Access schemas
class FileAccessBase(BaseModel):
    access_level: FileAccessLevel

class FileAccessCreate(FileAccessBase):
    user_id: int

class FileAccessUpdate(BaseModel):
    access_level: Optional[FileAccessLevel] = None

class FileAccessResponse(FileAccessBase):
    id: int
    file_id: int
    user_id: int
    granted_by_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Folder schemas
class FolderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    is_public: bool = False

class FolderCreate(FolderBase):
    parent_id: Optional[int] = None

class FolderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_public: Optional[bool] = None
    parent_id: Optional[int] = None

class FolderResponse(FolderBase):
    id: int
    path: str
    user_id: int
    parent_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        orm_mode = True

# Statistics schema
class FileStats(BaseModel):
    total_files: int
    total_size: int
    files_by_type: Dict[str, int]
    files_by_status: Dict[str, int]
    recent_files: List[FileResponse]
    shared_files: List[FileResponse]
    public_files: List[FileResponse]
    folders: List[FolderResponse] 