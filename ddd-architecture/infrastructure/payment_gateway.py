from datetime import datetime
from uuid import uuid4, UUID

from domain.money import Money
from application.interfaces import PaymentGateway, PaymentResult


class FakePaymentGateway(PaymentGateway):
    """Фейковый платежный шлюз для тестирования"""
    
    def __init__(self, always_succeed: bool = True):
        """
        Args:
            always_succeed: если True, все платежи успешны
        """
        self.always_succeed = always_succeed
        self.processed_payments = []
    
    def charge(self, order_id: UUID, amount: Money) -> PaymentResult:
        """Имитирует процесс платежа"""
        
        # Записываем информацию о платеже для тестирования
        payment_record = {
            'order_id': order_id,
            'amount': amount,
            'timestamp': datetime.now()
        }
        self.processed_payments.append(payment_record)
        
        # Генерируем случайный transaction_id
        transaction_id = str(uuid4())
        
        # Возвращаем результат в зависимости от настройки
        if self.always_succeed:
            return PaymentResult(
                success=True,
                transaction_id=transaction_id,
                message="Payment processed successfully"
            )
        else:
            return PaymentResult(
                success=False,
                transaction_id=transaction_id,
                message="Payment declined by gateway"
            )
