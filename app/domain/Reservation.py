from datetime import datetime
from pydantic import BaseModel, Field
import enum

class ReservationStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"

class Reservation(BaseModel):
    id: int | None = None
    user_id: str | None = None
    exam_schedule_id: int
    exam_start: datetime | None = None
    exam_end: datetime | None = None
    num_examinees: int = Field(0, ge=0)
    status: ReservationStatus = ReservationStatus.pending
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def is_pending(self) -> bool:
        return self.status == ReservationStatus.pending

    def confirm(self):
        if self.status == ReservationStatus.confirmed:
            raise ValueError("Reservation already confirmed")
        self.status = ReservationStatus.confirmed
        self.updated_at = datetime.now()
