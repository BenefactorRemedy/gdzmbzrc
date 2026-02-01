"""Юнит-тесты для модуля parser"""

import pytest
from datetime import date
from src.parser import (
    parse_date, parse_orders, parse_stock, parse_yes_no,
    parse_reserved, parse_input_data
)


class TestParseDate:
    """Тесты парсинга дат"""
    
    def test_parse_date_dd_mm_yyyy(self):
        """Парсинг формата DD.MM.YYYY"""
        result = parse_date("15.01.2026")
        assert result == date(2026, 1, 15)
    
    def test_parse_date_yyyy_mm_dd(self):
        """Парсинг формата YYYY-MM-DD"""
        result = parse_date("2026-01-15")
        assert result == date(2026, 1, 15)
    
    def test_parse_date_empty(self):
        """Пустая дата возвращает None"""
        assert parse_date("") is None
        assert parse_date("-") is None
        assert parse_date("НЕТ") is None
        assert parse_date("NO") is None


class TestParseOrders:
    """Тесты парсинга заказов"""
    
    def test_parse_single_order(self):
        """Парсинг одного заказа"""
        q1 = "ORD001|SKU-A|100|A|15.01.2026"
        orders = parse_orders(q1)
        
        assert len(orders) == 1
        assert orders[0].id == "ORD001"
        assert orders[0].sku == "SKU-A"
        assert orders[0].qty == 100
        assert orders[0].order_class == "A"
        assert orders[0].due_date == date(2026, 1, 15)
    
    def test_parse_multiple_orders(self):
        """Парсинг нескольких заказов"""
        q1 = """ORD001|SKU-A|100|A|15.01.2026
ORD002|SKU-B|50|B|-
ORD003|SKU-C|30|C|20.01.2026"""
        
        orders = parse_orders(q1)
        
        assert len(orders) == 3
        assert orders[1].id == "ORD002"
        assert orders[1].due_date is None
    
    def test_parse_orders_with_comments(self):
        """Игнорирование комментариев"""
        q1 = """# Это комментарий
ORD001|SKU-A|100|A|-
# Еще комментарий
ORD002|SKU-B|50|B|-"""
        
        orders = parse_orders(q1)
        assert len(orders) == 2


class TestParseStock:
    """Тесты парсинга запасов"""
    
    def test_parse_stock(self):
        """Парсинг запасов"""
        q2 = """SKU-A|150
SKU-B|200"""
        
        stock = parse_stock(q2)
        
        assert len(stock) == 2
        assert stock[0].sku == "SKU-A"
        assert stock[0].qty == 150


class TestParseYesNo:
    """Тесты парсинга YES/NO"""
    
    def test_parse_yes(self):
        """Различные варианты YES"""
        assert parse_yes_no("YES") is True
        assert parse_yes_no("yes") is True
        assert parse_yes_no("ДА") is True
        assert parse_yes_no("Y") is True
        assert parse_yes_no("1") is True
    
    def test_parse_no(self):
        """Различные варианты NO"""
        assert parse_yes_no("NO") is False
        assert parse_yes_no("no") is False
        assert parse_yes_no("НЕТ") is False
        assert parse_yes_no("N") is False


class TestParseReserved:
    """Тесты парсинга зарезервированных запасов"""
    
    def test_parse_reserved(self):
        """Парсинг зарезервированных запасов"""
        q4 = """SKU-A|20
SKU-B|30"""
        
        reserved = parse_reserved(q4)
        
        assert len(reserved) == 2
        assert reserved[0] == ("SKU-A", 20)
        assert reserved[1] == ("SKU-B", 30)
    
    def test_parse_no_reserved(self):
        """Парсинг NO - нет резервов"""
        assert parse_reserved("NO") == []
        assert parse_reserved("-") == []
