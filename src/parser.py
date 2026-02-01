"""Парсер входных данных из строковых ответов Q1-Q6"""

from datetime import datetime, date
from typing import List, Optional, Tuple
from src.models import Order, Stock, InputData


def parse_date(date_str: str) -> Optional[date]:
    """Парсинг даты в формате DD.MM.YYYY или YYYY-MM-DD"""
    if not date_str or date_str.strip().upper() in ["НЕТ", "NO", "NONE", "-", ""]:
        return None
    
    date_str = date_str.strip()
    
    # Попробуем разные форматы
    formats = ["%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


def parse_orders(q1_response: str) -> List[Order]:
    """
    Парсинг Q1: Список заказов
    Формат: ID|SKU|QTY|CLASS|DUE_DATE (по одному на строку)
    Пример:
    ORD001|SKU-A|100|A|15.01.2026
    ORD002|SKU-B|50|B|-
    """
    orders = []
    
    for line in q1_response.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 4:
            continue
        
        order_id = parts[0]
        sku = parts[1]
        try:
            qty = int(parts[2])
        except ValueError:
            continue
        
        order_class = parts[3].upper()
        due_date = parse_date(parts[4]) if len(parts) > 4 else None
        
        orders.append(Order(
            id=order_id,
            sku=sku,
            qty=qty,
            order_class=order_class,
            due_date=due_date
        ))
    
    return orders


def parse_stock(q2_response: str) -> List[Stock]:
    """
    Парсинг Q2: Список запасов
    Формат: SKU|QTY (по одному на строку)
    Пример:
    SKU-A|150
    SKU-B|30
    """
    stock_list = []
    
    for line in q2_response.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 2:
            continue
        
        sku = parts[0]
        try:
            qty = int(parts[1])
        except ValueError:
            continue
        
        stock_list.append(Stock(sku=sku, qty=qty))
    
    return stock_list


def parse_yes_no(response: str) -> bool:
    """Парсинг YES/NO ответа"""
    response = response.strip().upper()
    return response in ["YES", "ДА", "Y", "TRUE", "1"]


def parse_reserved(q4_response: str) -> List[Tuple[str, int]]:
    """
    Парсинг Q4: Зарезервированные количества
    Формат: SKU|RESERVED_QTY (по одному на строку)
    Пример:
    SKU-A|20
    SKU-C|10
    Или просто "NO" / "-" если нет резервов
    """
    if q4_response.strip().upper() in ["NO", "НЕТ", "-", "NONE", ""]:
        return []
    
    reserved = []
    
    for line in q4_response.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 2:
            continue
        
        sku = parts[0]
        try:
            qty = int(parts[1])
        except ValueError:
            continue
        
        reserved.append((sku, qty))
    
    return reserved


def parse_input_data(q1: str, q2: str, q3: str, q4: str, q5: str, q6: str) -> InputData:
    """
    Парсинг всех входных данных Q1-Q6
    
    Q1: Список заказов
    Q2: Список запасов
    Q3: Partial allocation? YES/NO
    Q4: Зарезервированные количества
    Q5: Sort by due date? YES/NO
    Q6: Service mode (Anti-zero)? YES/NO
    """
    orders = parse_orders(q1)
    stock = parse_stock(q2)
    q3_partial = parse_yes_no(q3)
    reserved = parse_reserved(q4)
    q5_use_due_date = parse_yes_no(q5)
    q6_service_mode = parse_yes_no(q6)
    
    return InputData(
        orders=orders,
        stock=stock,
        q3_partial=q3_partial,
        q4_reserved=reserved,
        q5_use_due_date=q5_use_due_date,
        q6_service_mode=q6_service_mode
    )
