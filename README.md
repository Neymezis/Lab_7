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
    requirements.txt
</pre>
