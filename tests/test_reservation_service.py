# tests/test_reservation_service.py
import pytest
from datetime import date, timedelta
from unittest.mock import Mock, MagicMock # ❗️ MagicMock 추가

# --- 테스트할 대상 ---
from src.services.reservation_service import ReservationService

# --- 테스트에 필요한 모델 ---
from src.models.user import User
from src.models.caravan import Caravan
from src.models.reservation import Reservation
from src.models.common import UserRole

# --- Mock 객체로 대체할 대상 ---
from src.services.validators import ReservationValidator
from src.repositories.base import ReservationRepository
from src.services.factories import ReservationFactory
from src.services.strategies import PriceCalculator, LongStayDiscountStrategy # ❗️ LongStayDiscountStrategy 추가
from src.services.observers import NotificationService


# --- 테스트 준비 (Fixtures) ---

@pytest.fixture
def mock_dependencies():
    """ReservationService가 의존하는 모든 객체를 Mock으로 만듭니다."""
    return {
        "validator": Mock(spec=ReservationValidator),
        "repository": Mock(spec=ReservationRepository),
        "factory": Mock(spec=ReservationFactory),
        "price_calculator": Mock(spec=PriceCalculator),
        "notification_service": Mock(spec=NotificationService)
    }

@pytest.fixture
def sample_data():
    """테스트에 사용할 기본 데이터를 만듭니다."""
    guest = User(username="TestGuest", role=UserRole.GUEST)
    caravan = Caravan(host_id="Host", name="TestCaravan", capacity=4)
    start_date = date.today() + timedelta(days=10)
    end_date = date.today() + timedelta(days=16) # 7일 예약
    return guest, caravan, start_date, end_date

# --- 테스트 케이스 ---

def test_create_reservation_success_long_stay(mock_dependencies, sample_data):
    """
    [Service 테스트] 7일 장기 예약 시, 모든 서비스가 올바르게 호출되는지 검증
    """
    # 1. 준비 (Arrange)
    validator = mock_dependencies["validator"]
    repo = mock_dependencies["repository"]
    factory = mock_dependencies["factory"]
    price_calc = mock_dependencies["price_calculator"]
    notifier = mock_dependencies["notification_service"]
    
    guest, caravan, start_date, end_date = sample_data
    
    # --- ❗️ 1. [AttributeError] 수정 ---
    # 서비스 코드가 f-string (f"...{new_reservation.reservation_id}")에서 
    # Mock 객체의 'reservation_id' 속성에 접근하므로, 미리 값을 설정해줘야 합니다.
    # 'MagicMock'은 f-string 변환 등에 더 유연하게 대처합니다.
    mock_reservation = MagicMock(spec=Reservation)
    mock_reservation.reservation_id = "test-mock-id-123" # 가짜 ID 설정

    # Mock 객체의 반환값 설정
    validator.validate_reservation_request.return_value = True # 검증 통과
    price_calc.calculate_total_price.return_value = 630000 # 10% 할인된 가격
    factory.create_reservation.return_value = mock_reservation # 수정된 Mock 객체 반환
    
    # 테스트 대상인 ReservationService를 Mock 객체들을 주입하여 생성
    service = ReservationService(
        validator=validator,
        repository=repo,
        factory=factory,
        price_calculator=price_calc,
        notification_service=notifier
    )

    # 2. 실행 (Act)
    service.create_reservation(guest, caravan, start_date, end_date)

    # 3. 검증 (Assert)
    
    # [검증 1] Validator가 올바른 인자로 1번 호출되었는가?
    validator.validate_reservation_request.assert_called_once_with(
        guest, caravan, start_date, end_date
    )
    
    # --- ❗️ 2. [AssertionError] 수정 ---
    # 이전 코드는 객체 '인스턴스'를 비교하려 해서 실패했습니다. (테스트 객체 vs 서비스 객체)
    # 'set_strategy'가 호출되었는지, 그리고 그 인자가 'LongStayDiscountStrategy'의
    # *인스턴스(타입)*가 맞는지 확인하는 것이 올바른 방법입니다.
    price_calc.set_strategy.assert_called_once() # 1. 일단 호출되었는지 확인
    args, _ = price_calc.set_strategy.call_args  # 2. 호출된 인자(args)를 가져옴
    assert isinstance(args[0], LongStayDiscountStrategy) # 3. 인자의 타입이 맞는지 확인

    # [검증 3] 가격 계산기가 1번 호출되었는가?
    price_calc.calculate_total_price.assert_called_once()
    
    # [검증 4] Factory가 1번 호출되었는가?
    factory.create_reservation.assert_called_once()
    
    # [검증 5] Repository가 1번 호출되었는가? (DB에 저장)
    repo.add.assert_called_once_with(mock_reservation)
    
    # [검증 6] 알림이 2번(게스트, 호스트) 호출되었는가?
    assert notifier.send_notification.call_count == 2
    
    print("\n테스트 성공: ReservationService 핵심 로직 검증 완료")

    # tests/test_reservation_service.py 에 추가

