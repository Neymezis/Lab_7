# Лабораторная работа 7: Архитектура, слои и DDD-lite

## Структура проекта

ddd-architecture/
    domain/                    # Доменный слой
        __init__.py
        entities.py            # Сущности (Order, OrderLine)
        value_objects.py       # Value Objects (Money)
        enums.py               # Перечисления (OrderStatus)
        exceptions.py          # Доменные исключения
        interfaces.py          # Интерфейсы (порты)
    application/               # Слой приложения
        __init__.py
        use_cases.py           # Use Cases (PayOrderUseCase)
    infrastructure/            # Инфраструктурный слой
        __init__.py
        repositories.py        # Реализация репозиториев
        gateways.py            # Реализация шлюзов
    tests/                     # Тесты
        __init__.py
        test_pay_order_use_case.py
    README.md
    requirements.txt
