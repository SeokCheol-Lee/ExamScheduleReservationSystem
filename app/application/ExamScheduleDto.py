from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ExamScheduleResponseDTO(BaseModel):
    id: int
    exam_start: datetime
    exam_end: datetime
    capacity: int
    confirmed_count: int
    available_capacity: int

class ExamScheduleCreateDTO(BaseModel):
    exam_start: datetime
    exam_end: datetime
    capacity: int
