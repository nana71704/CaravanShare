# tests/test_validators.py
import pytest
from datetime import date, timedelta

# ❗️ 테스트 대상 클래스 import
from src.services.validators import ReservationValidator
from src.exceptions.custom_exceptions import ValidationError, ReservationConflictError

# ❗️ 테스트에 필요한 모델 import
from src.models.user import User
from src.models.caravan import Caravan
from src.models.common import UserRole, CaravanStatus

# ❗️ Mock 객체를 만들기 위해 import
from unittest.mock import Mock


# --- 테스트를 위한 '고정' 데이터 (Fixture) ---
@pytest.fixture
def mock_repo():
    """
    가짜(Mock) 리포지토리를 만듭니다. 
    이 리포지토리는 항상 '예약 가능'하다고(True) 응답합니다.
    """
    repo = Mock()
    repo.is_caravan_available.return_value = True
    return repo

@pytest.fixture
def guest_user():
    """테스트용 게스트 유저를 만듭니다."""
    return User(username="TestGuest", role=UserRole.GUEST)

@pytest.fixture
def available_caravan():
    """테스트용 카라반을 만듭니다."""
    return Caravan(host_id="Host", name="TestCaravan", capacity=4, status=CaravanStatus.AVAILABLE)

# --- 1. 날짜 검증 테스트 ---
def test_validate_dates_fail_if_past_date(mock_repo, guest_user, available_caravan):
    """
    [요구사항 2 테스트] 과거 날짜로 예약을 시도하면 ValidationError가 발생해야 한다.
    """
    # 준비 (Arrange)
    validator = ReservationValidator(repository=mock_repo)
    past_date = date.today() - timedelta(days=1)
    future_date = date.today() + timedelta(days=3)

    # 실행 및 검증 (Act & Assert)
    with pytest.raises(ValidationError) as e:
        validator.validate_reservation_request(guest_user, available_caravan, past_date, future_date)
    
    # 에러 메시지 검증
    assert "예약 날짜가 유효하지 않습니다." in str(e.value)
    print("\n테스트 성공: 과거 날짜 검증 완료")

# --- 2. 예약 충돌 테스트 ---
def test_validate_fail_if_repository_reports_conflict(guest_user, available_caravan):
    """
    [요구사항 2/3 테스트] 리포지토리가 '예약 불가능(False)'을 반환하면 ReservationConflictError가 발생해야 한다.
    """
    # 준비 (Arrange)
    # ❗️ 이번에는 '예약 불가능'하다고 응답할 Mock Repo를 새로 만듭니다.
    conflict_repo = Mock()
    conflict_repo.is_caravan_available.return_value = False # ⬅️ 충돌 발생!
    
    validator = ReservationValidator(repository=conflict_repo)
    start_date = date.today() + timedelta(days=10)
    end_date = date.today() + timedelta(days=15)

    # 실행 및 검증 (Act & Assert)
    with pytest.raises(ReservationConflictError) as e:
        validator.validate_reservation_request(guest_user, available_caravan, start_date, end_date)
    
    assert "선택한 날짜에 이미 예약이 있습니다." in str(e.value)
    print("\n테스트 성공: 예약 충돌 검증 완료")