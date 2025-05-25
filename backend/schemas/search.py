from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class SearchHistoryBase(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    results_count: int = 0

class SearchHistoryCreate(SearchHistoryBase):
    pass

class SearchHistoryResponse(SearchHistoryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class SearchSuggestionBase(BaseModel):
    suggestion: str
    type: str
    metadata: Optional[Dict[str, Any]] = None

class SearchSuggestionCreate(SearchSuggestionBase):
    pass

class SearchSuggestionUpdate(BaseModel):
    suggestion: Optional[str] = None
    type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SearchSuggestionResponse(SearchSuggestionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SearchIndexBase(BaseModel):
    entity_type: str
    entity_id: int
    content: str
    metadata: Optional[Dict[str, Any]] = None

class SearchIndexCreate(SearchIndexBase):
    pass

class SearchIndexUpdate(BaseModel):
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SearchIndexResponse(SearchIndexBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SearchFilterBase(BaseModel):
    name: str
    description: Optional[str] = None
    filter_type: str
    filter_config: Dict[str, Any]
    is_active: bool = True

class SearchFilterCreate(SearchFilterBase):
    pass

class SearchFilterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    filter_type: Optional[str] = None
    filter_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class SearchFilterResponse(SearchFilterBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SearchAnalyticsBase(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    results_count: int = 0
    response_time: Optional[int] = None

class SearchAnalyticsCreate(SearchAnalyticsBase):
    pass

class SearchAnalyticsResponse(SearchAnalyticsBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    page: int = 1
    page_size: int = 20
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int
    suggestions: Optional[List[str]] = None
    filters: Optional[List[Dict[str, Any]]] = None

class SearchStats(BaseModel):
    total_searches: int
    average_response_time: float
    popular_queries: List[Dict[str, Any]]
    search_by_type: Dict[str, int]
    search_by_date: List[Dict[str, Any]]
    filter_usage: Dict[str, int] 