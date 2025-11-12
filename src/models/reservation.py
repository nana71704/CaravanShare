# src/models/reservation.py
from dataclasses import dataclass, field
from datetime import date
import uuid
from src.models.common import ReservationStatus # ❗️ import 경로 변경

@dataclass
class Reservation:
    # 기본값 없는 필드
    guest_id: str
    caravan_id: str
    start_date: date
    end_date: date
    total_price: int
    
    # 기본값 있는 필드
    reservation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ReservationStatus = ReservationStatus.PENDING