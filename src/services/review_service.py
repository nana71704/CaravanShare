# src/services/review_service.py
from src.repositories.base import ReviewRepository, ReservationRepository
from src.models.review import Review
from src.exceptions.custom_exceptions import ValidationError

class ReviewService:
    def __init__(
        self,
        review_repo: ReviewRepository,
        reservation_repo: ReservationRepository
    ):
        self._review_repo = review_repo
        self._reservation_repo = reservation_repo

    def create_review(self, reservation_id: str, guest_id: str, host_id: str, rating: int, comment: str) -> Review:
        """
        리뷰를 작성합니다.
        """
        print(f"리뷰 서비스: {reservation_id}에 대한 리뷰 작성 시도...")
        
        # 1. 검증: 이미 리뷰가 작성되었는지?
        if self._review_repo.get_by_reservation_id(reservation_id):
            raise ValidationError("이미 이 예약에 대한 리뷰를 작성했습니다.")
        
        # 2. 검증: 별점 범위 (1-5)
        if not (1 <= rating <= 5):
            raise ValidationError("별점은 1점에서 5점 사이여야 합니다.")
        
        # 3. 리뷰 객체 생성 및 저장
        review = Review(
            reservation_id=reservation_id,
            guest_id=guest_id,
            host_id=host_id,
            rating=rating,
            comment=comment
        )
        self._review_repo.add(review)
        
        # 4. (확장) 호스트의 신뢰도 점수(trust_score) 업데이트 로직 추가 가능
        
        print(f"리뷰 서비스: 리뷰 {review.review_id} 생성 완료")
        return review