"""
Тесты сценариев с предупреждениями (B1-B3)
"""
import pytest
from src.main import run_allocation


def test_b1_missing_sku():
    """
    B1: SKU в заказах отсутствует в остатках
    Должно быть WARN, но распределение выполняется
    """
    q1 = """ORD001|SKU-A|100|A|-
ORD002|SKU-B|50|A|-"""
    q2 = "SKU-A|100"  # SKU-B отсутствует
    
    report = run_allocation(q1, q2)
    
    assert report.status == "WARN"
    assert len(report.errors) == 1
    assert report.errors[0].level == "WARN"
    assert report.errors[0].code == "B1"
    assert "SKU-B" in report.errors[0].details
    
    # Распределение все равно выполнено
    assert len(report.results) == 2
    result_map = {r.order_id: r for r in report.results}
    assert result_map["ORD001"].allocated == 100
    assert result_map["ORD002"].allocated == 0  # SKU отсутствует


def test_b2_reserved_exceeds_stock():
    """
    B2: Резерв превышает остаток
    Должно быть WARN, но распределение выполняется
    """
    q1 = "ORD001|SKU-A|50|A|-"
    q2 = "SKU-A|100"
    q4 = "SKU-A|150"  # Резерв больше остатка
    
    report = run_allocation(q1, q2, q4=q4)
    
    assert report.status == "WARN"
    assert len(report.errors) == 1
    assert report.errors[0].level == "WARN"
    assert report.errors[0].code == "B2"
    
    # Распределение выполнено, но available = 0 (100 - 150 = 0)
    assert len(report.results) == 1
    assert report.results[0].allocated == 0


def test_b3_class_c_orders():
    """
    B3: Есть заказы класса C (низкий приоритет)
    Должно быть WARN
    """
    q1 = """ORD001|SKU-A|50|A|-
ORD002|SKU-A|30|C|-"""
    q2 = "SKU-A|100"
    
    report = run_allocation(q1, q2)
    
    assert report.status == "WARN"
    assert len(report.errors) == 1
    assert report.errors[0].level == "WARN"
    assert report.errors[0].code == "B3"
    assert "ORD002" in report.errors[0].details
    
    # Распределение выполнено
    assert len(report.results) == 2


def test_b4_multiple_warnings():
    """
    Тест с несколькими предупреждениями одновременно
    """
    q1 = """ORD001|SKU-A|50|A|-
ORD002|SKU-B|30|C|-"""
    q2 = "SKU-A|100"
    q4 = "SKU-A|150"
    
    report = run_allocation(q1, q2, q4=q4)
    
    assert report.status == "WARN"
    # Должно быть 3 предупреждения: B1 (SKU-B), B2 (резерв), B3 (класс C)
    assert len(report.errors) == 3
    
    error_codes = [e.code for e in report.errors]
    assert "B1" in error_codes
    assert "B2" in error_codes
    assert "B3" in error_codes
