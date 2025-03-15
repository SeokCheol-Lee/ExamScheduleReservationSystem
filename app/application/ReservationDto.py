from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.domain.Reservation import ReservationStatus

class ReservationCreateDTO(BaseModel):
    exam_schedule_id: int 
    num_examinees: int = Field(default=1, gt=0)

class ReservationUpdateDTO(BaseModel):
    num_examinees: Optional[int] = Field(default=None, gt=0)

class ReservationResponseDTO(BaseModel):
    id: int
    user_id: str
    exam_schedule_id: int 
    exam_start: Optional[datetime] = None  # Optional로 수정
    exam_end: Optional[datetime] = None      # Optional로 수정
    num_examinees: int
    status: ReservationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
