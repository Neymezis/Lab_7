from typing import Optional
from uuid import UUID

from domain.order_aggregate import Order
from domain.money import Money
from domain.order_status import OrderStatus
from domain.domain_exceptions import (
    EmptyOrderException,
    OrderAlreadyPaidException
)
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
        2. Проверить, можно ли оплатить заказ
        3. Вызвать платежный шлюз
        4. Если платеж успешен, выполнить доменную операцию оплаты
        5. Сохранить обновленный заказ
        6. Вернуть результат
        
        Args:
            order_id: ID заказа для оплаты
            
        Returns:
            PaymentResult: результат операции оплаты
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
            # 2. Проверяем, можно ли оплатить заказ (те же проверки, что и в order.pay())
            if not order.lines:
                raise EmptyOrderException("Cannot pay empty order")
            
            if order.status == OrderStatus.PAID:
                raise OrderAlreadyPaidException("Order is already paid")
            
            # 3. Вызываем платежный шлюз
            amount = order.total_amount
            payment_result = self._payment_gateway.charge(order_id, amount)
            
            # 4. Если платеж успешен, выполняем доменную операцию
            if payment_result.success:
                order.pay()  # Теперь это безопасно - все проверки уже пройдены
                self._order_repository.save(order)
            
            return payment_result
            
        except Exception as e:
            # Возвращаем ошибку, если что-то пошло не так
            return PaymentResult(
                success=False,
                transaction_id="",
                message=str(e)
            )
