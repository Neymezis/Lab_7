from typing import Optional
from uuid import UUID

from domain.order_aggregate import Order
from domain.money import Money
from domain.order_status import OrderStatus
from .interfaces import OrderRepository, PaymentGateway, PaymentResult


class PayOrderUseCase:
    """Use Case для оплаты заказа"""
    
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
            # Сохраняем исходный статус
            original_status = order.status
            
            # 2. Доменная операция оплаты (меняет статус на PAID)
            order.pay()
            amount = order.total_amount
            
            # 3. Вызываем платежный шлюз
            payment_result = self._payment_gateway.charge(order_id, amount)
            
            # 4. Если платеж успешен, сохраняем заказ
            if payment_result.success:
                self._order_repository.save(order)
            else:
                # Если платеж не прошел, восстанавливаем исходный статус
                order._status = original_status
            
            return payment_result
            
        except Exception as e:
            # Возвращаем ошибку, если что-то пошло не так
            return PaymentResult(
                success=False,
                transaction_id="",
                message=str(e)
            )
