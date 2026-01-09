import pytest
from decimal import Decimal
from uuid import uuid4
from datetime import datetime

from domain.order_aggregate import Order, OrderLine
from domain.money import Money
from domain.order_status import OrderStatus
from application.pay_order_usecase import PayOrderUseCase
from application.interfaces import PaymentResult
from infrastructure.order_repository import InMemoryOrderRepository
from infrastructure.payment_gateway import FakePaymentGateway
class PayOrderUseCase:
    
    def __init__(
        self, 
        order_repository: OrderRepository,
        payment_gateway: PaymentGateway
    ):
        self._order_repository = order_repository
        self._payment_gateway = payment_gateway
    
    def execute(self, order_id: UUID) -> PaymentResult:
        """
        Выполнить оплату заказа
        
        Шаги:
        1. Загрузить заказ из репозитория
        2. Выполнить доменную операцию оплаты
        3. Вызвать платёж через PaymentGateway
        4. Сохранить заказ (только если платеж успешен)
        5. Вернуть результат оплаты
        """
        # 1. Загружаем заказ
        order = self._order_repository.get_by_id(order_id)
        if order is None:
            return PaymentResult(
                success=False,
                transaction_id="",
                message=f"Order {order_id} not found"
            )
        
        try:
            # 2. Доменная операция оплаты (проверяет инварианты)
            order.pay()
            amount = order.total_amount
            
            # 3. Вызываем платежный шлюз
            payment_result = self._payment_gateway.charge(order_id, amount)
            
            # 4. Если платеж успешен, сохраняем заказ
            if payment_result.success:
                self._order_repository.save(order)
            else:
                # Если платеж не прошел, откатываем статус заказа
                # В реальной системе здесь была бы транзакция или компенсирующее действие
                # Для простоты создаем новый объект с исходным статусом
                order._status = OrderStatus.PENDING
            
            return payment_result
            
        except Exception as e:
            # Возвращаем ошибку, если что-то пошло не так
            return PaymentResult(
                success=False,
                transaction_id="",
                message=str(e)
            )
