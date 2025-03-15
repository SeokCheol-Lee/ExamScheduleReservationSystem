from datetime import datetime, timezone
from typing import List
from app.infrastructure.ReservationRepository import ReservationRepository
from app.application.ExamScheduleDto import ExamScheduleCreateDTO, ExamScheduleResponseDTO
from app.domain.ExamSchedule import ExamSchedule

class ExamScheduleService:
    def __init__(self, repository: ReservationRepository):
        self.repository = repository

    # 시험 일정 생성 (관리자 전용)
    async def create_exam_schedule(self, dto: ExamScheduleCreateDTO) -> ExamScheduleResponseDTO:
        if dto.exam_start >= dto.exam_end:
            raise Exception("Exam start must be before exam end")

        exam_schedule = await self.repository.create_exam_schedule(
            exam_start=dto.exam_start,
            exam_end=dto.exam_end,
            capacity=dto.capacity
        )
        return ExamScheduleResponseDTO(
            id=exam_schedule.id,
            exam_start=exam_schedule.exam_start,
            exam_end=exam_schedule.exam_end,
            capacity=exam_schedule.capacity,
            confirmed_count=0,
            available_capacity=exam_schedule.capacity
        )

    # 시험 일정 조회 (모든 사용자에게 공개)
    async def get_exam_schedules(self) -> List[dict]:
        schedules = await self.repository.get_exam_schedules()

        dto_list = [
            ExamScheduleResponseDTO(
                id=s["exam_schedule_id"],
                exam_start=s["exam_start"],
                exam_end=s["exam_end"],
                capacity=s["capacity"],
                confirmed_count=s["confirmed_count"],
                available_capacity=s["available_capacity"]
            ).model_dump()
            for s in schedules
        ]

        # datetime을 ISO 형식으로 변환
        for d in dto_list:
            for key in ["exam_start", "exam_end"]:
                if isinstance(d.get(key), datetime):
                    dt = d[key]
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    d[key] = dt.isoformat()

        return dto_list
