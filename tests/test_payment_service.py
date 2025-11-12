# tests/test_payment_service.py
import pytest
from unittest.mock import Mock, MagicMock

# --- 테스트 대상 ---
from src.services.payment_service import PaymentService

# --- Mock 객체로 대체할 대상 ---
from src.repositories.base import PaymentRepository, ReservationRepository
from src.services.observers import NotificationService

# --- 테스트에 필요한 모델 ---
from src.models.payment import PaymentStatus

@pytest.fixture
def mock_payment_deps():
    """PaymentService의 의존성 Mock 객체들을 만듭니다."""
    return {
        "payment_repo": Mock(spec=PaymentRepository),
        "reservation_repo": Mock(spec=ReservationRepository),
        "notification_service": Mock(spec=NotificationService)
    }

def test_process_payment_success(mock_payment_deps):
    """
    [PaymentService 테스트] 결제 처리가 성공적으로 완료되는지 검증
    """
    # 1. 준비 (Arrange)
    payment_repo = mock_payment_deps["payment_repo"]
    reservation_repo = mock_payment_deps["reservation_repo"]
    notifier = mock_payment_deps["notification_service"]

    # 테스트할 서비스 생성
    service = PaymentService(
        payment_repo=payment_repo,
        reservation_repo=reservation_repo,
        notification_service=notifier
    )
    
    test_reservation_id = "res-123"
    test_amount = 150000

    # 2. 실행 (Act)
    result_payment = service.process_payment(test_reservation_id, test_amount)

    # 3. 검증 (Assert)
    
    # [검증 1] 리포지토리에 'add'가 1번 호출되었는지?
    payment_repo.add.assert_called_once()
    
    # [검증 2] 반환된 Payment 객체의 상태가 'COMPLETED'인지?
    assert result_payment.status == PaymentStatus.COMPLETED
    
    # [검증 3] 반환된 Payment 객체의 금액이 일치하는지?
    assert result_payment.amount == test_amount

    print("\n테스트 성공: PaymentService (결제 성공) 로직 검증 완료")