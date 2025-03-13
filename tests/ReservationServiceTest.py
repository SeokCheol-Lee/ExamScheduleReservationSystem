import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.infrastructure.Database import Base
from app.interface.api import app, get_session
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from contextlib import asynccontextmanager
from fastapi import FastAPI

# ✅ FastAPI lifespan을 올바르게 설정
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ 올바른 방식으로 엔진 생성 (async with ❌)
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # ✅ 세션 팩토리 생성
    TestSession = async_sessionmaker(engine, expire_on_commit=False)

    # ✅ FastAPI 의존성 오버라이드 설정
    async def get_test_session():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session

    yield  # FastAPI 앱 실행 유지

    # ✅ 엔진 정리 (테스트 종료 후)
    await engine.dispose()

# ✅ FastAPI 애플리케이션을 실행하는 fixture
@pytest_asyncio.fixture(scope="session")
async def test_app():
    async with lifespan(app):
        yield app

# ✅ HTTP 클라이언트 설정 (FastAPI 서버와 연결 보장)
@pytest_asyncio.fixture(scope="function")
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_and_get_reservation(client):
    exam_start = datetime.now(timezone.utc) + timedelta(days=4)
    exam_end = exam_start + timedelta(hours=2)
    data = {
        "exam_start": exam_start.isoformat(),
        "exam_end": exam_end.isoformat(),
        "num_examinees": 1000
    }
    headers = {"X-User-Id": "user1", "X-User-Role": "customer"}
    response = await client.post("/reservations", json=data, headers=headers)
    assert response.status_code == 200, response.text

@pytest.mark.asyncio
async def test_update_and_delete_reservation(client):
    # 예약 생성 (시험 시작은 현재로부터 5일 후)
    exam_start = datetime.now(timezone.utc) + timedelta(days=5)
    exam_end = exam_start + timedelta(hours=2)
    data = {
        "exam_start": exam_start.isoformat(),
        "exam_end": exam_end.isoformat(),
        "num_examinees": 2000
    }
    headers = {"X-User-Id": "user2", "X-User-Role": "customer"}
    response = await client.post("/reservations", json=data, headers=headers)
    assert response.status_code == 200, response.text
    reservation = response.json()
    reservation_id = reservation["id"]

    # 예약 수정: 응시 인원 변경
    update_data = {"num_examinees": 2500}
    response = await client.put(f"/reservations/{reservation_id}", json=update_data, headers=headers)
    assert response.status_code == 200, response.text
    updated = response.json()
    assert updated["num_examinees"] == 2500

    # 예약 삭제
    response = await client.delete(f"/reservations/{reservation_id}", headers=headers)
    assert response.status_code == 200, response.text
    detail = response.json()
    assert "deleted" in detail["detail"]

@pytest.mark.asyncio
async def test_confirm_reservation(client):
    # 고객이 예약 생성 (시험 시작은 현재로부터 6일 후)
    exam_start = datetime.now(timezone.utc) + timedelta(days=6)
    exam_end = exam_start + timedelta(hours=2)
    data = {
        "exam_start": exam_start.isoformat(),
        "exam_end": exam_end.isoformat(),
        "num_examinees": 3000
    }
    headers_customer = {"X-User-Id": "user3", "X-User-Role": "customer"}
    headers_admin = {"X-User-Id": "admin1", "X-User-Role": "admin"}
    response = await client.post("/reservations", json=data, headers=headers_customer)
    assert response.status_code == 200, response.text
    reservation = response.json()
    reservation_id = reservation["id"]

    # 고객이 예약 확정 시도: 실패해야 함
    response = await client.post(f"/reservations/{reservation_id}/confirm", headers=headers_customer)
    assert response.status_code == 403

    # 어드민이 예약 확정: 성공해야 함
    response = await client.post(f"/reservations/{reservation_id}/confirm", headers=headers_admin)
    assert response.status_code == 200, response.text
    confirmed = response.json()
    assert confirmed["status"] == "confirmed"

@pytest.mark.asyncio
async def test_get_exam_schedules(client):
    # 동일 시험 일정에 대해 예약 생성 (시험 시작은 현재로부터 7일 후)
    exam_start = datetime.now(timezone.utc) + timedelta(days=7)
    exam_end = exam_start + timedelta(hours=2)
    data1 = {
        "exam_start": exam_start.isoformat(),
        "exam_end": exam_end.isoformat(),
        "num_examinees": 4000
    }
    data2 = {
        "exam_start": exam_start.isoformat(),
        "exam_end": exam_end.isoformat(),
        "num_examinees": 5000
    }
    headers = {"X-User-Id": "user4", "X-User-Role": "customer"}
    await client.post("/reservations", json=data1, headers=headers)
    await client.post("/reservations", json=data2, headers=headers)
    
    # 시험 일정 및 남은 용량 조회
    response = await client.get("/exam-schedules")
    assert response.status_code == 200, response.text
    schedules = response.json()
    # exam_start 필드가 ISO 포맷 문자열과 일치하는지 확인
    schedule = next((s for s in schedules if s["exam_start"] == exam_start.isoformat()), None)
    assert schedule is not None
    assert "confirmed_count" in schedule
    assert "available_capacity" in schedule
