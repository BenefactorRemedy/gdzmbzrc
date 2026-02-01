"""
Тесты критических ошибок (C1-C4)
"""
import pytest
from src.main import run_allocation


def test_c1_duplicate_order_ids():
    """
    C1: Дубликаты Order ID
    Должно быть STOP, распределение не выполняется
    """
    q1 = """ORD001|SKU-A|100|A|-
ORD001|SKU-B|50|B|-"""  # Дубликат ORD001
    q2 = """SKU-A|100
SKU-B|50"""
    
    report = run_allocation(q1, q2)
    
    assert report.status == "STOP"
    assert len(report.errors) >= 1
    
    # Найти ошибку C1
    c1_errors = [e for e in report.errors if e.code == "C1"]
    assert len(c1_errors) == 1
    assert c1_errors[0].level == "STOP"
    assert "ORD001" in c1_errors[0].details
    
    # Результаты не должны быть вычислены
    assert len(report.results) == 0
    assert not report.metrics


def test_c2_duplicate_stock_skus():
    """
    C2: Дубликаты SKU в остатках
    Должно быть STOP
    """
    q1 = "ORD001|SKU-A|100|A|-"
    q2 = """SKU-A|100
SKU-A|50"""  # Дубликат SKU-A
    
    report = run_allocation(q1, q2)
    
    assert report.status == "STOP"
    
    c2_errors = [e for e in report.errors if e.code == "C2"]
    assert len(c2_errors) == 1
    assert c2_errors[0].level == "STOP"
    assert "SKU-A" in c2_errors[0].details
    
    assert len(report.results) == 0


def test_c3_invalid_order_quantity():
    """
    C3: Количество в заказе <= 0
    Должно быть STOP
    """
    q1 = """ORD001|SKU-A|100|A|-
ORD002|SKU-A|0|A|-
ORD003|SKU-A|-5|B|-"""
    q2 = "SKU-A|200"
    
    report = run_allocation(q1, q2)
    
    assert report.status == "STOP"
    
    c3_errors = [e for e in report.errors if e.code == "C3"]
    assert len(c3_errors) == 1
    assert c3_errors[0].level == "STOP"
    # Должны быть упомянуты оба заказа с некорректным qty
    assert "ORD002" in c3_errors[0].details
    assert "ORD003" in c3_errors[0].details
    
    assert len(report.results) == 0


def test_c4_negative_stock_quantity():
    """
    C4: Количество в остатках < 0
    Должно быть STOP
    """
    q1 = "ORD001|SKU-A|100|A|-"
    q2 = """SKU-A|100
SKU-B|-50"""
    
    report = run_allocation(q1, q2)
    
    assert report.status == "STOP"
    
    c4_errors = [e for e in report.errors if e.code == "C4"]
    assert len(c4_errors) == 1
    assert c4_errors[0].level == "STOP"
    assert "SKU-B" in c4_errors[0].details
    
    assert len(report.results) == 0


def test_c5_multiple_stop_errors():
    """
    Тест с несколькими критическими ошибками одновременно
    """
    q1 = """ORD001|SKU-A|0|A|-
ORD001|SKU-B|50|B|-"""  # C1 + C3
    q2 = """SKU-A|-10
SKU-A|100"""  # C2 + C4
    
    report = run_allocation(q1, q2)
    
    assert report.status == "STOP"
    
    # Должно быть несколько STOP ошибок
    stop_errors = [e for e in report.errors if e.level == "STOP"]
    assert len(stop_errors) >= 2
    
    error_codes = [e.code for e in stop_errors]
    # Могут быть любые комбинации C1-C4
    assert any(code in ["C1", "C2", "C3", "C4"] for code in error_codes)
    
    # Распределение не выполнено
    assert len(report.results) == 0
