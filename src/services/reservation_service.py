# src/services/reservation_service.py
from datetime import date
from src.models.user import User # ❗️ import 경로 변경
from src.models.caravan import Caravan # ❗️ import 경로 변경
from src.services.validators import ReservationValidator # ❗️ import 경로 변경
from src.repositories.base import ReservationRepository # ❗️ import 경로 변경
from src.services.factories import ReservationFactory # ❗️ import 경로 변경
from src.services.strategies import PriceCalculator, LongStayDiscountStrategy, NoDiscountStrategy # ❗️ import 경로 변경
from src.services.observers import NotificationService # ❗️ import 경로 변경
from src.exceptions.custom_exceptions import ValidationError, ReservationConflictError # ❗️ import 경로 변경

class ReservationService:
    def __init__(
        self,
        validator: ReservationValidator,
        repository: ReservationRepository,
        factory: ReservationFactory,
        price_calculator: PriceCalculator,
        notification_service: NotificationService
    ):
        self._validator = validator
        self._repository = repository
        self._factory = factory
        self._price_calculator = price_calculator
        self._notification_service = notification_service

    def create_reservation(self, guest: User, caravan: Caravan, start_date: date, end_date: date):
        try:
            self._validator.validate_reservation_request(guest, caravan, start_date, end_date)
            
            rental_days = (end_date - start_date).days + 1
            if rental_days >= 7:
                self._price_calculator.set_strategy(LongStayDiscountStrategy())
            else:
                self._price_calculator.set_strategy(NoDiscountStrategy())
                
            total_price = self._price_calculator.calculate_total_price(
                caravan.daily_rate, start_date, end_date
            )
            
            new_reservation = self._factory.create_reservation(
                guest_id=guest.user_id,
                caravan_id=caravan.caravan_id,
                start_date=start_date,
                end_date=end_date,
                total_price=total_price
            )
            
            self._repository.add(new_reservation)
            
            self._notification_service.send_notification(
                user_id=guest.user_id,
                message=f"예약 신청이 완료되었습니다. (ID: {new_reservation.reservation_id})"
            )
            self._notification_service.send_notification(
                user_id=caravan.host_id,
                message=f"{caravan.name}에 새로운 예약 신청이 있습니다. 승인이 필요합니다."
            )
            
            return new_reservation

        except (ValidationError, ReservationConflictError) as e:
            print(f"예약 실패: {e.message}")
            return None
        except Exception as e:
            print(f"알 수 없는 오류 발생: {e}")
            return None