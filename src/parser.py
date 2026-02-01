"""
Парсинг входных данных Q1-Q6
"""
from datetime import datetime
from typing import List, Optional
from src.models import Order, Stock, InputData


def parse_q1(text: str) -> List[Order]:
    """
    Q1: Парсинг заказов
    Формат: OrderID|SKU|Qty|Class|DueDate
    Пример: ORD001|SKU-A|100|A|2026-02-15
    """
    orders = []
    if not text or text.strip() == "-":
        return orders
    
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or line == "-":
            continue
            
        parts = line.split('|')
        if len(parts) < 4:
            continue
            
        order_id = parts[0].strip()
        sku = parts[1].strip()
        
        try:
            qty = int(parts[2].strip())
        except ValueError:
            qty = 0
            
        priority_class = parts[3].strip().upper()
        
        # Дата может отсутствовать или быть "-"
        due_date = None
        if len(parts) > 4 and parts[4].strip() and parts[4].strip() != "-":
            try:
                due_date = datetime.strptime(parts[4].strip(), "%Y-%m-%d").date()
            except ValueError:
                pass
        
        orders.append(Order(
            order_id=order_id,
            sku=sku,
            qty=qty,
            priority_class=priority_class,
            due_date=due_date
        ))
    
    return orders


def parse_q2(text: str) -> List[Stock]:
    """
    Q2: Парсинг остатков
    Формат: SKU|Qty
    Пример: SKU-A|500
    """
    stock_list = []
    if not text or text.strip() == "-":
        return stock_list
    
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or line == "-":
            continue
            
        parts = line.split('|')
        if len(parts) < 2:
            continue
            
        sku = parts[0].strip()
        try:
            qty = int(parts[1].strip())
        except ValueError:
            qty = 0
            
        stock_list.append(Stock(sku=sku, qty=qty))
    
    return stock_list


def parse_q3(text: str) -> bool:
    """
    Q3: Разрешена ли частичная отгрузка?
    YES = True (частичная), NO = False (все или ничего)
    """
    text = text.strip().upper()
    return text == "YES" or text == "ДА"


def parse_q4(text: str) -> List[Stock]:
    """
    Q4: Парсинг резервов
    Формат: SKU|Reserved
    Пример: SKU-A|50
    """
    reserved_list = []
    if not text or text.strip() == "-":
        return reserved_list
    
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or line == "-":
            continue
            
        parts = line.split('|')
        if len(parts) < 2:
            continue
            
        sku = parts[0].strip()
        try:
            reserved = int(parts[1].strip())
        except ValueError:
            reserved = 0
            
        reserved_list.append(Stock(sku=sku, qty=0, reserved=reserved))
    
    return reserved_list


def parse_q5(text: str) -> bool:
    """
    Q5: Сортировать ли по дате?
    YES = True (сортировка по due_date), NO = False (FIFO)
    """
    text = text.strip().upper()
    return text == "YES" or text == "ДА"


def parse_q6(text: str) -> bool:
    """
    Q6: Режим "Сервис" (анти-ноль)?
    YES = True (сервис, анти-ноль), NO = False (простота)
    """
    text = text.strip().upper()
    return text == "YES" or text == "ДА"


def parse_input_data(q1: str, q2: str, q3: str = "YES", q4: str = "-", 
                     q5: str = "NO", q6: str = "NO") -> InputData:
    """
    Парсинг всех входных данных Q1-Q6
    """
    orders = parse_q1(q1)
    stock = parse_q2(q2)
    allow_partial = parse_q3(q3)
    reserved_stock = parse_q4(q4)
    sort_by_due_date = parse_q5(q5)
    service_mode = parse_q6(q6)
    
    # Применить резервы к остаткам
    for reserved in reserved_stock:
        stock_item = None
        for s in stock:
            if s.sku == reserved.sku:
                stock_item = s
                break
        
        if stock_item:
            stock_item.reserved = reserved.reserved
    
    return InputData(
        orders=orders,
        stock=stock,
        allow_partial=allow_partial,
        reserved_stock=reserved_stock,
        sort_by_due_date=sort_by_due_date,
        service_mode=service_mode
    )
