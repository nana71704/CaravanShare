# src/services/caravan_service.py
from src.models.user import User
from src.models.caravan import Caravan
from src.models.common import UserRole
from src.repositories.base import CaravanRepository
from src.exceptions.custom_exceptions import ValidationError

class CaravanService:
    def __init__(self, caravan_repo: CaravanRepository):
        self._caravan_repo = caravan_repo

    def register_caravan(
        self,
        host: User,
        name: str,
        capacity: int
    ) -> Caravan:
        """
        [MVP 1-2] 호스트가 카라반을 등록합니다.
        """
        # 1. 검증: 호스트만 등록 가능
        if host.role != UserRole.HOST:
            raise ValidationError("호스트만 카라반을 등록할 수 있습니다.")
        
        # 2. 검증: 수용 인원은 1명 이상
        if capacity < 1:
            raise ValidationError("수용 인원은 1명 이상이어야 합니다.")
            
        # 3. 객체 생성 및 저장
        caravan = Caravan(
            host_id=host.user_id,
            name=name,
            capacity=capacity
        )
        self._caravan_repo.add(caravan)
        
        print(f"카라반 서비스: {host.username}님이 {name} 카라반 등록 완료")
        return caravan

    def search_caravans(self, guest: User, min_capacity: int) -> list[Caravan]:
        """
        [MVP 1-2] 게스트가 카라반을 검색합니다.
        """
        # 1. 검증: 게스트만 검색 가능
        if guest.role != UserRole.GUEST:
            raise ValidationError("게스트만 카라반을 검색할 수 있습니다.")
        
        print(f"카라반 서비스: {guest.username}님이 수용 인원 {min_capacity}명 이상 검색")
        return self._caravan_repo.search_by_capacity(min_capacity)