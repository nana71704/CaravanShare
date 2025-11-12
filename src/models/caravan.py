# src/models/caravan.py
from dataclasses import dataclass, field
import uuid
from src.models.common import CaravanStatus # ❗️ import 경로 변경
from src.constants import DEFAULT_DAILY_RATE # ❗️ import 경로 변경

@dataclass
class Caravan:
    # 기본값 없는 필드
    host_id: str
    name: str
    capacity: int
    
    # 기본값 있는 필드
    caravan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    daily_rate: int = DEFAULT_DAILY_RATE
    status: CaravanStatus = CaravanStatus.AVAILABLE
    amenities: list[str] = field(default_factory=list)