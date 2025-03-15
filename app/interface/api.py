from fastapi import FastAPI, Depends, HTTPException, Header, status
from typing import List, Optional
from app.infrastructure.Database import async_session, engine, Base
from app.infrastructure.ReservationRepository import ReservationRepository
from app.application.ReservationService import ReservationService
from app.application.AdminReservationService import AdminReservationService
from app.application.ExamScheduleService import ExamScheduleService
from app.application.ReservationDto import ReservationCreateDTO, ReservationUpdateDTO
from app.application.ExamScheduleDto import ExamScheduleCreateDTO, ExamScheduleResponseDTO
import uvicorn

app = FastAPI(title="시험 일정 예약 시스템 API")

# DB 세션 의존성
async def get_session():
    async with async_session() as session:
        yield session

# 단순 사용자 모델 (실제 프로젝트에서는 JWT/OAuth2 사용 권장)
class User:
    def __init__(self, user_id: str, role: str):
        self.user_id = user_id
        self.role = role

# 현재 사용자 의존성 (헤더 사용)
async def get_current_user(
    x_user_id: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header("customer")
):
    if x_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-User-Id header missing")
    return User(user_id=x_user_id, role=x_user_role)

# ReservationService 의존성 주입
async def get_reservation_service(session=Depends(get_session)):
    repo = ReservationRepository(session)
    return ReservationService(repo)

# AdminReservationService 의존성 주입
async def get_admin_reservation_service(session=Depends(get_session)):
    repo = ReservationRepository(session)
    return AdminReservationService(repo)

# ExamScheduleService 의존성 주입
async def get_exam_schedule_service(session=Depends(get_session)):
    repo = ReservationRepository(session)
    return ExamScheduleService(repo)

# API 엔드포인트

# 고객: 예약 생성
@app.post("/reservations", response_model=dict)
async def create_reservation(
    dto: ReservationCreateDTO,
    current_user: User = Depends(get_current_user),
    service: ReservationService = Depends(get_reservation_service)
):
    try:
        reservation = await service.create_reservation(current_user.user_id, dto)
        return reservation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 고객: 내 예약 조회
@app.get("/reservations", response_model=List[dict])
async def get_my_reservations(
    current_user: User = Depends(get_current_user),
    service: ReservationService = Depends(get_reservation_service)
):
    try:
        reservations = await service.get_my_reservations(current_user.user_id)
        return reservations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 고객: 예약 수정
@app.put("/reservations/{reservation_id}", response_model=dict)
async def update_reservation(
    reservation_id: int,
    dto: ReservationUpdateDTO,
    current_user: User = Depends(get_current_user),
    service: ReservationService = Depends(get_reservation_service)
):
    try:
        reservation = await service.update_reservation(reservation_id, current_user.user_id, dto)
        return reservation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 고객: 예약 삭제
@app.delete("/reservations/{reservation_id}")
async def delete_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    service: ReservationService = Depends(get_reservation_service)
):
    try:
        await service.delete_reservation(reservation_id, current_user.user_id)
        return {"detail": "Reservation deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 관리자: 예약 확정
@app.post("/reservations/{reservation_id}/confirm", response_model=dict)
async def confirm_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    service: AdminReservationService = Depends(get_admin_reservation_service)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can confirm reservations")
    try:
        reservation = await service.confirm_reservation(reservation_id)
        return reservation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 관리자: 전체 예약 조회
@app.get("/admin/reservations", response_model=List[dict])
async def get_all_reservations(
    current_user: User = Depends(get_current_user),
    service: AdminReservationService = Depends(get_admin_reservation_service)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view all reservations")
    try:
        reservations = await service.get_all_reservations()
        return reservations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 관리자: 시험 일정 생성
@app.post("/admin/exam-schedules", response_model=ExamScheduleResponseDTO)
async def create_exam_schedule(
    dto: ExamScheduleCreateDTO,
    current_user: User = Depends(get_current_user),
    service: ExamScheduleService = Depends(get_exam_schedule_service)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create exam schedules")
    try:
        schedule = await service.create_exam_schedule(dto)
        return schedule
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 시험 일정 조회 (모든 사용자)
@app.get("/exam-schedules", response_model=List[dict])
async def get_exam_schedules(
    service: ExamScheduleService = Depends(get_exam_schedule_service)
):
    try:
        schedules = await service.get_exam_schedules()
        return schedules
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 애플리케이션 시작 시 테이블 생성
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)