# tests/test_user_service.py
import pytest
from unittest.mock import Mock

# --- 테스트 대상 ---
from src.services.user_service import UserService
from src.exceptions.custom_exceptions import ValidationError

# --- Mock 객체로 대체할 대상 ---
from src.repositories.base import UserRepository

# --- 테스트에 필요한 모델 ---
from src.models.user import User
from src.models.common import UserRole

@pytest.fixture
def mock_user_repo():
    """UserService의 의존성 Mock 객체를 만듭니다."""
    return Mock(spec=UserRepository)

def test_register_user_fail_if_username_exists(mock_user_repo):
    """
    [UserService 테스트] 이미 존재하는 이름으로 가입 시 ValidationError가 발생하는지 검증
    """
    # 1. 준비 (Arrange)
    
    # ❗️ get_by_username이 'TestUser'를 반환하도록 설정 (이미 존재함)
    existing_user = User(username="TestUser", role=UserRole.GUEST)
    mock_user_repo.get_by_username.return_value = existing_user
    
    service = UserService(user_repo=mock_user_repo)

    # 2. 실행 및 검증 (Act & Assert)
    with pytest.raises(ValidationError) as e:
        service.register_user(
            username="TestUser",  # ❗️ 이미 존재하는 이름
            role=UserRole.HOST
        )
    
    # [검증 1] 정확한 예외가 발생했는지?
    assert "이미 존재합니다." in str(e.value)
    
    # [검증 2] 리포지토리 'add'는 호출되지 않아야 함
    mock_user_repo.add.assert_not_called()
    
    print("\n테스트 성공: UserService (중복 가입) 검증 완료")