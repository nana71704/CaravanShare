# src/models/user.py
from dataclasses import dataclass, field
import uuid
from src.models.common import UserRole # ❗️ import 경로 변경

@dataclass
class User:
    # 기본값이 없는 필드를 먼저 선언
    username: str
    role: UserRole
    
    # 기본값이 있는 필드를 나중에 선언
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trust_score: float = 5.0