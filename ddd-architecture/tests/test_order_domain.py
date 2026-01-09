import pytest
from decimal import Decimal
from uuid import uuid4

from domain.order_status import OrderStatus
from domain.money import Money
from domain.order_aggregate import Order, OrderLine
from domain.domain_exceptions import (
    EmptyOrderException,
    OrderAlreadyPaidException,
    OrderModificationException
)


class TestOrderLine:
    """Тесты для OrderLine"""
    
    def test_order_line_total_calculation(self):
        """Тест расчета общей стоимости строки заказа"""
        # Arrange
        price = Money(Decimal("10.50"))
        line = OrderLine(
            product_id=uuid4(),
            product_name="Test Product",
            price=price,
            quantity=3
        )
        
        # Act & Assert
        expected_total = Money(Decimal("31.50"))  # 10.50 * 3
        assert line.total == expected_total


class TestOrder:
    """Тесты для агрегата Order"""
    
    def test_create_order_with_lines(self):
        """Тест создания заказа с товарами"""
        # Arrange
        order = Order()
        line = OrderLine(
            product_id=uuid4(),
            product_name="Product",
            price=Money(Decimal("15.99")),
            quantity=2
        )
        
        # Act
        order.add_line(line)
        
        # Assert
        assert len(order.lines) == 1
        assert order.total_amount.amount == Decimal("31.98")
        assert order.status == OrderStatus.DRAFT
    
    def test_cannot_pay_empty_order(self):
        """Тест: нельзя оплатить пустой заказ"""
        # Arrange
        order = Order()
        
        # Act & Assert
        with pytest.raises(EmptyOrderException):
            order.pay()
    
    def test_cannot_pay_already_paid_order(self):
        """Тест: нельзя оплатить уже оплаченный заказ"""
        # Arrange
        order = Order()
        line = OrderLine(
            product_id=uuid4(),
            product_name="Product",
            price=Money(Decimal("10.00")),
            quantity=1
        )
        order.add_line(line)
        
        # Первая оплата
        order.pay()
        
        # Вторая оплата должна вызвать исключение
        with pytest.raises(OrderAlreadyPaidException):
            order.pay()
    
    def test_cannot_modify_order_after_payment(self):
        """Тест: нельзя изменить заказ после оплаты"""
        # Arrange
        order = Order()
        line1 = OrderLine(
            product_id=uuid4(),
            product_name="Product 1",
            price=Money(Decimal("5.00")),
            quantity=2
        )
        order.add_line(line1)
        order.pay()  # Оплачиваем заказ
        
        # Act & Assert - попытка добавить новый товар
        line2 = OrderLine(
            product_id=uuid4(),
            product_name="Product 2",
            price=Money(Decimal("3.00")),
            quantity=1
        )
        
        with pytest.raises(OrderModificationException):
            order.add_line(line2)
    
    def test_total_amount_calculation(self):
        """Тест корректного расчета суммы заказа"""
        # Arrange
        order = Order()
        
        lines = [
            OrderLine(
                product_id=uuid4(),
                product_name=f"Product {i}",
                price=Money(Decimal(f"{i + 1}.50")),
                quantity=i + 1
            )
            for i in range(3)
        ]
        
        # Act
        for line in lines:
            order.add_line(line)
        
        # Assert
        # 1.50 * 1 + 2.50 * 2 + 3.50 * 3 = 1.50 + 5.00 + 10.50 = 17.00
        expected_total = Decimal("17.00")
        assert order.total_amount.amount == expected_total
    
    def test_remove_line_from_order(self):
        """Тест удаления строки из заказа"""
        # Arrange
        order = Order()
        product_id_to_remove = uuid4()
        
        line1 = OrderLine(
            product_id=uuid4(),
            product_name="Product 1",
            price=Money(Decimal("10.00")),
            quantity=1
        )
        line2 = OrderLine(
            product_id=product_id_to_remove,
            product_name="Product 2",
            price=Money(Decimal("20.00")),
            quantity=1
        )
        
        order.add_line(line1)
        order.add_line(line2)
        
        # Act
        order.remove_line(product_id_to_remove)
        
        # Assert
        assert len(order.lines) == 1
        assert order.lines[0].product_id == line1.product_id
        assert order.total_amount.amount == Decimal("10.00")
    
    def test_cannot_remove_line_from_paid_order(self):
        """Тест: нельзя удалить строку из оплаченного заказа"""
        # Arrange
        order = Order()
        product_id = uuid4()
        
        line = OrderLine(
            product_id=product_id,
            product_name="Product",
            price=Money(Decimal("15.00")),
            quantity=1
        )
        order.add_line(line)
        order.pay()
        
        # Act & Assert
        with pytest.raises(OrderModificationException):
            order.remove_line(product_id)
