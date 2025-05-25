from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
import math
import logging

from ..models.chw_tracker import (
    CHWFieldVisit,
    CHWActivity,
    CHWLocationTracking,
    CHWPerformanceMetrics,
    VisitStatus,
    ActivityType
)
from ..schemas.chw_tracker import (
    CHWFieldVisitCreate,
    CHWFieldVisitUpdate,
    CHWActivityCreate,
    CHWActivityUpdate,
    CHWLocationTrackingCreate,
    CHWPerformanceMetricsCreate,
    CHWVisitStats,
    CHWActivityStats,
    CHWLocationStats
)

logger = logging.getLogger(__name__)

class CHWTrackerService:
    def __init__(self, db: Session):
        self.db = db

    async def create_field_visit(
        self,
        visit_data: CHWFieldVisitCreate,
        chw_id: int
    ) -> CHWFieldVisit:
        """Create a new field visit."""
        try:
            visit = CHWFieldVisit(
                **visit_data.dict(),
                chw_id=chw_id
            )
            self.db.add(visit)
            self.db.commit()
            self.db.refresh(visit)
            return visit
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating field visit: {str(e)}")
            raise

    async def update_field_visit(
        self,
        visit_id: int,
        visit_data: CHWFieldVisitUpdate
    ) -> CHWFieldVisit:
        """Update a field visit."""
        try:
            visit = self.db.query(CHWFieldVisit).filter(
                CHWFieldVisit.id == visit_id
            ).first()
            
            if not visit:
                raise ValueError("Visit not found")

            for key, value in visit_data.dict(exclude_unset=True).items():
                setattr(visit, key, value)

            self.db.commit()
            self.db.refresh(visit)
            return visit
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating field visit: {str(e)}")
            raise

    async def get_field_visits(
        self,
        chw_id: Optional[int] = None,
        patient_id: Optional[int] = None,
        status: Optional[VisitStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CHWFieldVisit]:
        """Get field visits with optional filters."""
        try:
            query = self.db.query(CHWFieldVisit)

            if chw_id:
                query = query.filter(CHWFieldVisit.chw_id == chw_id)
            if patient_id:
                query = query.filter(CHWFieldVisit.patient_id == patient_id)
            if status:
                query = query.filter(CHWFieldVisit.status == status)
            if start_date:
                query = query.filter(CHWFieldVisit.visit_date >= start_date)
            if end_date:
                query = query.filter(CHWFieldVisit.visit_date <= end_date)

            return query.order_by(desc(CHWFieldVisit.visit_date)).all()
        except Exception as e:
            logger.error(f"Error getting field visits: {str(e)}")
            raise

    async def create_activity(
        self,
        activity_data: CHWActivityCreate
    ) -> CHWActivity:
        """Create a new activity for a field visit."""
        try:
            activity = CHWActivity(**activity_data.dict())
            self.db.add(activity)
            self.db.commit()
            self.db.refresh(activity)
            return activity
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating activity: {str(e)}")
            raise

    async def update_activity(
        self,
        activity_id: int,
        activity_data: CHWActivityUpdate
    ) -> CHWActivity:
        """Update an activity."""
        try:
            activity = self.db.query(CHWActivity).filter(
                CHWActivity.id == activity_id
            ).first()
            
            if not activity:
                raise ValueError("Activity not found")

            for key, value in activity_data.dict(exclude_unset=True).items():
                setattr(activity, key, value)

            self.db.commit()
            self.db.refresh(activity)
            return activity
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating activity: {str(e)}")
            raise

    async def track_location(
        self,
        location_data: CHWLocationTrackingCreate
    ) -> CHWLocationTracking:
        """Track CHW location during a visit."""
        try:
            location = CHWLocationTracking(**location_data.dict())
            self.db.add(location)
            self.db.commit()
            self.db.refresh(location)
            return location
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error tracking location: {str(e)}")
            raise

    async def get_visit_stats(
        self,
        chw_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> CHWVisitStats:
        """Get statistics for CHW visits."""
        try:
            query = self.db.query(CHWFieldVisit).filter(
                CHWFieldVisit.chw_id == chw_id
            )

            if start_date:
                query = query.filter(CHWFieldVisit.visit_date >= start_date)
            if end_date:
                query = query.filter(CHWFieldVisit.visit_date <= end_date)

            visits = query.all()
            
            # Calculate statistics
            total_visits = len(visits)
            visits_by_status = {}
            visits_by_type = {}
            total_duration = 0
            completed_visits = 0
            verified_visits = 0

            for visit in visits:
                # Count by status
                status = visit.status.value
                visits_by_status[status] = visits_by_status.get(status, 0) + 1

                # Count by type
                visit_type = visit.visit_type.value
                visits_by_type[visit_type] = visits_by_type.get(visit_type, 0) + 1

                # Calculate duration
                if visit.start_time and visit.end_time:
                    duration = (visit.end_time - visit.start_time).total_seconds() / 60
                    total_duration += duration
                    completed_visits += 1

                if visit.is_verified:
                    verified_visits += 1

            return CHWVisitStats(
                total_visits=total_visits,
                visits_by_status=visits_by_status,
                visits_by_type=visits_by_type,
                average_visit_duration=total_duration / completed_visits if completed_visits > 0 else 0,
                total_distance=self._calculate_total_distance(visits),
                completion_rate=completed_visits / total_visits if total_visits > 0 else 0,
                verification_rate=verified_visits / total_visits if total_visits > 0 else 0
            )
        except Exception as e:
            logger.error(f"Error getting visit stats: {str(e)}")
            raise

    async def get_activity_stats(
        self,
        chw_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> CHWActivityStats:
        """Get statistics for CHW activities."""
        try:
            query = self.db.query(CHWActivity).join(
                CHWFieldVisit
            ).filter(
                CHWFieldVisit.chw_id == chw_id
            )

            if start_date:
                query = query.filter(CHWFieldVisit.visit_date >= start_date)
            if end_date:
                query = query.filter(CHWFieldVisit.visit_date <= end_date)

            activities = query.all()
            
            # Calculate statistics
            total_activities = len(activities)
            activities_by_type = {}
            total_duration = 0
            successful_activities = 0

            for activity in activities:
                # Count by type
                activity_type = activity.activity_type.value
                activities_by_type[activity_type] = activities_by_type.get(activity_type, 0) + 1

                # Calculate duration
                if activity.start_time and activity.end_time:
                    duration = (activity.end_time - activity.start_time).total_seconds() / 60
                    total_duration += duration

                # Count successful activities
                if activity.outcome and "success" in activity.outcome.lower():
                    successful_activities += 1

            return CHWActivityStats(
                total_activities=total_activities,
                activities_by_type=activities_by_type,
                average_activity_duration=total_duration / total_activities if total_activities > 0 else 0,
                success_rate=successful_activities / total_activities if total_activities > 0 else 0
            )
        except Exception as e:
            logger.error(f"Error getting activity stats: {str(e)}")
            raise

    async def get_location_stats(
        self,
        chw_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> CHWLocationStats:
        """Get statistics for CHW location tracking."""
        try:
            query = self.db.query(CHWLocationTracking).join(
                CHWFieldVisit
            ).filter(
                CHWFieldVisit.chw_id == chw_id
            )

            if start_date:
                query = query.filter(CHWFieldVisit.visit_date >= start_date)
            if end_date:
                query = query.filter(CHWFieldVisit.visit_date <= end_date)

            locations = query.all()
            
            # Calculate statistics
            total_points = len(locations)
            total_speed = 0
            total_distance = 0
            visited_areas = {}

            for i in range(len(locations) - 1):
                current = locations[i]
                next_loc = locations[i + 1]

                # Calculate distance between points
                distance = self._calculate_distance(
                    current.latitude,
                    current.longitude,
                    next_loc.latitude,
                    next_loc.longitude
                )
                total_distance += distance

                # Add speed
                if current.speed:
                    total_speed += current.speed

                # Track visited areas
                area_key = f"{round(current.latitude, 3)},{round(current.longitude, 3)}"
                visited_areas[area_key] = visited_areas.get(area_key, 0) + 1

            # Sort visited areas by frequency
            most_visited = sorted(
                [
                    {"location": key, "visits": value}
                    for key, value in visited_areas.items()
                ],
                key=lambda x: x["visits"],
                reverse=True
            )[:5]

            return CHWLocationStats(
                total_tracking_points=total_points,
                average_speed=total_speed / total_points if total_points > 0 else 0,
                total_distance=total_distance,
                coverage_area=self._calculate_coverage_area(locations),
                most_visited_areas=most_visited
            )
        except Exception as e:
            logger.error(f"Error getting location stats: {str(e)}")
            raise

    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance between two points using Haversine formula."""
        R = 6371  # Earth's radius in kilometers

        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    def _calculate_total_distance(self, visits: List[CHWFieldVisit]) -> float:
        """Calculate total distance traveled during visits."""
        total_distance = 0
        for visit in visits:
            if visit.location_tracking:
                locations = sorted(
                    visit.location_tracking,
                    key=lambda x: x.timestamp
                )
                for i in range(len(locations) - 1):
                    total_distance += self._calculate_distance(
                        locations[i].latitude,
                        locations[i].longitude,
                        locations[i + 1].latitude,
                        locations[i + 1].longitude
                    )
        return total_distance

    def _calculate_coverage_area(self, locations: List[CHWLocationTracking]) -> float:
        """Calculate the area covered by CHW movements."""
        if not locations:
            return 0

        # Create a convex hull of points
        points = [(loc.latitude, loc.longitude) for loc in locations]
        
        # Calculate area using shoelace formula
        area = 0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        
        return abs(area) / 2 