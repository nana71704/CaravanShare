# src/repositories/memory_repository.py
from datetime import date, timedelta
from src.models.reservation import Reservation
from src.repositories.base import ReservationRepository
from src.exceptions.custom_exceptions import ReservationConflictError

class InMemoryReservationRepository(ReservationRepository):
    """
    메모리 기반 리포지토리 구현체
    """
    def __init__(self):
        self._reservations: dict[str, Reservation] = {}
        self._bookings_by_caravan: dict[str, dict[date, str]] = {}

    def add(self, reservation: Reservation):
        if reservation.reservation_id in self._reservations:
            raise ReservationConflictError(f"예약 ID {reservation.reservation_id}가 이미 존재합니다.")
        
        self._reservations[reservation.reservation_id] = reservation
        
        if reservation.caravan_id not in self._bookings_by_caravan:
            self._bookings_by_caravan[reservation.caravan_id] = {}
            
        current_date = reservation.start_date
        while current_date <= reservation.end_date:
            self._bookings_by_caravan[reservation.caravan_id][current_date] = reservation.reservation_id
            current_date += timedelta(days=1)
        
        print(f"리포지토리: 예약 {reservation.reservation_id} 추가됨")

    def get_by_id(self, reservation_id: str) -> Reservation | None:
        return self._reservations.get(reservation_id)

    def is_caravan_available(self, caravan_id: str, start_date: date, end_date: date) -> bool:
        caravan_bookings = self._bookings_by_caravan.get(caravan_id, {})
        
        current_date = start_date
        while current_date <= end_date:
            if current_date in caravan_bookings:
                return False
            current_date += timedelta(days=1)
            
        return True

# --- Payment & Review Repositories ---
from src.repositories.base import PaymentRepository, ReviewRepository
from src.models.payment import Payment
from src.models.review import Review

class InMemoryPaymentRepository(PaymentRepository):
    def __init__(self):
        self._payments: dict[str, Payment] = {}

    def add(self, payment: Payment):
        self._payments[payment.payment_id] = payment
        print(f"결제 리포지토리: 결제 {payment.payment_id} 추가됨")

    def get_by_id(self, payment_id: str) -> Payment | None:
        # vvv --- 수정된 부분 --- vvv
        return self._payments.get(payment_id) # ❗️ ']' 기호 삭제
        # ^^^ --- 수정된 부분 --- ^^^

class InMemoryReviewRepository(ReviewRepository):
    def __init__(self):
        self._reviews: dict[str, Review] = {} # review_id 기준
        self._reviews_by_reservation: dict[str, Review] = {} # reservation_id 기준

    def add(self, review: Review):
        self._reviews[review.review_id] = review
        self._reviews_by_reservation[review.reservation_id] = review
        print(f"리뷰 리포지토리: 리뷰 {review.review_id} 추가됨")

    def get_by_reservation_id(self, reservation_id: str) -> Review | None:
        return self._reviews_by_reservation.get(reservation_id)

# --- Caravan & User Repositories ---
from src.repositories.base import CaravanRepository
from src.models.caravan import Caravan

class InMemoryCaravanRepository(CaravanRepository):
    def __init__(self):
        self._caravans: dict[str, Caravan] = {}

    def add(self, caravan: Caravan):
        self._caravans[caravan.caravan_id] = caravan
        print(f"카라반 리포지토리: 카라반 {caravan.caravan_id} 추가됨")

    def get_by_id(self, caravan_id: str) -> Caravan | None:
        return self._caravans.get(caravan_id)

    def search_by_capacity(self, min_capacity: int) -> list[Caravan]:
        return [
            caravan for caravan in self._caravans.values()
            if caravan.capacity >= min_capacity
        ]

from src.repositories.base import UserRepository
from src.models.user import User

class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users_by_id: dict[str, User] = {}
        self._users_by_username: dict[str, User] = {}

    def add(self, user: User):
        self._users_by_id[user.user_id] = user
        self._users_by_username[user.username] = user
        print(f"사용자 리포지토리: {user.username} 추가됨")

    def get_by_username(self, username: str) -> User | None:
        return self._users_by_username.get(username)