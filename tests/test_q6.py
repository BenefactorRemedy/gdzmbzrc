"""
Тесты Q6: Service mode (анти-ноль) vs Simplicity
"""
import pytest
from src.main import run_allocation


def test_q6_service_mode_prevents_zeros():
    """
    Service mode (Q6=YES): При дефиците сначала по 1 каждому
    """
    q1 = """ORD001|SKU-A|50|A|-
ORD002|SKU-A|50|A|-
ORD003|SKU-A|50|A|-"""
    q2 = "SKU-A|80"  # Дефицит: 80 < 150
    q3 = "YES"
    q6 = "YES"  # Service mode
    
    report = run_allocation(q1, q2, q3, q6=q6)
    
    assert report.status == "SUCCESS"
    result_map = {r.order_id: r for r in report.results}
    
    # Анти-ноль: сначала по 1 каждому (3 шт), остаток 77
    # ORD001: 1 + 49 = 50 (полный запрос), остаток 28
    # ORD002: 1 + 27 = 28, остаток 0
    # ORD003: 1 + 0 = 1 (не ноль!)
    assert result_map["ORD001"].allocated == 50
    # ORD002 получает оставшееся: 1 (anti-zero) + 27 (FIFO) = 28
    # но фактически есть 28 доступных, так что получает все
    assert result_map["ORD002"].allocated >= 27  # At least 27
    assert result_map["ORD003"].allocated > 0  # Не ноль благодаря анти-ноль


def test_q6_simplicity_mode_allows_zeros():
    """
    Simplicity mode (Q6=NO): FIFO без анти-ноль
    """
    q1 = """ORD001|SKU-A|50|A|-
ORD002|SKU-A|50|A|-
ORD003|SKU-A|50|A|-"""
    q2 = "SKU-A|80"  # Дефицит
    q3 = "YES"
    q6 = "NO"  # Simplicity mode
    
    report = run_allocation(q1, q2, q3, q6=q6)
    
    assert report.status == "SUCCESS"
    result_map = {r.order_id: r for r in report.results}
    
    # FIFO: первый получает все 50, второй - 30, третий - 0
    assert result_map["ORD001"].allocated == 50
    assert result_map["ORD002"].allocated == 30
    assert result_map["ORD003"].allocated == 0  # Ноль в простом режиме


def test_q6_service_mode_no_deficit():
    """
    Service mode при отсутствии дефицита
    Должен работать как обычно
    """
    q1 = """ORD001|SKU-A|50|A|-
ORD002|SKU-A|50|A|-"""
    q2 = "SKU-A|200"  # Достаточно запасов
    q6 = "YES"
    
    report = run_allocation(q1, q2, q6=q6)
    
    assert report.status == "SUCCESS"
    result_map = {r.order_id: r for r in report.results}
    
    # Нет дефицита - распределение нормальное
    assert result_map["ORD001"].allocated == 50
    assert result_map["ORD002"].allocated == 50


def test_q6_service_mode_single_order():
    """
    Service mode при одном заказе
    Анти-ноль не должен влиять (нет конкуренции)
    """
    q1 = "ORD001|SKU-A|100|A|-"
    q2 = "SKU-A|50"  # Дефицит, но только один заказ
    q6 = "YES"
    
    report = run_allocation(q1, q2, q6=q6)
    
    assert report.status == "SUCCESS"
    # Один заказ - нет конкуренции, анти-ноль не применяется
    # Получает все доступное
    assert report.results[0].allocated == 50


def test_q6_service_mode_multiple_skus():
    """
    Service mode с несколькими SKU
    Анти-ноль применяется отдельно к каждому SKU
    """
    q1 = """ORD001|SKU-A|50|A|-
ORD002|SKU-A|50|A|-
ORD003|SKU-B|40|A|-
ORD004|SKU-B|40|A|-"""
    q2 = """SKU-A|60
SKU-B|50"""
    q6 = "YES"
    
    report = run_allocation(q1, q2, q6=q6)
    
    assert report.status == "SUCCESS"
    result_map = {r.order_id: r for r in report.results}
    
    # SKU-A: дефицит (60 < 100), анти-ноль
    # ORD001, ORD002 оба получают > 0
    assert result_map["ORD001"].allocated > 0
    assert result_map["ORD002"].allocated > 0
    
    # SKU-B: дефицит (50 < 80), анти-ноль
    # ORD003, ORD004 оба получают > 0
    assert result_map["ORD003"].allocated > 0
    assert result_map["ORD004"].allocated > 0


def test_q6_service_mode_with_priorities():
    """
    Service mode с разными приоритетами
    Анти-ноль применяется внутри каждого приоритета
    """
    q1 = """ORD001|SKU-A|100|A|-
ORD002|SKU-A|100|A|-
ORD003|SKU-A|50|B|-
ORD004|SKU-A|50|B|-"""
    q2 = "SKU-A|250"  # Дефицит общий: 250 < 300
    q6 = "YES"
    
    report = run_allocation(q1, q2, q6=q6)
    
    assert report.status == "SUCCESS"
    result_map = {r.order_id: r for r in report.results}
    
    # Приоритет A идет первым
    # После A останется мало для B, но анти-ноль должен помочь
    # Все заказы должны получить > 0
    for order_id in ["ORD001", "ORD002", "ORD003", "ORD004"]:
        assert result_map[order_id].allocated > 0, f"{order_id} получил 0"
