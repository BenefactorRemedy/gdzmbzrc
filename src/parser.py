"""
Парсинг входных данных из строковых ответов Q1-Q6
"""
import re
from datetime import datetime
from typing import List, Tuple
from src.models import Order, Stock, InputData


def parse_q1_orders(text: str) -> List[Order]:
    """
    Парсинг Q1: Список заказов
    Формат: ID | SKU | Qty | Class [| Due_Date]
    Пример: ORD001 | ITEM-A | 10 | A | 2024-12-31
    """
    orders = []
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 4:
            continue
            
        order_id = parts[0]
        sku = parts[1]
        qty = int(parts[2])
        priority_class = parts[3].upper()
        
        due_date = None
        if len(parts) >= 5 and parts[4]:
            try:
                due_date = datetime.strptime(parts[4], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        orders.append(Order(
            id=order_id,
            sku=sku,
            qty=qty,
            priority_class=priority_class,
            due_date=due_date
        ))
    
    return orders


def parse_q2_stock(text: str) -> List[Stock]:
    """
    Парсинг Q2: Складские остатки
    Формат: SKU | Qty
    Пример: ITEM-A | 100
    """
    stock_list = []
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 2:
            continue
            
        sku = parts[0]
        qty = int(parts[1])
        
        stock_list.append(Stock(sku=sku, qty=qty))
    
    return stock_list


def parse_q3_partial(text: str) -> bool:
    """
    Парсинг Q3: Разрешены ли частичные отгрузки?
    YES = True, NO = False
    """
    text = text.strip().upper()
    if 'YES' in text or 'ДА' in text:
        return True
    elif 'NO' in text or 'НЕТ' in text:
        return False
    else:
        # По умолчанию разрешаем частичные отгрузки
        return True


def parse_q4_reserved(text: str) -> List[Stock]:
    """
    Парсинг Q4: Зарезервированные остатки
    Формат: SKU | Qty
    Пример: ITEM-A | 20
    """
    return parse_q2_stock(text)  # Тот же формат что и Q2


def parse_q5_due_date(text: str) -> bool:
    """
    Парсинг Q5: Использовать ли Due Date для сортировки?
    YES = True (сортировка по дате), NO = False (FIFO)
    """
    text = text.strip().upper()
    if 'YES' in text or 'ДА' in text:
        return True
    elif 'NO' in text or 'НЕТ' in text:
        return False
    else:
        # По умолчанию FIFO
        return False


def parse_q6_service_mode(text: str) -> bool:
    """
    Парсинг Q6: Режим обслуживания при дефиците
    Service (Anti-zero) = True, Simplicity (FIFO) = False
    """
    text = text.strip().upper()
    if 'SERVICE' in text or 'СЕРВИС' in text or 'ANTI-ZERO' in text:
        return True
    elif 'SIMPLICITY' in text or 'ПРОСТОТА' in text or 'FIFO' in text:
        return False
    else:
        # По умолчанию Simplicity
        return False


def parse_input_data(q1: str, q2: str, q3: str, q4: str, q5: str, q6: str) -> InputData:
    """
    Парсинг всех входных данных из ответов на 6 вопросов
    """
    return InputData(
        orders=parse_q1_orders(q1),
        stock=parse_q2_stock(q2),
        partial_allowed=parse_q3_partial(q3),
        reserved_stock=parse_q4_reserved(q4),
        use_due_date=parse_q5_due_date(q5),
        service_mode=parse_q6_service_mode(q6)
    )
