from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..services.search import SearchService
from ..schemas.search import (
    SearchRequest, SearchResponse, SearchStats,
    SearchHistoryResponse, SearchSuggestionResponse,
    SearchFilterResponse, SearchAnalyticsResponse
)
from ..auth import get_current_user

router = APIRouter(
    prefix="/search",
    tags=["search"],
    dependencies=[Depends(get_current_user)]
)

@router.post("", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Perform a search across all indexed content."""
    search_service = SearchService(db)
    return await search_service.search(request, current_user.id)

@router.get("/suggestions", response_model=List[str])
async def get_suggestions(
    query: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get search suggestions based on the query."""
    search_service = SearchService(db)
    return await search_service.get_suggestions(query, current_user.id)

@router.get("/filters", response_model=List[SearchFilterResponse])
async def get_filters(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get available search filters for the user."""
    search_service = SearchService(db)
    return await search_service.get_available_filters(current_user.id)

@router.get("/history", response_model=List[SearchHistoryResponse])
async def get_search_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100)
):
    """Get user's search history."""
    search_service = SearchService(db)
    return await search_service.get_search_history(current_user.id, limit)

@router.get("/stats", response_model=SearchStats)
async def get_search_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get search statistics for the user."""
    search_service = SearchService(db)
    return await search_service.get_search_stats(current_user.id, days)

@router.post("/suggestions", response_model=SearchSuggestionResponse)
async def create_suggestion(
    suggestion: SearchSuggestionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new search suggestion."""
    search_service = SearchService(db)
    return await search_service.create_suggestion(suggestion, current_user.id)

@router.post("/filters", response_model=SearchFilterResponse)
async def create_filter(
    filter: SearchFilterCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new search filter."""
    search_service = SearchService(db)
    return await search_service.create_filter(filter, current_user.id)

@router.get("/analytics", response_model=List[SearchAnalyticsResponse])
async def get_search_analytics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100)
):
    """Get user's search analytics."""
    search_service = SearchService(db)
    return await search_service.get_search_analytics(current_user.id, limit) 