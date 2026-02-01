"""
Тесты для парсера
"""
import pytest
from datetime import date
from src.parser import (
    parse_q1_orders, parse_q2_stock, parse_q3_partial,
    parse_q4_reserved, parse_q5_due_date, parse_q6_service_mode
)


class TestQ1Parser:
    """Тесты парсинга Q1 (заказы)"""
    
    def test_parse_basic_orders(self):
        """Парсинг базовых заказов"""
        text = """
        O1 | ITEM-A | 10 | A
        O2 | ITEM-B | 20 | B
        """
        orders = parse_q1_orders(text)
        
        assert len(orders) == 2
        assert orders[0].id == 'O1'
        assert orders[0].sku == 'ITEM-A'
        assert orders[0].qty == 10
        assert orders[0].priority_class == 'A'
    
    def test_parse_orders_with_due_date(self):
        """Парсинг заказов с Due Date"""
        text = "O1 | ITEM-A | 10 | A | 2024-12-31"
        orders = parse_q1_orders(text)
        
        assert len(orders) == 1
        assert orders[0].due_date == date(2024, 12, 31)
    
    def test_ignore_comments(self):
        """Игнорирование комментариев"""
        text = """
        # Это комментарий
        O1 | ITEM-A | 10 | A
        """
        orders = parse_q1_orders(text)
        
        assert len(orders) == 1


class TestQ2Parser:
    """Тесты парсинга Q2 (остатки)"""
    
    def test_parse_stock(self):
        """Парсинг остатков"""
        text = """
        ITEM-A | 100
        ITEM-B | 50
        """
        stock = parse_q2_stock(text)
        
        assert len(stock) == 2
        assert stock[0].sku == 'ITEM-A'
        assert stock[0].qty == 100


class TestQ3Parser:
    """Тесты парсинга Q3 (частичные отгрузки)"""
    
    def test_parse_yes(self):
        """Парсинг YES"""
        assert parse_q3_partial("YES") == True
        assert parse_q3_partial("yes") == True
        assert parse_q3_partial("ДА") == True
    
    def test_parse_no(self):
        """Парсинг NO"""
        assert parse_q3_partial("NO") == False
        assert parse_q3_partial("no") == False
        assert parse_q3_partial("НЕТ") == False


class TestQ5Parser:
    """Тесты парсинга Q5 (Due Date)"""
    
    def test_parse_yes(self):
        """Парсинг YES"""
        assert parse_q5_due_date("YES") == True
    
    def test_parse_no(self):
        """Парсинг NO"""
        assert parse_q5_due_date("NO") == False


class TestQ6Parser:
    """Тесты парсинга Q6 (режим обслуживания)"""
    
    def test_parse_service(self):
        """Парсинг Service"""
        assert parse_q6_service_mode("Service") == True
        assert parse_q6_service_mode("SERVICE") == True
        assert parse_q6_service_mode("Anti-zero") == True
    
    def test_parse_simplicity(self):
        """Парсинг Simplicity"""
        assert parse_q6_service_mode("Simplicity") == False
        assert parse_q6_service_mode("SIMPLICITY") == False
        assert parse_q6_service_mode("FIFO") == False
