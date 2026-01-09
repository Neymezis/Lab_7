from typing import Dict, Optional
from uuid import UUID

from domain.order_aggregate import Order
from application.interfaces import OrderRepository


class InMemoryOrderRepository(OrderRepository):
    """In-memory реализация репозитория заказов"""
    
    def __init__(self):
        self._storage: Dict[UUID, Order] = {}
    
    def get_by_id(self, order_id: UUID) -> Optional[Order]:
        return self._storage.get(order_id)
    
    def save(self, order: Order) -> None:
        self._storage[order.id] = order
