class DomainException(Exception):
    """Базовое исключение домена"""
    pass


class EmptyOrderException(DomainException):
    """Нельзя оплатить пустой заказ"""
    pass


class OrderAlreadyPaidException(DomainException):
    """Нельзя оплатить заказ повторно"""
    pass


class OrderModificationException(DomainException):
    """Нельзя изменить оплаченный заказ"""
    pass
