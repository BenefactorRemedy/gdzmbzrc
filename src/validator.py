"""
Валидация входных данных - STOP (критические ошибки) и WARN (предупреждения)
"""
from typing import List, Tuple
from src.models import InputData, Order, Stock


class ValidationError(Exception):
    """Критическая ошибка валидации (STOP)"""
    pass


def validate_input_data(data: InputData) -> Tuple[List[str], List[str]]:
    """
    Валидация входных данных
    Возвращает: (errors, warnings)
    - errors: список критических ошибок (STOP)
    - warnings: список предупреждений (WARN)
    """
    errors = []
    warnings = []
    
    # STOP: Проверка дублей в заказах
    order_ids = [order.id for order in data.orders]
    duplicates = [oid for oid in order_ids if order_ids.count(oid) > 1]
    if duplicates:
        unique_duplicates = list(set(duplicates))
        errors.append(f"STOP: Найдены дублирующиеся ID заказов: {', '.join(unique_duplicates)}")
    
    # STOP: Проверка qty <= 0 в заказах
    for order in data.orders:
        if order.qty <= 0:
            errors.append(f"STOP: Заказ {order.id} имеет недопустимое количество: {order.qty}")
    
    # STOP: Проверка qty < 0 в остатках
    for stock in data.stock:
        if stock.qty < 0:
            errors.append(f"STOP: SKU {stock.sku} имеет отрицательный остаток: {stock.qty}")
    
    # STOP: Проверка qty < 0 в резервах
    for reserved in data.reserved_stock:
        if reserved.qty < 0:
            errors.append(f"STOP: SKU {reserved.sku} имеет отрицательный резерв: {reserved.qty}")
    
    # STOP: Проверка дублей в остатках
    stock_skus = [stock.sku for stock in data.stock]
    stock_duplicates = [sku for sku in stock_skus if stock_skus.count(sku) > 1]
    if stock_duplicates:
        unique_stock_dups = list(set(stock_duplicates))
        errors.append(f"STOP: Найдены дублирующиеся SKU в остатках: {', '.join(unique_stock_dups)}")
    
    # WARN: SKU заказа отсутствует в остатках
    stock_sku_set = set(stock.sku for stock in data.stock)
    for order in data.orders:
        if order.sku not in stock_sku_set:
            warnings.append(f"WARN: SKU '{order.sku}' из заказа {order.id} отсутствует в остатках")
    
    # WARN: Резерв превышает остаток
    stock_dict = {stock.sku: stock.qty for stock in data.stock}
    for reserved in data.reserved_stock:
        available = stock_dict.get(reserved.sku, 0)
        if reserved.qty > available:
            warnings.append(
                f"WARN: Резерв SKU '{reserved.sku}' ({reserved.qty}) превышает остаток ({available})"
            )
    
    return errors, warnings


def check_stop_conditions(data: InputData) -> None:
    """
    Проверка критических ошибок, выбрасывает ValidationError если найдены
    """
    errors, _ = validate_input_data(data)
    if errors:
        raise ValidationError('\n'.join(errors))
