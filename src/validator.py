"""Модуль валидации входных данных - STOP и WARN логика"""

from typing import List, Tuple
from src.models import InputData, Order, Stock


class ValidationError(Exception):
    """Критическая ошибка валидации (STOP)"""
    pass


def validate_input_data(data: InputData) -> Tuple[List[str], List[str]]:
    """
    Валидация входных данных
    
    Returns:
        (errors, warnings) - списки ошибок и предупреждений
        
    STOP условия (критические ошибки):
    - C1: Дубликаты ID заказов
    - C2: Дубликаты SKU в запасах
    - C3: QTY заказа <= 0
    - C4: QTY запаса < 0
    
    WARN условия (предупреждения):
    - B1: SKU заказа нет в запасах
    - B2: Зарезервированное количество > доступного запаса
    - B3: Заказ класса C (низкий приоритет)
    """
    errors = []
    warnings = []
    
    # C1: Проверка дубликатов ID заказов
    order_ids = [o.id for o in data.orders]
    duplicate_ids = [oid for oid in set(order_ids) if order_ids.count(oid) > 1]
    if duplicate_ids:
        errors.append(f"STOP C1: Дубликаты ID заказов: {', '.join(duplicate_ids)}")
    
    # C2: Проверка дубликатов SKU в запасах
    stock_skus = [s.sku for s in data.stock]
    duplicate_skus = [sku for sku in set(stock_skus) if stock_skus.count(sku) > 1]
    if duplicate_skus:
        errors.append(f"STOP C2: Дубликаты SKU в запасах: {', '.join(duplicate_skus)}")
    
    # C3: Проверка QTY заказов
    for order in data.orders:
        if order.qty <= 0:
            errors.append(f"STOP C3: Заказ {order.id} имеет недопустимое количество: {order.qty}")
    
    # C4: Проверка QTY запасов
    for stock in data.stock:
        if stock.qty < 0:
            errors.append(f"STOP C4: SKU {stock.sku} имеет отрицательный запас: {stock.qty}")
    
    # Если есть критические ошибки, возвращаем только их
    if errors:
        return errors, warnings
    
    # B1: Проверка наличия SKU в запасах
    stock_sku_set = set(s.sku for s in data.stock)
    for order in data.orders:
        if order.sku not in stock_sku_set:
            warnings.append(f"WARN B1: SKU {order.sku} заказа {order.id} отсутствует в запасах")
    
    # B2: Проверка зарезервированных количеств
    stock_dict = {s.sku: s.qty for s in data.stock}
    for sku, reserved_qty in data.q4_reserved:
        stock_qty = stock_dict.get(sku, 0)
        if reserved_qty > stock_qty:
            warnings.append(
                f"WARN B2: Зарезервировано {reserved_qty} для SKU {sku}, "
                f"но в наличии только {stock_qty}"
            )
    
    # B3: Предупреждение о заказах класса C
    class_c_orders = [o.id for o in data.orders if o.order_class == 'C']
    if class_c_orders:
        warnings.append(
            f"WARN B3: Заказы класса C (низкий приоритет): {', '.join(class_c_orders)}"
        )
    
    return errors, warnings


def check_critical_errors(data: InputData) -> None:
    """
    Проверка критических ошибок. Выбрасывает ValidationError если найдены.
    """
    errors, _ = validate_input_data(data)
    
    if errors:
        error_msg = "\n".join(errors)
        raise ValidationError(f"Обнаружены критические ошибки:\n{error_msg}")
