from sqlalchemy import func, select, case
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.infrastructure.Database import Base
from app.domain.Reservation import Reservation, ReservationStatus
from sqlalchemy import Column, Integer, String, DateTime

# ORM 모델 정의 (Domain 객체와 분리하여 Persistence Model로 사용)
class ReservationORM(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    exam_start = Column(DateTime(timezone=True), nullable=False)  # 변경됨
    exam_end = Column(DateTime(timezone=True), nullable=False)    # 변경됨
    num_examinees = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default=ReservationStatus.pending)
    created_at = Column(DateTime, default=datetime)
    updated_at = Column(DateTime, default=datetime, onupdate=datetime)

# Reservation Repository 구현
class ReservationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, reservation: Reservation) -> ReservationORM:
        orm_obj = ReservationORM(
            user_id=reservation.user_id,
            exam_start=reservation.exam_start,
            exam_end=reservation.exam_end,
            num_examinees=reservation.num_examinees,
            status=reservation.status.value if isinstance(reservation.status, ReservationStatus) else reservation.status
        )
        self.session.add(orm_obj)
        await self.session.commit()
        await self.session.refresh(orm_obj)
        return orm_obj

    async def get_by_id(self, reservation_id: int) -> ReservationORM:
        stmt = select(ReservationORM).where(ReservationORM.id == reservation_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self):
        stmt = select(ReservationORM)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_user(self, user_id: str):
        stmt = select(ReservationORM).where(ReservationORM.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, reservation: ReservationORM) -> ReservationORM:
        await self.session.commit()
        await self.session.refresh(reservation)
        return reservation

    async def delete(self, reservation: ReservationORM):
        await self.session.delete(reservation)
        await self.session.commit()

    async def get_confirmed_sum(self, exam_start, exam_end, exclude_id: int = None) -> int:
        stmt = select(func.coalesce(func.sum(
            case(
                (ReservationORM.status == ReservationStatus.confirmed.value, ReservationORM.num_examinees),
                else_=0
            )
        ), 0)).where(
            ReservationORM.exam_start == exam_start,
            ReservationORM.exam_end == exam_end
        )
        if exclude_id:
            stmt = stmt.where(ReservationORM.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_exam_schedules(self):
        stmt = select(
            ReservationORM.exam_start,
            ReservationORM.exam_end,
            func.coalesce(func.sum(
                case(
                    (ReservationORM.status == ReservationStatus.confirmed.value, ReservationORM.num_examinees),
                    else_=0
                )
            ), 0).label("confirmed_count")
        ).group_by(ReservationORM.exam_start, ReservationORM.exam_end)
        result = await self.session.execute(stmt)
        schedules = []
        for row in result.all():
            exam_start, exam_end, confirmed_count = row
            available_capacity = max(50000 - confirmed_count, 0)
            schedules.append({
                "exam_start": exam_start,
                "exam_end": exam_end,
                "confirmed_count": confirmed_count,
                "available_capacity": available_capacity
            })
        return schedules
