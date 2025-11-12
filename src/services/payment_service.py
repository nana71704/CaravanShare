# src/services/payment_service.py
from src.repositories.base import PaymentRepository, ReservationRepository
from src.models.reservation import Reservation
from src.models.payment import Payment, PaymentStatus
from src.services.observers import NotificationService

class PaymentService:
    def __init__(
        self,
        payment_repo: PaymentRepository,
        reservation_repo: ReservationRepository,
        notification_service: NotificationService
    ):
        self._payment_repo = payment_repo
        self._reservation_repo = reservation_repo
        self._notification_service = notification_service

    def process_payment(self, reservation_id: str, amount: int) -> Payment:
        """
        결제 시도 및 처리를 담당합니다.
        (실제로는 PG사 연동 로직이 들어갑니다)
        """
        print(f"결제 서비스: {reservation_id}에 대한 결제 처리 시도...")
        
        # 1. 결제 객체 생성
        payment = Payment(reservation_id=reservation_id, amount=amount)
        
        # 2. (가정) PG사 결제 성공
        payment.status = PaymentStatus.COMPLETED
        
        # 3. DB에 저장
        self._payment_repo.add(payment)
        
        # 4. (옵저버) 결제 완료 알림
        # reservation = self._reservation_repo.get_by_id(reservation_id)
        # self._notification_service.send_notification(reservation.guest_id, "결제가 완료되었습니다.")
        
        print(f"결제 서비스: 결제 {payment.payment_id} 완료")
        return payment