# src/services/validators.py
from datetime import date
from src.constants import MIN_RESERVATION_DAYS # ❗️ import 경로 변경
from src.models.user import User # ❗️ import 경로 변경
from src.models.caravan import Caravan # ❗️ import 경로 변경
from src.models.common import UserRole, CaravanStatus # ❗️ import 경로 변경
from src.repositories.base import ReservationRepository # ❗️ import 경로 변경
from src.exceptions.custom_exceptions import ValidationError, ReservationConflictError # ❗️ import 경로 변경

class ReservationValidator:
    def __init__(self, repository: ReservationRepository):
        self._repository = repository

    def validate_reservation_request(self, guest: User, caravan: Caravan, start_date: date, end_date: date):
        print("검증기: 예약 검증 시작...")
        
        if not self._validate_user_role(guest):
            raise ValidationError("게스트만 예약을 신청할 수 있습니다.")
        
        if not self._validate_dates(start_date, end_date):
            raise ValidationError("예약 날짜가 유효하지 않습니다.")

        if not self._validate_caravan_status(caravan):
            raise ReservationConflictError("현재 예약 불가능한 카라반입니다.")

        if not self._repository.is_caravan_available(caravan.caravan_id, start_date, end_date):
            raise ReservationConflictError("선택한 날짜에 이미 예약이 있습니다.")
        
        print("검증기: 모든 검증 통과")
        return True

    def _validate_user_role(self, user: User) -> bool:
        return user.role == UserRole.GUEST

    def _validate_dates(self, start_date: date, end_date: date) -> bool:
        if start_date < date.today():
            return False
        if end_date < start_date:
            return False
        if (end_date - start_date).days < (MIN_RESERVATION_DAYS - 1):
            return False
        return True

    def _validate_caravan_status(self, caravan: Caravan) -> bool:
        return caravan.status == CaravanStatus.AVAILABLE