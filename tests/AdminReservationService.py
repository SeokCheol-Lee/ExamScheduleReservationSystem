import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timedelta, timezone
from app.application.ReservationDto import (
    ReservationCreateDTO,
    ReservationUpdateDTO,
    ReservationResponseDTO
)
from app.application.AdminReservationService import AdminReservationService
from app.domain.Reservation import Reservation, ReservationStatus

@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    return repo

@pytest.fixture
def admin_reservation_service(mock_repository):
    return AdminReservationService(repository=mock_repository)

# 전체 예약 조회 테스트
@pytest.mark.asyncio
async def test_get_all_reservations(admin_reservation_service, mock_repository):
    reservations = [
        ReservationResponseDTO(id=1, user_id="user1", exam_schedule_id=1, exam_start=datetime.now(timezone.utc),
                               exam_end=datetime.now(timezone.utc) + timedelta(hours=2), num_examinees=100,
                               status=ReservationStatus.pending, created_at=datetime.now(timezone.utc),
                               updated_at=datetime.now(timezone.utc)),
    ]
    mock_repository.list_all.return_value = reservations

    result = await admin_reservation_service.get_all_reservations()
    
    assert len(result) == 1
    assert result[0]["id"] == 1
    mock_repository.list_all.assert_called_once()

# 예약 확정 테스트
@pytest.mark.asyncio
async def test_confirm_reservation(admin_reservation_service, mock_repository):
    reservation = Reservation(id=1, user_id="user1", exam_schedule_id=1, exam_start=datetime.now(timezone.utc),
                              exam_end=datetime.now(timezone.utc) + timedelta(hours=2), num_examinees=100,
                              status=ReservationStatus.pending, created_at=datetime.now(timezone.utc),
                              updated_at=datetime.now(timezone.utc))
    mock_repository.get_by_id.return_value = reservation
    mock_repository.get_exam_schedule_by_id.return_value = AsyncMock(capacity=500, confirmed_count=100)
    mock_repository.get_confirmed_sum.return_value = 100
    mock_repository.update.return_value = reservation
    
    result = await admin_reservation_service.confirm_reservation(1)
    
    assert result["status"] == ReservationStatus.confirmed.value
    mock_repository.update.assert_called_once()

# 예약 수정 테스트
@pytest.mark.asyncio
async def test_update_reservation(admin_reservation_service, mock_repository):
    reservation = Reservation(id=1, user_id="user1", exam_schedule_id=1, exam_start=datetime.now(timezone.utc),
                              exam_end=datetime.now(timezone.utc) + timedelta(hours=2), num_examinees=100,
                              status=ReservationStatus.pending, created_at=datetime.now(timezone.utc),
                              updated_at=datetime.now(timezone.utc))
    mock_repository.get_by_id.return_value = reservation
    mock_repository.get_exam_schedule_by_id.return_value = AsyncMock(capacity=500, confirmed_count=100)
    mock_repository.get_confirmed_sum.return_value = 100
    mock_repository.update.return_value = reservation
    
    dto = ReservationUpdateDTO(num_examinees=150)
    result = await admin_reservation_service.update_reservation(1, dto)
    
    assert result["num_examinees"] == 150
    mock_repository.update.assert_called_once()

# 예약 삭제 테스트
@pytest.mark.asyncio
async def test_delete_reservation(admin_reservation_service, mock_repository):
    reservation = Reservation(id=1, user_id="user1", exam_schedule_id=1, exam_start=datetime.now(timezone.utc),
                              exam_end=datetime.now(timezone.utc) + timedelta(hours=2), num_examinees=100,
                              status=ReservationStatus.pending, created_at=datetime.now(timezone.utc),
                              updated_at=datetime.now(timezone.utc))
    mock_repository.get_by_id.return_value = reservation
    
    await admin_reservation_service.delete_reservation(1)
    
    mock_repository.delete.assert_called_once()
