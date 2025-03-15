import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timedelta, timezone
from app.application.ReservationDto import ReservationCreateDTO, ReservationUpdateDTO, ReservationResponseDTO
from app.domain.Reservation import Reservation, ReservationStatus
from app.application.ReservationService import ReservationService
from app.application.ExamScheduleDto import ExamScheduleResponseDTO

@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    return repo

@pytest.fixture
def reservation_service(mock_repository):
    return ReservationService(repository=mock_repository)

# 테스트: 예약 생성 성공
@pytest.mark.asyncio
async def test_create_reservation_success(reservation_service, mock_repository):
    exam_start = datetime.now(timezone.utc) + timedelta(days=5)
    exam_end = exam_start + timedelta(hours=2)
    exam_schedule = ExamScheduleResponseDTO(id=1, exam_start=exam_start, exam_end=exam_end, capacity=5000, confirmed_count=1000, available_capacity=4000)
    mock_repository.get_exam_schedule_by_id.return_value = exam_schedule
    mock_repository.get_confirmed_sum.return_value = 1000
    mock_repository.create.return_value = Reservation(id=1, user_id="user1", exam_schedule_id=1, exam_start=exam_start, exam_end=exam_end, num_examinees=500, status=ReservationStatus.pending)

    dto = ReservationCreateDTO(exam_schedule_id=1, num_examinees=500, exam_start=exam_start, exam_end=exam_end)
    result = await reservation_service.create_reservation("user1", dto)

    assert result["num_examinees"] == 500
    assert result["status"] == ReservationStatus.pending.value
    mock_repository.create.assert_called_once()

# 테스트: 예약 생성 실패 - 용량 초과
@pytest.mark.asyncio
async def test_create_reservation_fail_capacity_exceeded(reservation_service, mock_repository):
    exam_start = datetime.now(timezone.utc) + timedelta(days=5)
    exam_end = exam_start + timedelta(hours=2)
    exam_schedule = ExamScheduleResponseDTO(id=1, exam_start=exam_start, exam_end=exam_end, capacity=2000, confirmed_count=1800, available_capacity=200)
    mock_repository.get_exam_schedule_by_id.return_value = exam_schedule
    mock_repository.get_confirmed_sum.return_value = 1800

    dto = ReservationCreateDTO(exam_schedule_id=1, num_examinees=500, exam_start=exam_start, exam_end=exam_end)
    with pytest.raises(Exception, match="Exceeds available capacity for this exam schedule"):
        await reservation_service.create_reservation("user1", dto)

# 테스트: 예약 수정 성공
@pytest.mark.asyncio
async def test_update_reservation_success(reservation_service, mock_repository):
    exam_start = datetime.now(timezone.utc) + timedelta(days=5)
    exam_end = exam_start + timedelta(hours=2)
    reservation = ReservationResponseDTO(
        id=1,
        user_id="user1",
        exam_schedule_id=1,  # ✅ 추가됨
        exam_start=exam_start,
        exam_end=exam_end,
        num_examinees=500,
        status=ReservationStatus.pending,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_repository.get_by_id.return_value = reservation
    mock_repository.get_exam_schedule_by_id.return_value = ExamScheduleResponseDTO(id=1, exam_start=exam_start, exam_end=exam_end, capacity=3000, confirmed_count=1000, available_capacity=2000)
    mock_repository.get_confirmed_sum.return_value = 1000
    mock_repository.update.return_value = reservation

    dto = ReservationUpdateDTO(num_examinees=600)
    result = await reservation_service.update_reservation(1, "user1", dto)
    assert result["num_examinees"] == 600
    mock_repository.update.assert_called_once()

# 테스트: 예약 삭제 성공
@pytest.mark.asyncio
async def test_delete_reservation_success(reservation_service, mock_repository):
    exam_start = datetime.now(timezone.utc) + timedelta(days=5)
    exam_end = exam_start + timedelta(hours=2)
    reservation = ReservationResponseDTO(
        id=1,
        user_id="user1",
        exam_schedule_id=1,  # ✅ 추가됨
        exam_start=exam_start,
        exam_end=exam_end,
        num_examinees=500,
        status=ReservationStatus.pending,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_repository.get_by_id.return_value = reservation

    await reservation_service.delete_reservation(1, "user1")
    mock_repository.delete.assert_called_once()
