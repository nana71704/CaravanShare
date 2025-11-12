# tests/test_review_service.py
import pytest
from unittest.mock import Mock

# --- 테스트 대상 ---
from src.services.review_service import ReviewService
from src.exceptions.custom_exceptions import ValidationError

# --- Mock 객체로 대체할 대상 ---
from src.repositories.base import ReviewRepository, ReservationRepository

@pytest.fixture
def mock_review_deps():
    """ReviewService의 의존성 Mock 객체들을 만듭니다."""
    # 리뷰 중복 검사를 위해 'get_by_reservation_id'가 None을 반환하도록 설정
    review_repo = Mock(spec=ReviewRepository)
    review_repo.get_by_reservation_id.return_value = None 
    
    return {
        "review_repo": review_repo,
        "reservation_repo": Mock(spec=ReservationRepository)
    }

def test_create_review_fail_invalid_rating(mock_review_deps):
    """
    [ReviewService 테스트] 별점이 1~5 범위를 벗어날 때 ValidationError가 발생하는지 검증
    """
    # 1. 준비 (Arrange)
    review_repo = mock_review_deps["review_repo"]
    reservation_repo = mock_review_deps["reservation_repo"]

    service = ReviewService(
        review_repo=review_repo,
        reservation_repo=reservation_repo
    )
    
    # ❗️ 0점이라는 유효하지 않은 별점
    invalid_rating = 0

    # 2. 실행 및 검증 (Act & Assert)
    with pytest.raises(ValidationError) as e:
        service.create_review(
            reservation_id="res-123",
            guest_id="guest-abc",
            host_id="host-xyz",
            rating=invalid_rating,
            comment="별점이 0점"
        )
    
    # [검증 1] 정확한 예외가 발생했는지?
    assert "별점은 1점에서 5점 사이여야 합니다." in str(e.value)
    
    # [검증 2] 예외가 발생했으므로 리포지토리 'add'는 호출되지 않아야 함
    review_repo.add.assert_not_called()

    print("\n테스트 성공: ReviewService (잘못된 별점) 검증 완료")