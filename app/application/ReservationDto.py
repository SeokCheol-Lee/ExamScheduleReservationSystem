from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.domain.Reservation import ReservationStatus

class ReservationCreateDTO(BaseModel):
    exam_start: datetime
    exam_end: datetime
    num_examinees: int = Field(default=1, gt=0)  # 기본값 추가

class ReservationUpdateDTO(BaseModel):
    exam_start: Optional[datetime] = None
    exam_end: Optional[datetime] = None
    num_examinees: Optional[int] = Field(default=None, gt=0)

class ReservationResponseDTO(BaseModel):
    id: int
    user_id: str
    exam_start: datetime
    exam_end: datetime
    num_examinees: int
    status: ReservationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # orm_mode 대신 사용

class ExamScheduleResponseDTO(BaseModel):
    exam_start: datetime
    exam_end: datetime
    confirmed_count: int
    available_capacity: int