# --- (추가 테스트 1) 할인 없는 5일 예약 ---
def test_create_reservation_success_short_stay(mock_dependencies, sample_data):
    """
    [Service 테스트] 5일 단기 예약 시, NoDiscountStrategy가 설정되는지 검증
    """
    # 1. 준비 (Arrange)
    validator = mock_dependencies["validator"]
    repo = mock_dependencies["repository"]
    factory = mock_dependencies["factory"]
    price_calc = mock_dependencies["price_calculator"]
    notifier = mock_dependencies["notification_service"]
    
    # sample_data는 7일 예약이므로 날짜만 수정
    guest, caravan, start_date, _ = sample_data
    end_date = start_date + timedelta(days=4) # 5일 예약
    
    # Mock 객체 반환값 설정
    mock_reservation = MagicMock(spec=Reservation)
    mock_reservation.reservation_id = "test-mock-id-456"
    
    validator.validate_reservation_request.return_value = True
    price_calc.calculate_total_price.return_value = 500000
    factory.create_reservation.return_value = mock_reservation
    
    service = ReservationService(
        validator=validator,
        repository=repo,
        factory=factory,
        price_calculator=price_calc,
        notification_service=notifier
    )

    # 2. 실행 (Act)
    service.create_reservation(guest, caravan, start_date, end_date)

    # 3. 검증 (Assert)
    
    # [검증 1] Validator가 호출되었는지 확인
    validator.validate_reservation_request.assert_called_once_with(
        guest, caravan, start_date, end_date
    )
    
    # [검증 2] ❗️ NoDiscountStrategy가 설정되었는지 확인
    price_calc.set_strategy.assert_called_once()
    args, _ = price_calc.set_strategy.call_args
    # pytest.approx() 대신 'NoDiscountStrategy' 타입인지 확인합니다.
    # (이전 테스트에서 사용한 isinstance() 방식과 동일하게 수정)
    from src.services.strategies import NoDiscountStrategy
    assert isinstance(args[0], NoDiscountStrategy)

    # [검증 3] Repository가 호출되었는지 확인
    repo.add.assert_called_once_with(mock_reservation)
    
    # [검증 4] 알림이 2번 호출되었는지 확인
    assert notifier.send_notification.call_count == 2

    print("\n테스트 성공: Service (단기 예약) 로직 검증 완료")

    # tests/test_reservation_service.py 에 추가

# --- (추가 테스트 2) 검증기(Validator) 실패 시나리오 ---
def test_create_reservation_fails_if_validation_fails(mock_dependencies, sample_data):
    """
    [Service 테스트] Validator가 예외를 발생시켰을 때, Service가 중단되는지 검증
    """
    # 1. 준비 (Arrange)
    validator = mock_dependencies["validator"]
    repo = mock_dependencies["repository"]
    factory = mock_dependencies["factory"]
    price_calc = mock_dependencies["price_calculator"]
    
    guest, caravan, start_date, end_date = sample_data
    
    # ❗️ 검증기가 ValidationError를 발생시킨다고 설정
    from src.exceptions.custom_exceptions import ValidationError
    validator.validate_reservation_request.side_effect = ValidationError("테스트 검증 실패")
    
    service = ReservationService(
        validator=validator,
        repository=repo,
        factory=factory,
        price_calculator=price_calc,
        notification_service=mock_dependencies["notification_service"] # notifier
    )

    # 2. 실행 (Act)
    result = service.create_reservation(guest, caravan, start_date, end_date)

    # 3. 검증 (Assert)
    
    # [검증 1] Validator는 호출되어야 함
    validator.validate_reservation_request.assert_called_once()
    
    # [검증 2] ❗️ 검증 실패 시, 가격 계산, 팩토리, 리포지토리는 *호출되지 않아야 함*
    price_calc.calculate_total_price.assert_not_called()
    factory.create_reservation.assert_not_called()
    repo.add.assert_not_called()
    
    # [검증 3] ❗️ 실패했으므로 None을 반환해야 함
    assert result is None
    
    print("\n테스트 성공: Service (검증 실패) 로직 검증 완료")