from enum import Enum

class OrderStatus(Enum):
    """Статусы заказа"""
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
