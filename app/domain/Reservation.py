from datetime import datetime
from pydantic import BaseModel, Field
import enum

class ReservationStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"

class Reservation(BaseModel):
    id: int | None = None
    user_id: str | None = None
    exam_start: datetime | None = None
    exam_end: datetime | None = None
    num_examinees: int = Field(0, ge=0)  # 0 이상 값만 허용
    status: ReservationStatus = ReservationStatus.pending
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def is_pending(self) -> bool:
        return self.status == ReservationStatus.pending

    def confirm(self):
        if self.status == ReservationStatus.confirmed:
            raise ValueError("Reservation already confirmed")
        self.status = ReservationStatus.confirmed
        self.updated_at = datetime.now()  # 상태 변경 시 updated_at 갱신

# 사용 예시
reservation = Reservation(user_id="user123", exam_start=datetime(2025, 3, 15, 10, 0))
print(reservation.dict())  # Pydantic의 dict() 활용 가능
