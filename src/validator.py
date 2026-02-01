"""
Валидация входных данных (STOP и WARN)
"""
from typing import List
from src.models import InputData, ValidationError, Order, Stock


def validate_input_data(data: InputData) -> List[ValidationError]:
    """
    Выполнить все проверки STOP и WARN
    Возвращает список ошибок
    """
    errors = []
    
    # STOP проверки (критические)
    errors.extend(validate_stop_conditions(data))
    
    # WARN проверки (предупреждения)
    errors.extend(validate_warn_conditions(data))
    
    return errors


def validate_stop_conditions(data: InputData) -> List[ValidationError]:
    """
    STOP валидация (критические ошибки)
    C1: Дубликаты Order ID
    C2: Дубликаты SKU в остатках
    C3: Quantity <= 0 в заказах
    C4: Quantity < 0 в остатках
    """
    errors = []
    
    # C1: Проверка на дубликаты Order ID
    order_ids = [o.order_id for o in data.orders]
    duplicates = set([oid for oid in order_ids if order_ids.count(oid) > 1])
    if duplicates:
        errors.append(ValidationError(
            level="STOP",
            code="C1",
            message="Дубликаты Order ID",
            details=f"Повторяющиеся ID: {', '.join(sorted(duplicates))}"
        ))
    
    # C2: Проверка на дубликаты SKU в остатках
    stock_skus = [s.sku for s in data.stock]
    dup_skus = set([sku for sku in stock_skus if stock_skus.count(sku) > 1])
    if dup_skus:
        errors.append(ValidationError(
            level="STOP",
            code="C2",
            message="Дубликаты SKU в остатках",
            details=f"Повторяющиеся SKU: {', '.join(sorted(dup_skus))}"
        ))
    
    # C3: Проверка quantity <= 0 в заказах
    invalid_orders = [o.order_id for o in data.orders if o.qty <= 0]
    if invalid_orders:
        errors.append(ValidationError(
            level="STOP",
            code="C3",
            message="Недопустимое количество в заказах (qty <= 0)",
            details=f"Заказы: {', '.join(invalid_orders)}"
        ))
    
    # C4: Проверка quantity < 0 в остатках
    invalid_stock = [s.sku for s in data.stock if s.qty < 0]
    if invalid_stock:
        errors.append(ValidationError(
            level="STOP",
            code="C4",
            message="Недопустимое количество в остатках (qty < 0)",
            details=f"SKU: {', '.join(invalid_stock)}"
        ))
    
    return errors


def validate_warn_conditions(data: InputData) -> List[ValidationError]:
    """
    WARN валидация (предупреждения, не блокируют выполнение)
    B1: SKU в заказах отсутствует в остатках
    B2: Резерв > остаток
    B3: Есть заказы класса C
    """
    errors = []
    
    # B1: SKU в заказах отсутствует в остатках
    stock_skus = set([s.sku for s in data.stock])
    missing_skus = set()
    for order in data.orders:
        if order.sku not in stock_skus:
            missing_skus.add(order.sku)
    
    if missing_skus:
        errors.append(ValidationError(
            level="WARN",
            code="B1",
            message="SKU отсутствует в остатках",
            details=f"SKU: {', '.join(sorted(missing_skus))}"
        ))
    
    # B2: Резерв > остаток
    excessive_reserves = []
    for stock_item in data.stock:
        if stock_item.reserved > stock_item.qty:
            excessive_reserves.append(f"{stock_item.sku} (резерв {stock_item.reserved} > остаток {stock_item.qty})")
    
    if excessive_reserves:
        errors.append(ValidationError(
            level="WARN",
            code="B2",
            message="Резерв превышает остаток",
            details="; ".join(excessive_reserves)
        ))
    
    # B3: Есть заказы класса C
    class_c_orders = [o.order_id for o in data.orders if o.priority_class == 'C']
    if class_c_orders:
        errors.append(ValidationError(
            level="WARN",
            code="B3",
            message="Обнаружены заказы класса C (низкий приоритет)",
            details=f"Заказы: {', '.join(class_c_orders)}"
        ))
    
    return errors


def has_stop_errors(errors: List[ValidationError]) -> bool:
    """Проверить наличие критических ошибок STOP"""
    return any(e.level == "STOP" for e in errors)


def has_warn_errors(errors: List[ValidationError]) -> bool:
    """Проверить наличие предупреждений WARN"""
    return any(e.level == "WARN" for e in errors)
