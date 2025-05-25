from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..database import get_db
from ..models.integration import IntegrationType, IntegrationStatus
from ..schemas.integration import (
    IntegrationCreate, IntegrationUpdate, IntegrationResponse,
    APIRouteCreate, APIRouteUpdate, APIRouteResponse,
    APIRateLimitCreate, APIRateLimitUpdate, APIRateLimitResponse,
    APILogCreate, APILogResponse,
    APITransformationCreate, APITransformationUpdate, APITransformationResponse,
    IntegrationStats
)
from ..services.integration import integration_service
from ..auth import get_current_user

router = APIRouter(prefix="/integrations", tags=["integrations"])

# Integration endpoints
@router.post("", response_model=IntegrationResponse)
async def create_integration(
    integration: IntegrationCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new integration."""
    try:
        return await integration_service.create_integration(db, integration.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get an integration by ID."""
    integration = await integration_service.get_integration(db, integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration

@router.get("", response_model=List[IntegrationResponse])
async def get_integrations(
    integration_type: Optional[IntegrationType] = None,
    status: Optional[IntegrationStatus] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get integrations with optional filters."""
    return await integration_service.get_integrations(db, integration_type, status)

@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: int,
    integration: IntegrationUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update an integration."""
    updated_integration = await integration_service.update_integration(
        db, integration_id, integration.dict(exclude_unset=True)
    )
    if not updated_integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return updated_integration

# API Route endpoints
@router.post("/routes", response_model=APIRouteResponse)
async def create_route(
    route: APIRouteCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new API route."""
    try:
        return await integration_service.create_route(db, route.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/routes/{route_id}", response_model=APIRouteResponse)
async def get_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get an API route by ID."""
    route = await integration_service.get_route(db, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route

@router.get("/{integration_id}/routes", response_model=List[APIRouteResponse])
async def get_integration_routes(
    integration_id: int,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get routes for an integration."""
    return await integration_service.get_integration_routes(db, integration_id, is_active)

@router.put("/routes/{route_id}", response_model=APIRouteResponse)
async def update_route(
    route_id: int,
    route: APIRouteUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update an API route."""
    updated_route = await integration_service.update_route(
        db, route_id, route.dict(exclude_unset=True)
    )
    if not updated_route:
        raise HTTPException(status_code=404, detail="Route not found")
    return updated_route

# API Request execution endpoint
@router.post("/routes/{route_id}/execute")
async def execute_request(
    route_id: int,
    method: str,
    path: str,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Execute an API request."""
    try:
        return await integration_service.execute_request(
            db,
            route_id,
            method,
            path,
            headers,
            body,
            current_user.get("id"),
            current_user.get("ip_address")
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# API Log endpoints
@router.get("/routes/{route_id}/logs", response_model=List[APILogResponse])
async def get_route_logs(
    route_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get logs for a route."""
    return await integration_service.get_route_logs(db, route_id, start_date, end_date, limit)

# API Transformation endpoints
@router.post("/routes/{route_id}/transformations", response_model=APITransformationResponse)
async def create_transformation(
    route_id: int,
    transformation: APITransformationCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new API transformation."""
    try:
        transformation_data = transformation.dict()
        transformation_data["route_id"] = route_id
        return await integration_service.create_transformation(db, transformation_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/routes/{route_id}/transformations", response_model=List[APITransformationResponse])
async def get_route_transformations(
    route_id: int,
    transformation_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get transformations for a route."""
    return await integration_service.get_route_transformations(
        db, route_id, transformation_type, is_active
    )

@router.put("/transformations/{transformation_id}", response_model=APITransformationResponse)
async def update_transformation(
    transformation_id: int,
    transformation: APITransformationUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update an API transformation."""
    updated_transformation = await integration_service.update_transformation(
        db, transformation_id, transformation.dict(exclude_unset=True)
    )
    if not updated_transformation:
        raise HTTPException(status_code=404, detail="Transformation not found")
    return updated_transformation

# Statistics endpoint
@router.get("/stats", response_model=IntegrationStats)
async def get_integration_stats(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get comprehensive integration statistics."""
    try:
        return await integration_service.get_integration_stats(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 