# src/models/review.py
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class Review:
    reservation_id: str
    guest_id: str
    host_id: str
    rating: int  # 1~5점
    comment: str
    
    review_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)