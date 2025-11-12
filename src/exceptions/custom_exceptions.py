# src/exceptions/custom_exceptions.py

class CaravanShareError(Exception):
    """베이스 예외"""
    pass

class ValidationError(CaravanShareError):
    """입력값 검증 실패"""
    def __init__(self, message="입력값이 유효하지 않습니다."):
        self.message = message
        super().__init__(self.message)

class ReservationConflictError(CaravanShareError):
    """예약 충돌 또는 불가능"""
    def __init__(self, message="해당 날짜에 예약할 수 없습니다."):
        self.message = message
        super().__init__(self.message)