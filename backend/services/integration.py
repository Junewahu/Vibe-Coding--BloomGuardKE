from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
import requests
import json
import uuid
from ..models.integration import (
    Integration, APIRoute, APIRateLimit,
    APILog, APITransformation, IntegrationType,
    IntegrationStatus, IntegrationAuthType
)
from ..schemas.integration import (
    IntegrationCreate, IntegrationUpdate,
    APIRouteCreate, APIRouteUpdate,
    APIRateLimitCreate, APIRateLimitUpdate,
    APILogCreate, APITransformationCreate,
    APITransformationUpdate
)

logger = logging.getLogger(__name__)

class IntegrationService:
    async def create_integration(
        self,
        db: Session,
        integration_data: Dict[str, Any]
    ) -> Integration:
        """Create a new integration."""
        try:
            integration = Integration(**integration_data)
            db.add(integration)
            db.commit()
            db.refresh(integration)
            return integration
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating integration: {str(e)}")
            raise

    async def get_integration(
        self,
        db: Session,
        integration_id: int
    ) -> Optional[Integration]:
        """Get an integration by ID."""
        return db.query(Integration).filter(Integration.id == integration_id).first()

    async def get_integrations(
        self,
        db: Session,
        integration_type: Optional[IntegrationType] = None,
        status: Optional[IntegrationStatus] = None
    ) -> List[Integration]:
        """Get integrations with optional filters."""
        query = db.query(Integration)
        if integration_type:
            query = query.filter(Integration.integration_type == integration_type)
        if status:
            query = query.filter(Integration.status == status)
        return query.all()

    async def update_integration(
        self,
        db: Session,
        integration_id: int,
        integration_data: Dict[str, Any]
    ) -> Optional[Integration]:
        """Update an integration."""
        try:
            integration = await self.get_integration(db, integration_id)
            if integration:
                for key, value in integration_data.items():
                    setattr(integration, key, value)
                db.commit()
                db.refresh(integration)
            return integration
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating integration: {str(e)}")
            raise

    async def create_route(
        self,
        db: Session,
        route_data: Dict[str, Any]
    ) -> APIRoute:
        """Create a new API route."""
        try:
            route = APIRoute(**route_data)
            db.add(route)
            db.commit()
            db.refresh(route)
            return route
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating route: {str(e)}")
            raise

    async def get_route(
        self,
        db: Session,
        route_id: int
    ) -> Optional[APIRoute]:
        """Get an API route by ID."""
        return db.query(APIRoute).filter(APIRoute.id == route_id).first()

    async def get_integration_routes(
        self,
        db: Session,
        integration_id: int,
        is_active: Optional[bool] = None
    ) -> List[APIRoute]:
        """Get routes for an integration."""
        query = db.query(APIRoute).filter(APIRoute.integration_id == integration_id)
        if is_active is not None:
            query = query.filter(APIRoute.is_active == is_active)
        return query.all()

    async def update_route(
        self,
        db: Session,
        route_id: int,
        route_data: Dict[str, Any]
    ) -> Optional[APIRoute]:
        """Update an API route."""
        try:
            route = await self.get_route(db, route_id)
            if route:
                for key, value in route_data.items():
                    setattr(route, key, value)
                db.commit()
                db.refresh(route)
            return route
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating route: {str(e)}")
            raise

    async def check_rate_limit(
        self,
        db: Session,
        route_id: int,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        """Check if a request is within rate limits."""
        route = await self.get_route(db, route_id)
        if not route or not route.rate_limit:
            return True

        window_start = datetime.utcnow() - timedelta(minutes=1)
        query = db.query(APIRateLimit).filter(
            APIRateLimit.route_id == route_id,
            APIRateLimit.window_start >= window_start
        )

        if user_id:
            query = query.filter(APIRateLimit.user_id == user_id)
        if ip_address:
            query = query.filter(APIRateLimit.ip_address == ip_address)

        rate_limit = query.first()
        if not rate_limit:
            rate_limit = APIRateLimit(
                route_id=route_id,
                user_id=user_id,
                ip_address=ip_address,
                window_start=window_start,
                window_end=datetime.utcnow() + timedelta(minutes=1)
            )
            db.add(rate_limit)
            db.commit()
            db.refresh(rate_limit)

        return rate_limit.requests_count < route.rate_limit

    async def increment_rate_limit(
        self,
        db: Session,
        route_id: int,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """Increment the request count for rate limiting."""
        window_start = datetime.utcnow() - timedelta(minutes=1)
        query = db.query(APIRateLimit).filter(
            APIRateLimit.route_id == route_id,
            APIRateLimit.window_start >= window_start
        )

        if user_id:
            query = query.filter(APIRateLimit.user_id == user_id)
        if ip_address:
            query = query.filter(APIRateLimit.ip_address == ip_address)

        rate_limit = query.first()
        if rate_limit:
            rate_limit.requests_count += 1
            db.commit()

    async def create_log(
        self,
        db: Session,
        log_data: Dict[str, Any]
    ) -> APILog:
        """Create a new API log entry."""
        try:
            log = APILog(**log_data)
            db.add(log)
            db.commit()
            db.refresh(log)
            return log
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating log: {str(e)}")
            raise

    async def get_route_logs(
        self,
        db: Session,
        route_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[APILog]:
        """Get logs for a route."""
        query = db.query(APILog).filter(APILog.route_id == route_id)
        if start_date:
            query = query.filter(APILog.created_at >= start_date)
        if end_date:
            query = query.filter(APILog.created_at <= end_date)
        return query.order_by(APILog.created_at.desc()).limit(limit).all()

    async def create_transformation(
        self,
        db: Session,
        transformation_data: Dict[str, Any]
    ) -> APITransformation:
        """Create a new API transformation."""
        try:
            transformation = APITransformation(**transformation_data)
            db.add(transformation)
            db.commit()
            db.refresh(transformation)
            return transformation
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating transformation: {str(e)}")
            raise

    async def get_route_transformations(
        self,
        db: Session,
        route_id: int,
        transformation_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[APITransformation]:
        """Get transformations for a route."""
        query = db.query(APITransformation).filter(APITransformation.route_id == route_id)
        if transformation_type:
            query = query.filter(APITransformation.transformation_type == transformation_type)
        if is_active is not None:
            query = query.filter(APITransformation.is_active == is_active)
        return query.all()

    async def update_transformation(
        self,
        db: Session,
        transformation_id: int,
        transformation_data: Dict[str, Any]
    ) -> Optional[APITransformation]:
        """Update an API transformation."""
        try:
            transformation = db.query(APITransformation).filter(
                APITransformation.id == transformation_id
            ).first()
            if transformation:
                for key, value in transformation_data.items():
                    setattr(transformation, key, value)
                db.commit()
                db.refresh(transformation)
            return transformation
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating transformation: {str(e)}")
            raise

    async def execute_request(
        self,
        db: Session,
        route_id: int,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute an API request with rate limiting and logging."""
        route = await self.get_route(db, route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")

        # Check rate limit
        if not await self.check_rate_limit(db, route_id, user_id, ip_address):
            raise Exception("Rate limit exceeded")

        # Get integration
        integration = await self.get_integration(db, route.integration_id)
        if not integration or integration.status != IntegrationStatus.ACTIVE:
            raise Exception("Integration not available")

        # Prepare request
        url = f"{integration.base_url.rstrip('/')}/{path.lstrip('/')}"
        request_headers = {**(integration.headers or {}), **(headers or {})}
        request_id = str(uuid.uuid4())

        # Create log entry
        log = await self.create_log(db, {
            "route_id": route_id,
            "user_id": user_id,
            "request_id": request_id,
            "method": method,
            "path": path,
            "request_headers": request_headers,
            "request_body": body,
            "ip_address": ip_address
        })

        try:
            # Execute request
            start_time = datetime.utcnow()
            response = requests.request(
                method=method,
                url=url,
                headers=request_headers,
                json=body,
                timeout=route.timeout or 30
            )
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Update log
            log.response_status = response.status_code
            log.response_headers = dict(response.headers)
            log.response_body = response.json() if response.text else None
            log.duration = duration
            db.commit()

            # Increment rate limit
            await self.increment_rate_limit(db, route_id, user_id, ip_address)

            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.json() if response.text else None,
                "duration": duration
            }

        except Exception as e:
            # Update log with error
            log.error_message = str(e)
            db.commit()
            raise

    async def get_integration_stats(
        self,
        db: Session
    ) -> Dict[str, Any]:
        """Get comprehensive integration statistics."""
        try:
            # Get total integrations
            total_integrations = db.query(Integration).count()

            # Get integrations by type
            integrations_by_type = {}
            for type_ in IntegrationType:
                count = db.query(Integration).filter(
                    Integration.integration_type == type_
                ).count()
                integrations_by_type[type_.value] = count

            # Get integrations by status
            integrations_by_status = {}
            for status in IntegrationStatus:
                count = db.query(Integration).filter(
                    Integration.status == status
                ).count()
                integrations_by_status[status.value] = count

            # Get route statistics
            total_routes = db.query(APIRoute).count()
            active_routes = db.query(APIRoute).filter(APIRoute.is_active == True).count()

            # Get request statistics
            total_requests = db.query(APILog).count()
            requests_by_status = {}
            for status in range(100, 600, 100):
                count = db.query(APILog).filter(
                    APILog.response_status >= status,
                    APILog.response_status < status + 100
                ).count()
                requests_by_status[f"{status}xx"] = count

            # Calculate average response time
            avg_response_time = db.query(func.avg(APILog.duration)).scalar() or 0

            # Get recent logs
            recent_logs = db.query(APILog).order_by(
                APILog.created_at.desc()
            ).limit(10).all()

            # Get rate limit violations
            rate_limit_violations = db.query(APIRateLimit).filter(
                APIRateLimit.requests_count > 0
            ).count()

            # Get transformation count
            transformation_count = db.query(APITransformation).count()

            return {
                "total_integrations": total_integrations,
                "integrations_by_type": integrations_by_type,
                "integrations_by_status": integrations_by_status,
                "total_routes": total_routes,
                "active_routes": active_routes,
                "total_requests": total_requests,
                "requests_by_status": requests_by_status,
                "average_response_time": avg_response_time,
                "recent_logs": recent_logs,
                "rate_limit_violations": rate_limit_violations,
                "transformation_count": transformation_count
            }
        except Exception as e:
            logger.error(f"Error getting integration stats: {str(e)}")
            raise

# Create singleton instance
integration_service = IntegrationService() 