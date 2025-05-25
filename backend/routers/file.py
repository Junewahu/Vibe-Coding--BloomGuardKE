from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..auth import get_current_active_user
from ..models.user import User
from ..models.file import FileType, FileStatus, FileAccessLevel
from ..services.file import file_service
from ..schemas.file import (
    FileCreate, FileUpdate, FileResponse,
    FileVersionResponse, FileShareCreate, FileShareResponse,
    FileAccessCreate, FileAccessResponse, FolderCreate,
    FolderResponse, FileStats
)

router = APIRouter(prefix="/files", tags=["files"])

# File endpoints
@router.post("", response_model=FileResponse)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    folder_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a new file."""
    try:
        return await file_service.create_file(
            db,
            file,
            current_user.id,
            folder_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a file by ID."""
    file = file_service.get_file(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check access
    if file.user_id != current_user.id and not file.is_public:
        access = file_service.get_file_access(db, file_id, current_user.id)
        if not access:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return file

@router.get("", response_model=List[FileResponse])
async def get_user_files(
    file_type: Optional[FileType] = Query(None, description="Filter by file type"),
    status: Optional[FileStatus] = Query(None, description="Filter by status"),
    folder_id: Optional[int] = Query(None, description="Filter by folder"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's files with optional filters."""
    return file_service.get_user_files(
        db,
        current_user.id,
        file_type=file_type,
        status=status,
        folder_id=folder_id
    )

@router.put("/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: int,
    file_update: FileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a file."""
    file = file_service.get_file(db, file_id)
    if not file or file.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="File not found")
    
    updated_file = await file_service.update_file(db, file_id, file_update)
    return updated_file

@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a file."""
    file = file_service.get_file(db, file_id)
    if not file or file.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="File not found")
    
    success = await file_service.delete_file(db, file_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete file")
    return {"message": "File deleted successfully"}

# File Version endpoints
@router.post("/{file_id}/versions", response_model=FileVersionResponse)
async def create_file_version(
    file_id: int,
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new file version."""
    original_file = file_service.get_file(db, file_id)
    if not original_file or original_file.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        return await file_service.create_file_version(
            db,
            file_id,
            current_user.id,
            file
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{file_id}/versions", response_model=List[FileVersionResponse])
async def get_file_versions(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get versions for a file."""
    file = file_service.get_file(db, file_id)
    if not file or file.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file_service.get_file_versions(db, file_id)

# File Share endpoints
@router.post("/{file_id}/shares", response_model=FileShareResponse)
async def create_file_share(
    file_id: int,
    share_data: FileShareCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new file share."""
    file = file_service.get_file(db, file_id)
    if not file or file.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        return await file_service.create_file_share(
            db,
            file_id,
            share_data,
            current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{file_id}/shares", response_model=List[FileShareResponse])
async def get_file_shares(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get shares for a file."""
    file = file_service.get_file(db, file_id)
    if not file or file.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file_service.get_file_shares(db, file_id)

# File Access endpoints
@router.post("/{file_id}/access", response_model=FileAccessResponse)
async def create_file_access(
    file_id: int,
    access_data: FileAccessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new file access control."""
    file = file_service.get_file(db, file_id)
    if not file or file.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        return await file_service.create_file_access(
            db,
            file_id,
            access_data,
            current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{file_id}/access", response_model=List[FileAccessResponse])
async def get_file_access(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get access controls for a file."""
    file = file_service.get_file(db, file_id)
    if not file or file.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file_service.get_file_access(db, file_id)

# Folder endpoints
@router.post("/folders", response_model=FolderResponse)
async def create_folder(
    folder_data: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new folder."""
    try:
        return await file_service.create_folder(
            db,
            folder_data,
            current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/folders/{folder_id}", response_model=FolderResponse)
async def get_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a folder by ID."""
    folder = file_service.get_folder(db, folder_id)
    if not folder or folder.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder

@router.get("/folders", response_model=List[FolderResponse])
async def get_user_folders(
    parent_id: Optional[int] = Query(None, description="Filter by parent folder"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's folders."""
    return file_service.get_user_folders(
        db,
        current_user.id,
        parent_id=parent_id
    )

# Statistics endpoint
@router.get("/stats", response_model=FileStats)
async def get_file_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive file statistics."""
    try:
        return await file_service.get_file_stats(db, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 