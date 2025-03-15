from datetime import datetime, timedelta, timezone
from typing import List
from app.infrastructure.ReservationRepository import ReservationRepository
from app.application.ReservationDto import (
    ReservationCreateDTO,
    ReservationUpdateDTO,
    ReservationResponseDTO
)
from app.application.ExamScheduleDto import ExamScheduleCreateDTO, ExamScheduleResponseDTO
from app.domain.Reservation import Reservation, ReservationStatus
from app.domain.Exception import ReservationException

class ReservationService:
    def __init__(self, repository: ReservationRepository):
        self.repository = repository

    # 사용자 예약 신청 (시험 일정에 예약)
    async def create_reservation(self, user_id: str, dto: ReservationCreateDTO) -> dict:
        # exam_schedule_id와 num_examinees가 dto에 포함되어 있음
        exam_schedule = await self.repository.get_exam_schedule_by_id(dto.exam_schedule_id)
        if not exam_schedule:
            raise ReservationException("Exam schedule not found")
        
        if exam_schedule.exam_start < datetime.now(timezone.utc) + timedelta(days=3):
            raise ReservationException("Reservation must be made at least 3 days before exam start")
        
        confirmed_sum = await self.repository.get_confirmed_sum(exam_schedule.id)
        if confirmed_sum + dto.num_examinees > exam_schedule.capacity:
            raise ReservationException("Exceeds available capacity for this exam schedule")
        
        # 예약 생성 시 exam_schedule에서 exam_start, exam_end 값을 가져와 할당합니다.
        reservation = Reservation(
            user_id=user_id,
            exam_schedule_id=dto.exam_schedule_id,
            num_examinees=dto.num_examinees,
            exam_start=exam_schedule.exam_start,
            exam_end=exam_schedule.exam_end,
            status=ReservationStatus.pending
        )
        reservation = await self.repository.create(reservation)
        
        # ORM 객체를 Pydantic 모델로 변환 후, exam_start, exam_end 값을 덮어씌웁니다.
        response = ReservationResponseDTO.model_validate(reservation).model_dump()
        response["exam_start"] = exam_schedule.exam_start
        response["exam_end"] = exam_schedule.exam_end
        return response

    # 내 예약 조회
    async def get_my_reservations(self, user_id: str) -> List[dict]:
        reservations = await self.repository.list_by_user(user_id)
        results = []
        for r in reservations:
            exam_schedule = await self.repository.get_exam_schedule_by_id(r.exam_schedule_id)
            dto = ReservationResponseDTO.model_validate(r).model_dump()
            if exam_schedule:
                dto["exam_start"] = exam_schedule.exam_start
                dto["exam_end"] = exam_schedule.exam_end
            results.append(dto)
        return results

    # 예약 수정 (일반 사용자는 자신의 예약만, 시험 일정 변경 불가)
    async def update_reservation(self, reservation_id: int, user_id: str, dto: ReservationUpdateDTO) -> dict:
        reservation = await self.repository.get_by_id(reservation_id)
        if not reservation:
            raise ReservationException("Reservation not found")
        if reservation.user_id != user_id:
            raise ReservationException("Not authorized to update this reservation")
        if reservation.status == ReservationStatus.confirmed:
            raise ReservationException("Confirmed reservations cannot be updated")
        
        new_num_examinees = dto.num_examinees if dto.num_examinees is not None else reservation.num_examinees

        exam_schedule = await self.repository.get_exam_schedule_by_id(reservation.exam_schedule_id)
        confirmed_sum = await self.repository.get_confirmed_sum(exam_schedule.id, exclude_id=reservation_id)
        if confirmed_sum + new_num_examinees > exam_schedule.capacity:
            raise ReservationException("Exceeds available capacity for this exam schedule")
        
        reservation.num_examinees = new_num_examinees
        reservation = await self.repository.update(reservation)
        response = ReservationResponseDTO.model_validate(reservation).model_dump()
        if exam_schedule:
            response["exam_start"] = exam_schedule.exam_start
            response["exam_end"] = exam_schedule.exam_end
        return response

    # 예약 삭제 (일반 사용자는 자신의 pending 상태 예약만 삭제 가능)
    async def delete_reservation(self, reservation_id: int, user_id: str):
        reservation = await self.repository.get_by_id(reservation_id)
        if not reservation:
            raise ReservationException("Reservation not found")
        if reservation.user_id != user_id:
            raise ReservationException("Not authorized to delete this reservation")
        if reservation.status == ReservationStatus.confirmed:
            raise ReservationException("Confirmed reservations cannot be deleted")
        await self.repository.delete(reservation)
