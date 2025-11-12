# src/services/strategies.py
from abc import ABC, abstractmethod
from datetime import date

class DiscountStrategy(ABC):
    """할인 전략 인터페이스"""
    @abstractmethod
    def calculate_discount(self, original_price: int, rental_days: int) -> int:
        pass

class NoDiscountStrategy(DiscountStrategy):
    """할인 없음"""
    def calculate_discount(self, original_price: int, rental_days: int) -> int:
        return 0

class LongStayDiscountStrategy(DiscountStrategy):
    """장기 숙박 할인 (7일 이상 10%)"""
    def calculate_discount(self, original_price: int, rental_days: int) -> int:
        if rental_days >= 7:
            return int(original_price * 0.1)
        return 0

class PriceCalculator:
    def __init__(self, strategy: DiscountStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: DiscountStrategy):
        self._strategy = strategy

    def calculate_total_price(self, daily_rate: int, start_date: date, end_date: date) -> int:
        rental_days = (end_date - start_date).days + 1
        original_price = daily_rate * rental_days
        
        discount = self._strategy.calculate_discount(original_price, rental_days)
        
        total_price = original_price - discount
        print(f"가격 계산: 원가 {original_price} - 할인 {discount} = 총 {total_price}")
        return total_price