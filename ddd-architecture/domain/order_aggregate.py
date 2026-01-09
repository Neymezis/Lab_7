from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import uuid4, UUID

from .order_status import OrderStatus
from .money import Money
from .domain_exceptions import (
    EmptyOrderException, 
    OrderAlreadyPaidException, 
    OrderModificationException
)


@dataclass
class OrderLine:
    """Строка заказа (часть агрегата Order)"""
    product_id: UUID
    product_name: str
    price: Money
    quantity: int
    
    @property
    def total(self) -> Money:
        """Вычисляет общую стоимость строки"""
        return self.price * self.quantity


class Order:
    """Агрегат корня - Заказ"""
    
    def __init__(
        self, 
        order_id: Optional[UUID] = None,
        customer_id: Optional[UUID] = None,
        lines: Optional[List[OrderLine]] = None,
        status: OrderStatus = OrderStatus.DRAFT
    ):
        self._id = order_id or uuid4()
        self._customer_id = customer_id or uuid4()
        self._lines = lines or []
        self._status = status
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        
        self._validate_invariants()
    
    @property
    def id(self) -> UUID:
        return self._id
    
    @property
    def customer_id(self) -> UUID:
        return self._customer_id
    
    @property
    def lines(self) -> List[OrderLine]:
        """Возвращает копию списка строк заказа"""
        return self._lines.copy()
    
    @property
    def status(self) -> OrderStatus:
        return self._status
    
    @property
    def total_amount(self) -> Money:
        """Вычисляет общую сумму заказа"""
        if not self._lines:
            return Money(Decimal('0'), "USD")
        
        total = self._lines[0].total
        for line in self._lines[1:]:
            total = total + line.total
        return total
    
    def add_line(self, line: OrderLine) -> None:
        """Добавляет строку в заказ"""
        if self._status == OrderStatus.PAID:
            raise OrderModificationException(
                "Cannot modify order after payment"
            )
        
        self._lines.append(line)
        self._updated_at = datetime.now()
        self._validate_invariants()
    
    def remove_line(self, product_id: UUID) -> None:
        """Удаляет строку из заказа по product_id"""
        if self._status == OrderStatus.PAID:
            raise OrderModificationException(
                "Cannot modify order after payment"
            )
        
        self._lines = [line for line in self._lines if line.product_id != product_id]
        self._updated_at = datetime.now()
        self._validate_invariants()
    
    def pay(self) -> None:
        """Оплачивает заказ - доменная операция"""
        # Инвариант: нельзя оплатить пустой заказ
        if not self._lines:
            raise EmptyOrderException("Cannot pay empty order")
        
        # Инвариант: нельзя оплатить заказ повторно
        if self._status == OrderStatus.PAID:
            raise OrderAlreadyPaidException("Order is already paid")
        
        self._status = OrderStatus.PAID
        self._updated_at = datetime.now()
    
    def _validate_invariants(self) -> None:
        """Проверяет инварианты агрегата"""
        # Инвариант: итоговая сумма равна сумме строк
        calculated_total = self.total_amount
        
        if self._lines:
            lines_sum = self._lines[0].total
            for line in self._lines[1:]:
                lines_sum = lines_sum + line.total
            
            if calculated_total.amount != lines_sum.amount:
                raise ValueError(
                    f"Total amount mismatch: {calculated_total.amount} != {lines_sum.amount}"
                )
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
