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

class AdminReservationService:
    def __init__(self, repository: ReservationRepository):
        self.repository = repository

    # 전체 예약 조회 (관리자 전용)
    async def get_all_reservations(self) -> List[dict]:
        reservations = await self.repository.list_all()
        results = []
        for r in reservations:
            exam_schedule = await self.repository.get_exam_schedule_by_id(r.exam_schedule_id)
            dto = ReservationResponseDTO.model_validate(r).model_dump()
            if exam_schedule:
                dto["exam_start"] = exam_schedule.exam_start
                dto["exam_end"] = exam_schedule.exam_end
            results.append(dto)
        return results

    # 예약 확정 (관리자 전용)
    async def confirm_reservation(self, reservation_id: int) -> dict:
        reservation = await self.repository.get_by_id(reservation_id)
        if not reservation:
            raise ReservationException("Reservation not found")
        if reservation.status == ReservationStatus.confirmed:
            raise ReservationException("Reservation already confirmed")
        
        exam_schedule = await self.repository.get_exam_schedule_by_id(reservation.exam_schedule_id)
        confirmed_sum = await self.repository.get_confirmed_sum(exam_schedule.id)
        if confirmed_sum + reservation.num_examinees > exam_schedule.capacity:
            raise ReservationException("Confirming this reservation exceeds capacity for the exam schedule")
        
        reservation.status = ReservationStatus.confirmed
        reservation = await self.repository.update(reservation)
        response = ReservationResponseDTO.model_validate(reservation).model_dump()
        if exam_schedule:
            response["exam_start"] = exam_schedule.exam_start
            response["exam_end"] = exam_schedule.exam_end
        return response

    # 예약 수정 (관리자는 예약 인원 변경 등 일부 수정 가능)
    async def update_reservation(self, reservation_id: int, dto: ReservationUpdateDTO) -> dict:
        reservation = await self.repository.get_by_id(reservation_id)
        if not reservation:
            raise ReservationException("Reservation not found")
        
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
    
    # 예약 삭제 (관리자 전용)
    async def delete_reservation(self, reservation_id: int):
        reservation = await self.repository.get_by_id(reservation_id)
        if not reservation:
            raise ReservationException("Reservation not found")
        await self.repository.delete(reservation)
