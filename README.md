# 시험 일정 예약 시스템 API 개발
## 1. 환경 설정

### 1.1 필수 사항

- **Docker** 및 **Docker Compose** (PostgreSQL 실행)
- **Python 3.10 이상**
- **Git**

### 1.2 프로젝트 클론

터미널(또는 CMD)에서 아래 명령어로 저장소를 클론합니다.

```bash
git clone https://github.com/SeokCheol-Lee/ExamScheduleReservationSystem.git
cd ExamScheduleReservationSystem
```

## 2. Docker를 활용한 PostgreSQL 설정

로컬에 PostgreSQL이 설치되어 있지 않다면 Docker 컨테이너로 실행할 수 있습니다.

터미널에서 다음 명령어를 실행하세요:

```bash
docker run --name reservation-postgres \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=Reservation \
  -p 5432:5432 \
  -d postgres:latest
```

설명:
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`는 .env 파일에 지정한 값과 동일하게 맞춥니다.
- `-p 5432:5432`는 컨테이너의 PostgreSQL 포트를 로컬 포트에 매핑합니다.
- 버전은 필요에 따라 변경할 수 있습니다.

---

## 3. API 문서
### Base URL

```
http://localhost:8000
```
- **테스트 문서(Swagger)** 
    ```
        http://localhost:8000/docs
    ```

### 3.1 Exam Schedules

#### GET /exam-schedules

- **설명:** 모든 시험 일정을 조회합니다.
- **Method:** GET
- **URL:** `/exam-schedules`
- **Response 예시:**

```json
[
  {
    "id": 1,
    "exam_start": "2025-04-15T14:00:00+00:00",
    "exam_end": "2025-04-15T16:00:00+00:00",
    "capacity": 50000,
    "confirmed_count": 30000,
    "available_capacity": 20000
  },
  {
    "id": 2,
    "exam_start": "2025-05-20T10:00:00+00:00",
    "exam_end": "2025-05-20T12:00:00+00:00",
    "capacity": 50000,
    "confirmed_count": 0,
    "available_capacity": 50000
  }
]
```

---

### 3.2 Reservations

#### POST /reservations

- **설명:** 예약 신청 (고객은 시험 일정에 예약을 신청합니다)
- **Method:** POST
- **URL:** `/reservations`
- **Headers:**
  - `x-user-id`: 사용자 ID (예: "1")
  - `x-user-role`: 사용자 역할 (예: "customer")
  - `Content-Type`: application/json
- **Request Body 예시:**

```json
{
  "exam_schedule_id": 3,
  "num_examinees": 1
}
```

- **Response 예시:**

```json
{
  "id": 10,
  "user_id": "1",
  "exam_schedule_id": 3,
  "exam_start": "2025-04-15T14:00:00+00:00",
  "exam_end": "2025-04-15T16:00:00+00:00",
  "num_examinees": 1,
  "status": "pending",
  "created_at": "2025-03-15T19:55:00+00:00",
  "updated_at": "2025-03-15T19:55:00+00:00"
}
```

#### GET /reservations

- **설명:** 로그인한 고객의 예약 내역을 조회합니다.
- **Method:** GET
- **URL:** `/reservations`
- **Headers:**
  - `x-user-id`: 사용자 ID
  - `x-user-role`: "customer"
- **Response 예시:**

```json
[
  {
    "id": 10,
    "user_id": "1",
    "exam_schedule_id": 3,
    "exam_start": "2025-04-15T14:00:00+00:00",
    "exam_end": "2025-04-15T16:00:00+00:00",
    "num_examinees": 1,
    "status": "pending",
    "created_at": "2025-03-15T19:55:00+00:00",
    "updated_at": "2025-03-15T19:55:00+00:00"
  }
]
```

#### PUT /reservations/{reservation_id}

- **설명:** 예약 수정 (예약 확정 전, 고객은 본인의 예약을 수정할 수 있습니다)
- **Method:** PUT
- **URL:** `/reservations/{reservation_id}`
- **Headers:**
  - `x-user-id`: 사용자 ID
  - `x-user-role`: "customer" 또는 "admin"
- **Request Body 예시:**

```json
{
  "num_examinees": 2
}
```

- **Response 예시:**

```json
{
  "id": 10,
  "user_id": "1",
  "exam_schedule_id": 3,
  "exam_start": "2025-04-15T14:00:00+00:00",
  "exam_end": "2025-04-15T16:00:00+00:00",
  "num_examinees": 2,
  "status": "pending",
  "created_at": "2025-03-15T19:55:00+00:00",
  "updated_at": "2025-03-15T19:57:00+00:00"
}
```

#### DELETE /reservations/{reservation_id}

- **설명:** 예약 삭제 (고객은 확정 전 본인의 예약만 삭제 가능하며, 관리자 권한으로 모든 예약 삭제 가능)
- **Method:** DELETE
- **URL:** `/reservations/{reservation_id}`
- **Headers:**
  - `x-user-id`: 사용자 ID
  - `x-user-role`: "customer" 또는 "admin"
- **Response:** HTTP 204 No Content

#### POST /reservations/{reservation_id}/confirm

- **설명:** 예약 확정 (관리자 전용 – 예약을 확정하여 최종적으로 시험 운영에 반영)
- **Method:** POST
- **URL:** `/reservations/{reservation_id}/confirm`
- **Headers:**
  - `x-user-id`: 관리자 ID
  - `x-user-role`: "admin"
- **Response 예시:**

```json
{
  "id": 10,
  "user_id": "1",
  "exam_schedule_id": 3,
  "exam_start": "2025-04-15T14:00:00+00:00",
  "exam_end": "2025-04-15T16:00:00+00:00",
  "num_examinees": 1,
  "status": "confirmed",
  "created_at": "2025-03-15T19:55:00+00:00",
  "updated_at": "2025-03-15T19:58:00+00:00"
}
```