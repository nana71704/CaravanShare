# src/models/common.py
from enum import Enum, auto

class UserRole(Enum):
    HOST = auto()
    GUEST = auto()

class CaravanStatus(Enum):
    AVAILABLE = auto()
    RESERVED = auto()
    MAINTENANCE = auto()

class ReservationStatus(Enum):
    PENDING = auto()
    CONFIRMED = auto()
    CANCELLED = auto()
    COMPLETED = auto()