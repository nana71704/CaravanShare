# src/models/payment.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
import uuid

class PaymentStatus(Enum):
    PENDING = auto()  # 결제 대기
    COMPLETED = auto() # 결제 완료
    FAILED = auto()    # 결제 실패

@dataclass
class Payment:
    reservation_id: str
    amount: int
    
    payment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)