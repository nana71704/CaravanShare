# tests/test_caravan_service.py
import pytest
from unittest.mock import Mock

# --- 테스트 대상 ---
from src.services.caravan_service import CaravanService
from src.exceptions.custom_exceptions import ValidationError

# --- Mock 객체로 대체할 대상 ---
from src.repositories.base import CaravanRepository

# --- 테스트에 필요한 모델 ---
from src.models.user import User
from src.models.common import UserRole

@pytest.fixture
def mock_caravan_deps():
    """CaravanService의 의존성 Mock 객체를 만듭니다."""
    return {
        "caravan_repo": Mock(spec=CaravanRepository)
    }

@pytest.fixture
def host_user():
    """테스트용 호스트 유저를 만듭니다."""
    return User(username="TestHost", role=UserRole.HOST)

@pytest.fixture
def guest_user():
    """테스트용 게스트 유저를 만듭니다."""
    return User(username="TestGuest", role=UserRole.GUEST)


def test_register_caravan_fail_if_not_host(mock_caravan_deps, guest_user):
    """
    [CaravanService 테스트] 게스트가 카라반 등록 시도 시 ValidationError가 발생하는지 검증
    """
    # 1. 준비 (Arrange)
    caravan_repo = mock_caravan_deps["caravan_repo"]
    service = CaravanService(caravan_repo=caravan_repo)

    # 2. 실행 및 검증 (Act & Assert)
    with pytest.raises(ValidationError) as e:
        service.register_caravan(
            host=guest_user,  # ❗️ 게스트 유저
            name="게스트의 카라반",
            capacity=2
        )
    
    # [검증 1] 정확한 예외가 발생했는지?
    assert "호스트만 카라반을 등록할 수 있습니다." in str(e.value)
    
    # [검증 2] 리포지토리 'add'는 호출되지 않아야 함
    caravan_repo.add.assert_not_called()
    
    print("\n테스트 성공: CaravanService (권한 없음) 검증 완료")