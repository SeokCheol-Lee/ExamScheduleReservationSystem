from datetime import datetime, timedelta, timezone
from typing import List
from app.infrastructure.ReservationRepository import ReservationRepository
from app.application.ReservationDto import (
    ReservationCreateDTO,
    ReservationUpdateDTO,
    ReservationResponseDTO,
    ExamScheduleResponseDTO
)
from app.domain.Reservation import Reservation, ReservationStatus

class ReservationService:
    CAPACITY_LIMIT = 50000

    def __init__(self, repository: ReservationRepository):
        self.repository = repository

    async def create_reservation(self, user_id: str, dto: ReservationCreateDTO) -> dict:
        # 비즈니스 규칙: 시험 시작 3일 전이어야 함
        if dto.exam_start < datetime.now(timezone.utc) + timedelta(days=3):
            raise Exception("Reservation must be made at least 3 days before exam start")
        
        confirmed_sum = await self.repository.get_confirmed_sum(dto.exam_start, dto.exam_end)
        if confirmed_sum + dto.num_examinees > self.CAPACITY_LIMIT:
            raise Exception("Exceeds available capacity for this exam schedule")

        reservation = Reservation(
            user_id=user_id,
            exam_start=dto.exam_start,
            exam_end=dto.exam_end,
            num_examinees=dto.num_examinees,
            status=ReservationStatus.pending
        )
        reservation = await self.repository.create(reservation)
        return ReservationResponseDTO.from_orm(reservation).model_dump()

    async def get_reservations(self, user_id: str, role: str) -> List[dict]:
        if role == "admin":
            reservations = await self.repository.list_all()
        else:
            reservations = await self.repository.list_by_user(user_id)
        # 각 ReservationResponseDTO를 dict로 변환
        return [ReservationResponseDTO.from_orm(r).model_dump() for r in reservations]

    async def update_reservation(self, reservation_id: int, user_id: str, role: str, dto: ReservationUpdateDTO) -> dict:
        reservation = await self.repository.get_by_id(reservation_id)
        if not reservation:
            raise Exception("Reservation not found")
        
        if role != "admin":
            if reservation.user_id != user_id:
                raise Exception("Not authorized to update this reservation")
            if reservation.status == ReservationStatus.confirmed:
                raise Exception("Confirmed reservations cannot be updated")
        
        new_exam_start = dto.exam_start or reservation.exam_start
        new_exam_end = dto.exam_end or reservation.exam_end
        new_num_examinees = dto.num_examinees or reservation.num_examinees

        # 만약 new_exam_start가 naive이면 UTC로 설정
        if new_exam_start.tzinfo is None:
            new_exam_start = new_exam_start.replace(tzinfo=timezone.utc)
        if new_exam_end.tzinfo is None:
            new_exam_end = new_exam_end.replace(tzinfo=timezone.utc)

        if new_exam_start < datetime.now(timezone.utc) + timedelta(days=3):
            raise Exception("Reservation must be made at least 3 days before exam start")
        
        if reservation.status == ReservationStatus.pending:
            confirmed_sum = await self.repository.get_confirmed_sum(new_exam_start, new_exam_end, exclude_id=reservation_id)
            if confirmed_sum + new_num_examinees > self.CAPACITY_LIMIT:
                raise Exception("Exceeds available capacity for this exam schedule")

        reservation.exam_start = new_exam_start
        reservation.exam_end = new_exam_end
        reservation.num_examinees = new_num_examinees
        reservation = await self.repository.update(reservation)
        return ReservationResponseDTO.from_orm(reservation).model_dump()

    async def delete_reservation(self, reservation_id: int, user_id: str, role: str):
        reservation = await self.repository.get_by_id(reservation_id)
        if not reservation:
            raise Exception("Reservation not found")
        if role != "admin":
            if reservation.user_id != user_id:
                raise Exception("Not authorized to delete this reservation")
            if reservation.status == ReservationStatus.confirmed:
                raise Exception("Confirmed reservations cannot be deleted")
        await self.repository.delete(reservation)

    async def confirm_reservation(self, reservation_id: int) -> dict:
        reservation = await self.repository.get_by_id(reservation_id)
        if not reservation:
            raise Exception("Reservation not found")
        if reservation.status == ReservationStatus.confirmed:
            raise Exception("Reservation already confirmed")
        confirmed_sum = await self.repository.get_confirmed_sum(reservation.exam_start, reservation.exam_end)
        if confirmed_sum + reservation.num_examinees > self.CAPACITY_LIMIT:
            raise Exception("Confirming this reservation exceeds capacity for the exam schedule")
        reservation.status = ReservationStatus.confirmed
        reservation = await self.repository.update(reservation)
        return ReservationResponseDTO.from_orm(reservation).model_dump()

    async def get_exam_schedules(self) -> List[dict]:
        schedules = await self.repository.get_exam_schedules()
        dto_list = [ExamScheduleResponseDTO(**s).model_dump() for s in schedules]
        # exam_start, exam_end가 datetime인 경우 UTC로 설정 후 isoformat() 적용
        for d in dto_list:
            for key in ["exam_start", "exam_end"]:
                if isinstance(d.get(key), datetime):
                    dt = d[key]
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    d[key] = dt.isoformat()
        return dto_list

