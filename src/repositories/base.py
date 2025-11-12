# src/repositories/base.py
from abc import ABC, abstractmethod
from datetime import date
from src.models.reservation import Reservation # ❗️ import 경로 변경

class ReservationRepository(ABC):
    """리포지토리 인터페이스 (DIP, 의존성 역전 원칙)"""
    @abstractmethod
    def add(self, reservation: Reservation):
        pass

    @abstractmethod
    def get_by_id(self, reservation_id: str) -> Reservation | None:
        pass

    @abstractmethod
    def is_caravan_available(self, caravan_id: str, start_date: date, end_date: date) -> bool:
        pass

    # src/repositories/base.py
# ... (기존 ReservationRepository 코드) ...

# ❗️ 아래 두 클래스를 파일 맨 아래에 추가하세요.
from src.models.payment import Payment
from src.models.review import Review

class PaymentRepository(ABC):
    @abstractmethod
    def add(self, payment: Payment):
        pass

    @abstractmethod
    def get_by_id(self, payment_id: str) -> Payment | None:
        pass

class ReviewRepository(ABC):
    @abstractmethod
    def add(self, review: Review):
        pass

    @abstractmethod
    def get_by_reservation_id(self, reservation_id: str) -> Review | None:
        pass

    # src/repositories/base.py
# ... (기존 PaymentRepository, ReviewRepository 코드 아래에 추가) ...
from src.models.caravan import Caravan

class CaravanRepository(ABC):
    @abstractmethod
    def add(self, caravan: Caravan):
        pass

    @abstractmethod
    def get_by_id(self, caravan_id: str) -> Caravan | None:
        pass
    
    @abstractmethod
    def search_by_capacity(self, min_capacity: int) -> list[Caravan]:
        pass

    # src/repositories/base.py
# ... (기존 CaravanRepository 코드 아래에 추가) ...
from src.models.user import User

class UserRepository(ABC):
    @abstractmethod
    def add(self, user: User):
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        pass