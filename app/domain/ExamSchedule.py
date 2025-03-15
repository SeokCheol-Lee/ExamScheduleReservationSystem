from datetime import datetime
from pydantic import BaseModel, Field

class ExamSchedule(BaseModel):
    id: int | None = None
    exam_start: datetime
    exam_end: datetime
    capacity: int = Field(..., ge=0)  # 0 이상의 값만 허용
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def is_valid(self) -> bool:
        # 시험 시작일이 시험 종료일보다 이전인지 확인
        return self.exam_start < self.exam_end

    def update_timestamp(self):
        # 업데이트 시각 갱신
        self.updated_at = datetime.now()
