# Лабораторная работа 7: Архитектура, слои и DDD-lite

## Структура проекта

<pre>
ddd-architecture/
    domain/                    # Доменный слой
        __init__.py
        order_aggregate.py     # Агрегат Order с OrderLine
        money.py               # Value Object Money
        order_status.py        # Enum OrderStatus
        domain_exceptions.py   # Доменные исключения
    application/               # Слой приложения
        __init__.py
        interfaces.py          # Интерфейсы репозитория и платежного шлюза
        pay_order_usecase.py   # PayOrderUseCase
    infrastructure/            # Инфраструктурный слой
        __init__.py
        order_repository.py    # InMemoryOrderRepository
        payment_gateway.py     # FakePaymentGateway
    tests/                     # Тесты
        __init__.py
        test_order_domain.py   # Тесты доменной модели
        test_payment_usecase.py # Тесты use-case
    README.md
</pre>

## Доменная модель

### Сущности
<code>Order</code> - заказ (корень агрегата)<br>
<code>OrderLine</code> - строка заказа (часть агрегата)

### Value Objects
<code>Money</code> - денежная сумма с валютой

### Перечисления
<code>OrderStatus</code> - статус заказа (DRAFT, PENDING, PAID, CANCELLED)

### Бизнес-инварианты
1. Нельзя оплатить пустой заказ
2. Нельзя оплатить заказ повторно
3. После оплаты нельзя менять строки заказа
4. Итоговая сумма равна сумме строк

## Интерфейсы

### OrderRepository
<pre>
<code>
def get_by_id(order_id: UUID) -> Order | None
def save(order: Order) -> None
</code>
</pre>

### PaymentGateway
<pre>
<code>
def charge(order_id: UUID, money: Money) -> PaymentResult
</code>
</pre>

## Use Cases

### PayOrderUseCase
Оркестрирует процесс оплаты заказа:

1. Загружает заказ через OrderRepository
2. Выполняет доменную операцию оплаты
3. Вызывает платёж через PaymentGateway
4. Сохраняет заказ
5. Возвращает результат оплаты

## Запуск тестов

<pre>
<code>
# Установка зависимостей
pip install -r requirements.txt

# Запуск тестов
pytest
</code>
</pre>

## Тестовые сценарии

1. Успешная оплата корректного заказа
2. Ошибка при оплате пустого заказа
3. Ошибка при повторной оплате
4. Невозможность изменения заказа после оплаты
5. Корректный расчёт итоговой суммы
