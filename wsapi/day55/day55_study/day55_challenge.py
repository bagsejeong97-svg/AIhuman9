# day55_challenge.py
# 행사 좌석 예약 API

from uuid import uuid4
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Event Reservation API")

EVENTS = {
    1: {"title": "Python 취업 특강", "capacity": 5},
    2: {"title": "AI 프로젝트 발표회", "capacity": 8},
}

RESERVATIONS = {}

# 행사 ID, 예약자 이름, 좌석 수를 사전에 검증하는 BaseModel
class ReservationInput(BaseModel):
    event_id: int = Field(gt=0)
    guest_name: str = Field(min_length=2, max_length=40)
    seats: int = Field(ge=1, le=4)

# 확정 예약을 구분하기 위한 ID를 포함한 모델
class ReservationOutput(ReservationInput):
    reservation_id: str

def remaining(event_id: int):
    used = sum(r.seats for r in RESERVATIONS.values()
               if r.event_id == event_id)
    return EVENTS[event_id]["capacity"] - used

@app.get("/events")
def get_events():
    return [{"event_id": eid, **event,
             "remaining": remaining(eid)}
            for eid, event in EVENTS.items()]

@app.post("/reservations", response_model=ReservationOutput,
          status_code=status.HTTP_201_CREATED)
def reserve(data: ReservationInput):
    if data.event_id not in EVENTS:
        raise HTTPException(404, detail="행사가 없습니다")
    if data.seats > remaining(data.event_id):
        raise HTTPException(409, detail="남은 좌석이 부족합니다")
    item = ReservationOutput(
        reservation_id=uuid4().hex, **data.model_dump()
    )
    RESERVATIONS[item.reservation_id] = item
    return item

@app.get("/reservations/{reservation_id}",
         response_model=ReservationOutput)

def get_reservation(reservation_id: str):
    if reservation_id not in RESERVATIONS:
        raise HTTPException(404, detail="예약이 없습니다")
    return RESERVATIONS[reservation_id]

@app.delete("/reservations/{reservation_id}")
def delete_reservation(reservation_id: str):
    get_reservation(reservation_id)
    del RESERVATIONS[reservation_id]
    return {"cancelled": reservation_id}










