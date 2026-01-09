# Лабораторная работа 7: Архитектура, слои и DDD-lite

## Структура проекта

payment-system/
├── domain/                    # Доменный слой (бизнес-логика)
│   ├── __init__.py
│   ├── order.py              # Агрегат Order и OrderLine
│   ├── money.py              # Value Object Money
│   ├── order_status.py       # Enum OrderStatus
│   └── exceptions.py         # Доменные исключения
├── application/              # Слой приложения (use cases)
│   ├── __init__.py
│   ├── interfaces.py         # Интерфейсы OrderRepository и PaymentGateway
│   └── use_cases.py          # PayOrderUseCase
├── infrastructure/           # Инфраструктурный слой (реализации)
│   ├── __init__.py
│   ├── repositories.py       # InMemoryOrderRepository
│   └── payment_gateways.py   # FakePaymentGateway
├── tests/                    # Тесты
│   ├── __init__.py
│   ├── test_domain.py        # Тесты доменной модели
│   └── test_use_cases.py     # Тесты use-case
├── requirements.txt          # Зависимости проекта
└── README.md                 # Этот файл

