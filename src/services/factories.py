# src/services/factories.py
from datetime import date
from src.models.reservation import Reservation, ReservationStatus # ❗️ import 경로 변경

class ReservationFactory:
    def create_reservation(self, guest_id: str, caravan_id: str, start_date: date, end_date: date, total_price: int) -> Reservation:
        """예약 객체 생성을 담당"""
        print("팩토리: 예약 객체 생성 중...")
        return Reservation(
            guest_id=guest_id,
            caravan_id=caravan_id,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            status=ReservationStatus.PENDING
        )