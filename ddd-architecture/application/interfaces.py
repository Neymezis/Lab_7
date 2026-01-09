from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from decimal import Decimal
from dataclasses import dataclass

from domain.order_aggregate import Order
from domain.money import Money


class OrderRepository(ABC):
    """Интерфейс репозитория заказов"""
    
    @abstractmethod
    def get_by_id(self, order_id: UUID) -> Optional[Order]:
        """Получить заказ по ID"""
        pass
    
    @abstractmethod
    def save(self, order: Order) -> None:
        """Сохранить заказ"""
        pass


@dataclass
class PaymentResult:
    """Результат платежа"""
    success: bool
    transaction_id: str
    message: str = ""


class PaymentGateway(ABC):
    """Интерфейс платежного шлюза"""
    
    @abstractmethod
    def charge(self, order_id: UUID, amount: Money) -> PaymentResult:
        """
        Выполнить платеж
        
        Args:
            order_id: ID заказа
            amount: сумма платежа
            
        Returns:
            PaymentResult: результат платежа
        """
        pass
