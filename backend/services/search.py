from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
import logging
from ..models.search import SearchHistory, SearchSuggestion, SearchIndex, SearchFilter, SearchAnalytics
from ..schemas.search import (
    SearchRequest, SearchResponse, SearchStats,
    SearchHistoryCreate, SearchSuggestionCreate, SearchFilterCreate,
    SearchAnalyticsCreate
)

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, db: Session):
        self.db = db

    async def search(self, request: SearchRequest, user_id: int) -> SearchResponse:
        """Perform a search across all indexed content."""
        start_time = time.time()

        try:
            # Build search query
            query = self.db.query(SearchIndex)
            
            # Apply text search
            if request.query:
                query = query.filter(SearchIndex.content.ilike(f"%{request.query}%"))

            # Apply filters
            if request.filters:
                for key, value in request.filters.items():
                    if isinstance(value, dict):
                        # Handle range filters
                        if 'min' in value:
                            query = query.filter(SearchIndex.metadata[key].astext >= str(value['min']))
                        if 'max' in value:
                            query = query.filter(SearchIndex.metadata[key].astext <= str(value['max']))
                    else:
                        # Handle exact match filters
                        query = query.filter(SearchIndex.metadata[key].astext == str(value))

            # Apply sorting
            if request.sort_by:
                sort_column = getattr(SearchIndex, request.sort_by, None)
                if sort_column:
                    if request.sort_order == "desc":
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(sort_column)

            # Get total count
            total = query.count()

            # Apply pagination
            query = query.offset((request.page - 1) * request.page_size).limit(request.page_size)

            # Execute query
            results = query.all()

            # Calculate response time
            response_time = int((time.time() - start_time) * 1000)

            # Log search analytics
            self._log_search_analytics(request, user_id, total, response_time)

            # Get suggestions
            suggestions = await self.get_suggestions(request.query, user_id)

            # Get available filters
            filters = await self.get_available_filters(user_id)

            return SearchResponse(
                results=[self._format_search_result(result) for result in results],
                total=total,
                page=request.page,
                page_size=request.page_size,
                total_pages=(total + request.page_size - 1) // request.page_size,
                suggestions=suggestions,
                filters=filters
            )

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            raise

    async def get_suggestions(self, query: str, user_id: int) -> List[str]:
        """Get search suggestions based on the query."""
        try:
            suggestions = self.db.query(SearchSuggestion.suggestion)\
                .filter(SearchSuggestion.suggestion.ilike(f"%{query}%"))\
                .filter(SearchSuggestion.user_id == user_id)\
                .order_by(desc(SearchSuggestion.created_at))\
                .limit(5)\
                .all()
            
            return [s[0] for s in suggestions]
        except Exception as e:
            logger.error(f"Error getting suggestions: {str(e)}")
            return []

    async def get_available_filters(self, user_id: int) -> List[Dict[str, Any]]:
        """Get available search filters for the user."""
        try:
            filters = self.db.query(SearchFilter)\
                .filter(SearchFilter.user_id == user_id)\
                .filter(SearchFilter.is_active == True)\
                .all()
            
            return [self._format_filter(filter) for filter in filters]
        except Exception as e:
            logger.error(f"Error getting filters: {str(e)}")
            return []

    async def create_search_history(self, history: SearchHistoryCreate, user_id: int) -> SearchHistory:
        """Create a new search history entry."""
        try:
            db_history = SearchHistory(
                **history.dict(),
                user_id=user_id
            )
            self.db.add(db_history)
            self.db.commit()
            self.db.refresh(db_history)
            return db_history
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating search history: {str(e)}")
            raise

    async def create_suggestion(self, suggestion: SearchSuggestionCreate, user_id: int) -> SearchSuggestion:
        """Create a new search suggestion."""
        try:
            db_suggestion = SearchSuggestion(
                **suggestion.dict(),
                user_id=user_id
            )
            self.db.add(db_suggestion)
            self.db.commit()
            self.db.refresh(db_suggestion)
            return db_suggestion
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating suggestion: {str(e)}")
            raise

    async def create_filter(self, filter: SearchFilterCreate, user_id: int) -> SearchFilter:
        """Create a new search filter."""
        try:
            db_filter = SearchFilter(
                **filter.dict(),
                user_id=user_id
            )
            self.db.add(db_filter)
            self.db.commit()
            self.db.refresh(db_filter)
            return db_filter
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating filter: {str(e)}")
            raise

    async def get_search_stats(self, user_id: int, days: int = 30) -> SearchStats:
        """Get search statistics for the user."""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            # Get total searches
            total_searches = self.db.query(func.count(SearchAnalytics.id))\
                .filter(SearchAnalytics.user_id == user_id)\
                .filter(SearchAnalytics.created_at >= start_date)\
                .scalar()

            # Get average response time
            avg_response_time = self.db.query(func.avg(SearchAnalytics.response_time))\
                .filter(SearchAnalytics.user_id == user_id)\
                .filter(SearchAnalytics.created_at >= start_date)\
                .scalar() or 0

            # Get popular queries
            popular_queries = self.db.query(
                SearchAnalytics.query,
                func.count(SearchAnalytics.id).label('count')
            )\
                .filter(SearchAnalytics.user_id == user_id)\
                .filter(SearchAnalytics.created_at >= start_date)\
                .group_by(SearchAnalytics.query)\
                .order_by(desc('count'))\
                .limit(10)\
                .all()

            # Get search by type
            search_by_type = self.db.query(
                SearchIndex.entity_type,
                func.count(SearchIndex.id).label('count')
            )\
                .filter(SearchIndex.created_at >= start_date)\
                .group_by(SearchIndex.entity_type)\
                .all()

            # Get search by date
            search_by_date = self.db.query(
                func.date(SearchAnalytics.created_at).label('date'),
                func.count(SearchAnalytics.id).label('count')
            )\
                .filter(SearchAnalytics.user_id == user_id)\
                .filter(SearchAnalytics.created_at >= start_date)\
                .group_by('date')\
                .order_by('date')\
                .all()

            # Get filter usage
            filter_usage = {}
            for filter in self.db.query(SearchFilter).filter(SearchFilter.user_id == user_id).all():
                usage_count = self.db.query(func.count(SearchAnalytics.id))\
                    .filter(SearchAnalytics.user_id == user_id)\
                    .filter(SearchAnalytics.filters.contains({filter.name: True}))\
                    .filter(SearchAnalytics.created_at >= start_date)\
                    .scalar()
                filter_usage[filter.name] = usage_count

            return SearchStats(
                total_searches=total_searches,
                average_response_time=float(avg_response_time),
                popular_queries=[{"query": q[0], "count": q[1]} for q in popular_queries],
                search_by_type={t[0]: t[1] for t in search_by_type},
                search_by_date=[{"date": d[0].isoformat(), "count": d[1]} for d in search_by_date],
                filter_usage=filter_usage
            )

        except Exception as e:
            logger.error(f"Error getting search stats: {str(e)}")
            raise

    def _log_search_analytics(self, request: SearchRequest, user_id: int, results_count: int, response_time: int):
        """Log search analytics."""
        try:
            analytics = SearchAnalytics(
                query=request.query,
                filters=request.filters,
                results_count=results_count,
                response_time=response_time,
                user_id=user_id
            )
            self.db.add(analytics)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error logging search analytics: {str(e)}")
            self.db.rollback()

    def _format_search_result(self, result: SearchIndex) -> Dict[str, Any]:
        """Format a search result for the response."""
        return {
            "id": result.id,
            "entity_type": result.entity_type,
            "entity_id": result.entity_id,
            "content": result.content,
            "metadata": result.metadata,
            "created_at": result.created_at.isoformat(),
            "updated_at": result.updated_at.isoformat()
        }

    def _format_filter(self, filter: SearchFilter) -> Dict[str, Any]:
        """Format a filter for the response."""
        return {
            "id": filter.id,
            "name": filter.name,
            "description": filter.description,
            "type": filter.filter_type,
            "config": filter.filter_config,
            "is_active": filter.is_active
        } 