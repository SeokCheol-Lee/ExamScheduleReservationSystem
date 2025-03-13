# 시험 일정 예약 시스템 API 개발
## 기능
### 1. 예약 조회 및 신청
- 고객은 예약 가능한 시간과 인원을 확인할 수 있습니다.
- 예약은 시험 시작 3일 전까지 신청 가능합니다.
- 동시간대 최대 5만 명까지 예약 가능하며, 확정되지 않은 예약은 인원 제한에서 제외됩니다.
- 고객은 자신의 예약만 조회할 수 있으며, 어드민은 모든 예약을 조회할 수 있습니다.

### 2. 예약 수정 및 확정
- 고객은 예약 확정 전까지 본인의 예약을 수정할 수 있습니다.
- 어드민은 모든 고객의 예약을 수정할 수 있습니다.
- 어드민이 예약을 확정하면, 시험 운영 일정에 반영됩니다.

### 3. 예약 삭제
- 고객은 확정 전까지 본인의 예약을 삭제할 수 있습니다.
- 어드민은 모든 고객의 예약을 삭제할 수 있습니다.

## 기술 스택
- **언어**: Python (FastAPI)
- **데이터베이스**: PostgreSQL
- **인증**: 간단한 헤더 기반 인증 (JWT/OAuth2 권장)

## API 명세
### 1. 예약 조회
**GET `/reservations`**
- 응답:
    ```json
    [
        {
            "id": 1,
            "user_id": "user123",
            "exam_id": 1,
            "date": "2025-05-01T10:00:00",
            "status": "pending"
        }
    ]
    ```

### 2. 예약 신청
**POST `/reservations`**
- 요청 바디:
  ```json
  {
    "exam_schedule_id": 1,
    "expected_attendees": 10000
  }
  ```
- 응답 바디:
    ```json
    {
  "id": 1,
  "user_id": "user123",
  "exam_id": 1,
  "date": "2025-05-01T10:00:00",
  "status": "pending"
    }
    ```
### 3. 예약 수정
**PUT /reservations/{reservation_id}**

- 요청 바디:
    ```json
    {
        "date": "2025-06-01T15:00:00"
    }
    ```
- 응답 바디:
    ```json
    {
        "id": 1,
        "user_id": "user123",
        "exam_id": 1,
        "date": "2025-06-01T15:00:00",
        "status": "pending"
    }
    ```
### 4. 예약 삭제
**DELETE /reservations/{reservation_id}**
- 응답 바디:
    ```json
    {
        "detail": "Reservation deleted"
    }
    ```

### 5. 예약 확인 (관리자 전용)
**POST /reservations/{reservation_id}/confirm**
- 응답 바디:
    ```json
    {
        "id": 1,
        "user_id": "user123",
        "exam_id": 1,
        "date": "2025-06-01T15:00:00",
        "status": "confirmed"
    }
    ```
### 6. 시험 일정 조회
**GET /exam-schedules**
- 응답 바디:
    ```json
    [
        {
            "exam_id": 1,
            "subject": "Mathematics",
            "date": "2025-06-01T15:00:00"
        }
    ]
    ```