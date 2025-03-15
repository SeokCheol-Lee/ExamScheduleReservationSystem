import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timedelta, timezone
from app.application.ExamScheduleDto import ExamScheduleCreateDTO, ExamScheduleResponseDTO
from app.application.ExamScheduleService import ExamScheduleService
from app.domain.ExamSchedule import ExamSchedule

@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    return repo

@pytest.fixture
def exam_schedule_service(mock_repository):
    return ExamScheduleService(repository=mock_repository)

# 테스트: 시험 일정 생성 성공
@pytest.mark.asyncio
async def test_create_exam_schedule_success(exam_schedule_service, mock_repository):
    exam_start = datetime.now(timezone.utc) + timedelta(days=5)
    exam_end = exam_start + timedelta(hours=2)
    dto = ExamScheduleCreateDTO(exam_start=exam_start, exam_end=exam_end, capacity=3000)
    mock_repository.create_exam_schedule.return_value = ExamScheduleResponseDTO(
        id=1, exam_start=exam_start, exam_end=exam_end, capacity=3000, confirmed_count=0, available_capacity=3000
    )

    result = await exam_schedule_service.create_exam_schedule(dto)

    # ✅ result["id"] 대신 result.id 로 접근
    assert result.id == 1
    mock_repository.create_exam_schedule.assert_called_once()


# 테스트: 시험 일정 생성 실패 - 종료 시간이 시작 시간보다 빠름
@pytest.mark.asyncio
async def test_create_exam_schedule_fail_invalid_time(exam_schedule_service, mock_repository):
    exam_start = datetime.now(timezone.utc) + timedelta(days=5)
    exam_end = exam_start - timedelta(hours=2)
    dto = ExamScheduleCreateDTO(exam_start=exam_start, exam_end=exam_end, capacity=3000)

    with pytest.raises(Exception, match="Exam start must be before exam end"):
        await exam_schedule_service.create_exam_schedule(dto)

# 테스트: 시험 일정 조회 성공
@pytest.mark.asyncio
async def test_get_exam_schedules_success(exam_schedule_service, mock_repository):
    exam_start = datetime.now(timezone.utc) + timedelta(days=5)
    exam_end = exam_start + timedelta(hours=2)
    schedules = [
        ExamScheduleResponseDTO(id=1, exam_start=exam_start, exam_end=exam_end, capacity=3000, confirmed_count=1000, available_capacity=2000),
        ExamScheduleResponseDTO(id=2, exam_start=exam_start + timedelta(days=1), exam_end=exam_end + timedelta(days=1), capacity=4000, confirmed_count=1500, available_capacity=2500),
    ]
    mock_repository.get_exam_schedules.return_value = schedules

    result = await exam_schedule_service.get_exam_schedules()

    # ✅ 수정: result는 dict 리스트이므로 key로 접근
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 2
    mock_repository.get_exam_schedules.assert_called_once()
