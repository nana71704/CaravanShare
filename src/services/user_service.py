# src/services/user_service.py
from src.models.user import User
from src.models.common import UserRole
from src.repositories.base import UserRepository
from src.exceptions.custom_exceptions import ValidationError

class UserService:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def register_user(self, username: str, role: UserRole) -> User:
        """
        [MVP 1-1] 사용자를 등록합니다 (회원가입).
        """
        # 1. 검증: 이미 존재하는 사용자 이름인지?
        if self._user_repo.get_by_username(username):
            raise ValidationError(f"사용자 이름 '{username}'(은)는 이미 존재합니다.")
        
        # 2. 검증: 사용자 이름 길이
        if not (3 <= len(username) <= 20):
            raise ValidationError("사용자 이름은 3자 이상 20자 이하이어야 합니다.")
            
        # 3. 객체 생성 및 저장
        user = User(username=username, role=role)
        self._user_repo.add(user)
        
        print(f"사용자 서비스: {username} ({role.name})님 회원가입 완료")
        return user