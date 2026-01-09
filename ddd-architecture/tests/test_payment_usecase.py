import pytest
from decimal import Decimal
from uuid import uuid4

from domain.order_aggregate import Order, OrderLine, OrderStatus
from domain.money import Money
from application.pay_order_usecase import PayOrderUseCase
from application.interfaces import PaymentResult
from infrastructure.order_repository import InMemoryOrderRepository
from infrastructure.payment_gateway import FakePaymentGateway


class TestPayOrderUseCase:
    """Тесты для use-case оплаты заказа"""
    
    @pytest.fixture
    def order_repository(self):
        return InMemoryOrderRepository()
    
    @pytest.fixture
    def successful_gateway(self):
        return FakePaymentGateway(always_succeed=True)
    
    @pytest.fixture
    def failing_gateway(self):
        return FakePaymentGateway(always_succeed=False)
    
    def create_test_order(self, repository: InMemoryOrderRepository) -> Order:
        """Создает тестовый заказ и сохраняет его в репозитории"""
        order = Order()
        line = OrderLine(
            product_id=uuid4(),
            product_name="Test Product",
            price=Money(Decimal("25.00")),
            quantity=3
        )
        order.add_line(line)
        repository.save(order)
        return order
    
    def test_successful_payment(self, order_repository, successful_gateway):
        """Тест успешной оплаты корректного заказа"""
        # Arrange
        order = self.create_test_order(order_repository)
        use_case = PayOrderUseCase(order_repository, successful_gateway)
        
        # Act
        result = use_case.execute(order.id)
        
        # Assert
        assert result.success is True
        assert "successfully" in result.message
        
        # Проверяем, что заказ обновлен в репозитории
        updated_order = order_repository.get_by_id(order.id)
        assert updated_order.status == OrderStatus.PAID
        
        # Проверяем, что платежный шлюз был вызван
        assert len(successful_gateway.processed_payments) == 1
        payment_record = successful_gateway.processed_payments[0]
        assert payment_record['order_id'] == order.id
        assert payment_record['amount'].amount == Decimal("75.00")
    
    def test_payment_of_empty_order_fails(self, order_repository, successful_gateway):
        """Тест ошибки при оплате пустого заказа"""
        # Arrange
        order = Order()  # Пустой заказ
        order_repository.save(order)
        use_case = PayOrderUseCase(order_repository, successful_gateway)
        
        # Act
        result = use_case.execute(order.id)
        
        # Assert
        assert result.success is False
        assert "Cannot pay empty order" in result.message
        
        # Заказ не должен быть оплачен
        updated_order = order_repository.get_by_id(order.id)
        assert updated_order.status == OrderStatus.DRAFT
    
    def test_double_payment_fails(self, order_repository, successful_gateway):
        """Тест ошибки при повторной оплате"""
        # Arrange
        order = self.create_test_order(order_repository)
        use_case = PayOrderUseCase(order_repository, successful_gateway)
        
        # Первая оплата
        first_result = use_case.execute(order.id)
        assert first_result.success is True
        
        # Вторая оплата
        second_result = use_case.execute(order.id)
        
        # Assert
        assert second_result.success is False
        assert "already paid" in second_result.message.lower()
    
    def test_order_not_found(self, order_repository, successful_gateway):
        """Тест обработки несуществующего заказа"""
        # Arrange
        use_case = PayOrderUseCase(order_repository, successful_gateway)
        non_existent_order_id = uuid4()
        
        # Act
        result = use_case.execute(non_existent_order_id)
        
        # Assert
        assert result.success is False
        assert "not found" in result.message.lower()
    
    def test_payment_gateway_failure(self, order_repository, failing_gateway):
        """Тест неудачной оплаты из-за платежного шлюза"""
        # Arrange
        order = self.create_test_order(order_repository)
        use_case = PayOrderUseCase(order_repository, failing_gateway)
        
        # Act
        result = use_case.execute(order.id)
        
        # Assert
        assert result.success is False
        assert "declined" in result.message.lower()
        
        # Заказ не должен быть оплачен, т.к. платеж не прошел
        updated_order = order_repository.get_by_id(order.id)
        assert updated_order.status == OrderStatus.DRAFT
    
    def test_correct_total_amount_sent_to_gateway(self, order_repository, successful_gateway):
        """Тест корректного расчета итоговой суммы при оплате"""
        # Arrange
        order = Order()
        
        # Добавляем товары с разными ценами и количествами
        lines = [
            OrderLine(
                product_id=uuid4(),
                product_name="Product A",
                price=Money(Decimal("10.99")),
                quantity=2
            ),
            OrderLine(
                product_id=uuid4(),
                product_name="Product B",
                price=Money(Decimal("5.49")),
                quantity=3
            )
        ]
        
        for line in lines:
            order.add_line(line)
        
        order_repository.save(order)
        use_case = PayOrderUseCase(order_repository, successful_gateway)
        
        # Рассчитываем ожидаемую сумму: 10.99*2 + 5.49*3 = 21.98 + 16.47 = 38.45
        expected_total = Decimal("38.45")
        
        # Act
        result = use_case.execute(order.id)
        
        # Assert
        assert result.success is True
        assert successful_gateway.processed_payments[0]['amount'].amount == expected_total
