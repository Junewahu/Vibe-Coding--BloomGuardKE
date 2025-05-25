from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
import logging

from ..models.incentives import (
    Reward,
    Achievement,
    AdherenceTracking,
    AdherenceCheck,
    IncentiveProgram,
    ProgramEnrollment,
    RewardType,
    AchievementType,
    AdherenceStatus
)
from ..schemas.incentives import (
    RewardCreate,
    RewardUpdate,
    AchievementCreate,
    AchievementUpdate,
    AdherenceTrackingCreate,
    AdherenceTrackingUpdate,
    AdherenceCheckCreate,
    AdherenceCheckUpdate,
    IncentiveProgramCreate,
    IncentiveProgramUpdate,
    ProgramEnrollmentCreate,
    ProgramEnrollmentUpdate,
    RewardStats,
    AchievementStats,
    AdherenceStats,
    ProgramStats
)

logger = logging.getLogger(__name__)

class IncentivesService:
    def __init__(self, db: Session):
        self.db = db

    # Reward Management
    async def create_reward(self, reward_data: RewardCreate) -> Reward:
        """Create a new reward."""
        try:
            reward = Reward(**reward_data.dict())
            self.db.add(reward)
            self.db.commit()
            self.db.refresh(reward)
            return reward
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating reward: {str(e)}")
            raise

    async def update_reward(self, reward_id: int, reward_data: RewardUpdate) -> Reward:
        """Update a reward."""
        try:
            reward = self.db.query(Reward).filter(Reward.id == reward_id).first()
            if not reward:
                raise ValueError("Reward not found")

            for key, value in reward_data.dict(exclude_unset=True).items():
                setattr(reward, key, value)

            self.db.commit()
            self.db.refresh(reward)
            return reward
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating reward: {str(e)}")
            raise

    async def get_rewards(
        self,
        chw_id: Optional[int] = None,
        reward_type: Optional[RewardType] = None,
        status: Optional[str] = None
    ) -> List[Reward]:
        """Get rewards with optional filters."""
        try:
            query = self.db.query(Reward)

            if chw_id:
                query = query.filter(Reward.chw_id == chw_id)
            if reward_type:
                query = query.filter(Reward.reward_type == reward_type)
            if status:
                query = query.filter(Reward.status == status)

            return query.order_by(desc(Reward.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting rewards: {str(e)}")
            raise

    # Achievement Management
    async def create_achievement(self, achievement_data: AchievementCreate) -> Achievement:
        """Create a new achievement."""
        try:
            achievement = Achievement(**achievement_data.dict())
            self.db.add(achievement)
            self.db.commit()
            self.db.refresh(achievement)
            return achievement
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating achievement: {str(e)}")
            raise

    async def update_achievement(
        self,
        achievement_id: int,
        achievement_data: AchievementUpdate
    ) -> Achievement:
        """Update an achievement."""
        try:
            achievement = self.db.query(Achievement).filter(
                Achievement.id == achievement_id
            ).first()
            if not achievement:
                raise ValueError("Achievement not found")

            for key, value in achievement_data.dict(exclude_unset=True).items():
                setattr(achievement, key, value)

            self.db.commit()
            self.db.refresh(achievement)
            return achievement
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating achievement: {str(e)}")
            raise

    async def get_achievements(
        self,
        chw_id: Optional[int] = None,
        achievement_type: Optional[AchievementType] = None,
        is_completed: Optional[bool] = None
    ) -> List[Achievement]:
        """Get achievements with optional filters."""
        try:
            query = self.db.query(Achievement)

            if chw_id:
                query = query.filter(Achievement.chw_id == chw_id)
            if achievement_type:
                query = query.filter(Achievement.achievement_type == achievement_type)
            if is_completed is not None:
                query = query.filter(Achievement.is_completed == is_completed)

            return query.order_by(desc(Achievement.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting achievements: {str(e)}")
            raise

    # Adherence Tracking
    async def create_adherence_tracking(
        self,
        tracking_data: AdherenceTrackingCreate
    ) -> AdherenceTracking:
        """Create a new adherence tracking record."""
        try:
            tracking = AdherenceTracking(**tracking_data.dict())
            self.db.add(tracking)
            self.db.commit()
            self.db.refresh(tracking)
            return tracking
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating adherence tracking: {str(e)}")
            raise

    async def update_adherence_tracking(
        self,
        tracking_id: int,
        tracking_data: AdherenceTrackingUpdate
    ) -> AdherenceTracking:
        """Update an adherence tracking record."""
        try:
            tracking = self.db.query(AdherenceTracking).filter(
                AdherenceTracking.id == tracking_id
            ).first()
            if not tracking:
                raise ValueError("Adherence tracking not found")

            for key, value in tracking_data.dict(exclude_unset=True).items():
                setattr(tracking, key, value)

            self.db.commit()
            self.db.refresh(tracking)
            return tracking
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating adherence tracking: {str(e)}")
            raise

    async def create_adherence_check(
        self,
        check_data: AdherenceCheckCreate
    ) -> AdherenceCheck:
        """Create a new adherence check."""
        try:
            check = AdherenceCheck(**check_data.dict())
            self.db.add(check)
            self.db.commit()
            self.db.refresh(check)
            return check
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating adherence check: {str(e)}")
            raise

    async def get_adherence_tracking(
        self,
        patient_id: Optional[int] = None,
        chw_id: Optional[int] = None,
        status: Optional[AdherenceStatus] = None
    ) -> List[AdherenceTracking]:
        """Get adherence tracking records with optional filters."""
        try:
            query = self.db.query(AdherenceTracking)

            if patient_id:
                query = query.filter(AdherenceTracking.patient_id == patient_id)
            if chw_id:
                query = query.filter(AdherenceTracking.chw_id == chw_id)
            if status:
                query = query.filter(AdherenceTracking.status == status)

            return query.order_by(desc(AdherenceTracking.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting adherence tracking: {str(e)}")
            raise

    # Incentive Program Management
    async def create_incentive_program(
        self,
        program_data: IncentiveProgramCreate
    ) -> IncentiveProgram:
        """Create a new incentive program."""
        try:
            program = IncentiveProgram(**program_data.dict())
            self.db.add(program)
            self.db.commit()
            self.db.refresh(program)
            return program
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating incentive program: {str(e)}")
            raise

    async def update_incentive_program(
        self,
        program_id: int,
        program_data: IncentiveProgramUpdate
    ) -> IncentiveProgram:
        """Update an incentive program."""
        try:
            program = self.db.query(IncentiveProgram).filter(
                IncentiveProgram.id == program_id
            ).first()
            if not program:
                raise ValueError("Incentive program not found")

            for key, value in program_data.dict(exclude_unset=True).items():
                setattr(program, key, value)

            self.db.commit()
            self.db.refresh(program)
            return program
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating incentive program: {str(e)}")
            raise

    async def enroll_in_program(
        self,
        enrollment_data: ProgramEnrollmentCreate
    ) -> ProgramEnrollment:
        """Enroll a CHW in an incentive program."""
        try:
            enrollment = ProgramEnrollment(**enrollment_data.dict())
            self.db.add(enrollment)
            self.db.commit()
            self.db.refresh(enrollment)
            return enrollment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error enrolling in program: {str(e)}")
            raise

    async def update_enrollment(
        self,
        enrollment_id: int,
        enrollment_data: ProgramEnrollmentUpdate
    ) -> ProgramEnrollment:
        """Update a program enrollment."""
        try:
            enrollment = self.db.query(ProgramEnrollment).filter(
                ProgramEnrollment.id == enrollment_id
            ).first()
            if not enrollment:
                raise ValueError("Program enrollment not found")

            for key, value in enrollment_data.dict(exclude_unset=True).items():
                setattr(enrollment, key, value)

            self.db.commit()
            self.db.refresh(enrollment)
            return enrollment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating enrollment: {str(e)}")
            raise

    # Statistics
    async def get_reward_stats(self, chw_id: int) -> RewardStats:
        """Get reward statistics for a CHW."""
        try:
            rewards = self.db.query(Reward).filter(Reward.chw_id == chw_id).all()
            
            total_rewards = len(rewards)
            rewards_by_type = {}
            total_value = 0
            distributed = 0

            for reward in rewards:
                # Count by type
                reward_type = reward.reward_type.value
                rewards_by_type[reward_type] = rewards_by_type.get(reward_type, 0) + 1

                # Calculate total value
                if reward.amount:
                    total_value += reward.amount

                # Count distributed rewards
                if reward.status == "distributed":
                    distributed += 1

            return RewardStats(
                total_rewards=total_rewards,
                rewards_by_type=rewards_by_type,
                total_value=total_value,
                distribution_rate=distributed / total_rewards if total_rewards > 0 else 0
            )
        except Exception as e:
            logger.error(f"Error getting reward stats: {str(e)}")
            raise

    async def get_achievement_stats(self, chw_id: int) -> AchievementStats:
        """Get achievement statistics for a CHW."""
        try:
            achievements = self.db.query(Achievement).filter(
                Achievement.chw_id == chw_id
            ).all()
            
            total_achievements = len(achievements)
            completed_achievements = 0
            achievements_by_type = {}
            total_completion_time = 0

            for achievement in achievements:
                # Count by type
                achievement_type = achievement.achievement_type.value
                achievements_by_type[achievement_type] = achievements_by_type.get(
                    achievement_type, 0
                ) + 1

                # Count completed achievements
                if achievement.is_completed and achievement.completed_at:
                    completed_achievements += 1
                    completion_time = (
                        achievement.completed_at - achievement.created_at
                    ).total_seconds() / 3600  # Convert to hours
                    total_completion_time += completion_time

            return AchievementStats(
                total_achievements=total_achievements,
                completed_achievements=completed_achievements,
                achievements_by_type=achievements_by_type,
                average_completion_time=total_completion_time / completed_achievements
                if completed_achievements > 0 else 0
            )
        except Exception as e:
            logger.error(f"Error getting achievement stats: {str(e)}")
            raise

    async def get_adherence_stats(
        self,
        chw_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> AdherenceStats:
        """Get adherence statistics for a CHW's patients."""
        try:
            query = self.db.query(AdherenceTracking).filter(
                AdherenceTracking.chw_id == chw_id
            )

            if start_date:
                query = query.filter(AdherenceTracking.created_at >= start_date)
            if end_date:
                query = query.filter(AdherenceTracking.created_at <= end_date)

            tracking_records = query.all()
            
            total_patients = len(set(record.patient_id for record in tracking_records))
            status_distribution = {}
            total_adherence_rate = 0
            compliant_count = 0

            for record in tracking_records:
                # Count by status
                status = record.status.value
                status_distribution[status] = status_distribution.get(status, 0) + 1

                # Calculate adherence rate
                if record.adherence_rate:
                    total_adherence_rate += record.adherence_rate

                if record.status == AdherenceStatus.COMPLIANT:
                    compliant_count += 1

            return AdherenceStats(
                total_patients=total_patients,
                compliance_rate=compliant_count / total_patients if total_patients > 0 else 0,
                status_distribution=status_distribution,
                average_adherence_rate=total_adherence_rate / len(tracking_records)
                if tracking_records else 0
            )
        except Exception as e:
            logger.error(f"Error getting adherence stats: {str(e)}")
            raise

    async def get_program_stats(
        self,
        chw_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ProgramStats:
        """Get program statistics for a CHW."""
        try:
            query = self.db.query(ProgramEnrollment).filter(
                ProgramEnrollment.chw_id == chw_id
            )

            if start_date:
                query = query.filter(ProgramEnrollment.enrollment_date >= start_date)
            if end_date:
                query = query.filter(ProgramEnrollment.enrollment_date <= end_date)

            enrollments = query.all()
            
            active_programs = len([
                e for e in enrollments
                if e.status == "active" and e.program.is_active
            ])
            completed_programs = len([
                e for e in enrollments
                if e.status == "completed"
            ])
            total_progress = sum(e.progress for e in enrollments)

            return ProgramStats(
                active_programs=active_programs,
                total_enrollments=len(enrollments),
                completion_rate=completed_programs / len(enrollments)
                if enrollments else 0,
                average_progress=total_progress / len(enrollments)
                if enrollments else 0
            )
        except Exception as e:
            logger.error(f"Error getting program stats: {str(e)}")
            raise 