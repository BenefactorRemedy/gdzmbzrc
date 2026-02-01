"""
Тесты нормальных сценариев (A1-A4)
"""
import pytest
from src.main import run_allocation


def test_a1_normal_case():
    """
    A1: Нормальный случай без Q6
    Приоритеты работают корректно: A → B → C
    """
    q1 = """ORD001|SKU-A|50|B|-
ORD002|SKU-A|30|A|-
ORD003|SKU-A|20|C|-"""
    q2 = "SKU-A|70"
    q3 = "YES"
    q4 = "-"
    q5 = "NO"
    q6 = "NO"
    
    report = run_allocation(q1, q2, q3, q4, q5, q6)
    
    assert report.status == "SUCCESS"
    assert len(report.results) == 3
    
    # Проверка распределения по приоритетам
    result_map = {r.order_id: r for r in report.results}
    
    # A получает 30 (весь запрос)
    assert result_map["ORD002"].allocated == 30
    assert result_map["ORD002"].priority_class == "A"
    
    # B получает 40 из 50 (остаток после A)
    assert result_map["ORD001"].allocated == 40
    assert result_map["ORD001"].priority_class == "B"
    
    # C получает 0 (ничего не осталось)
    assert result_map["ORD003"].allocated == 0
    assert result_map["ORD003"].priority_class == "C"


def test_a2_simplicity_mode():
    """
    A2: Q6 Simplicity (FIFO)
    Без анти-ноль логики
    """
    q1 = """ORD001|SKU-A|100|A|-
ORD002|SKU-A|80|A|-"""
    q2 = "SKU-A|120"
    q3 = "YES"
    q4 = "-"
    q5 = "NO"
    q6 = "NO"  # Простота - FIFO
    
    report = run_allocation(q1, q2, q3, q4, q5, q6)
    
    assert report.status == "SUCCESS"
    result_map = {r.order_id: r for r in report.results}
    
    # FIFO: первый заказ получает все что просил
    assert result_map["ORD001"].allocated == 100
    # Второй получает остаток
    assert result_map["ORD002"].allocated == 20


def test_a3_service_mode_anti_zero():
    """
    A3: Q6 Service (Anti-zero)
    При дефиците сначала по 1 каждому, потом остаток по FIFO
    """
    q1 = """ORD001|SKU-A|100|A|-
ORD002|SKU-A|80|A|-"""
    q2 = "SKU-A|120"
    q3 = "YES"
    q4 = "-"
    q5 = "NO"
    q6 = "YES"  # Сервис - анти-ноль
    
    report = run_allocation(q1, q2, q3, q4, q5, q6)
    
    assert report.status == "SUCCESS"
    result_map = {r.order_id: r for r in report.results}
    
    # Анти-ноль: сначала по 1 каждому (2 шт), остается 118
    # ORD001 получает 1 + 99 = 100 (полный запрос)
    assert result_map["ORD001"].allocated == 100
    # ORD002 получает 1 + 19 = 20
    assert result_map["ORD002"].allocated == 20


def test_a4_all_or_nothing():
    """
    A4: All-or-nothing (Q3=NO)
    Либо весь заказ, либо ничего
    """
    q1 = """ORD001|SKU-A|100|A|-
ORD002|SKU-A|80|A|-"""
    q2 = "SKU-A|120"
    q3 = "NO"  # Все или ничего
    q4 = "-"
    q5 = "NO"
    q6 = "NO"
    
    report = run_allocation(q1, q2, q3, q4, q5, q6)
    
    assert report.status == "SUCCESS"
    result_map = {r.order_id: r for r in report.results}
    
    # ORD001 получает все 100 (хватает)
    assert result_map["ORD001"].allocated == 100
    # ORD002 не получает ничего (остаток 20 < 80)
    assert result_map["ORD002"].allocated == 0


def test_a5_reserved_stock():
    """
    Тест с резервами (Q4)
    available = stock - reserved
    """
    q1 = "ORD001|SKU-A|100|A|-"
    q2 = "SKU-A|150"
    q3 = "YES"
    q4 = "SKU-A|50"  # Резерв 50
    q5 = "NO"
    q6 = "NO"
    
    report = run_allocation(q1, q2, q3, q4, q5, q6)
    
    assert report.status == "SUCCESS"
    result_map = {r.order_id: r for r in report.results}
    
    # Доступно: 150 - 50 = 100
    assert result_map["ORD001"].allocated == 100


def test_a6_due_date_sorting():
    """
    Тест сортировки по дате (Q5=YES)
    """
    q1 = """ORD001|SKU-A|50|A|2026-03-01
ORD002|SKU-A|50|A|2026-02-15
ORD003|SKU-A|50|A|2026-02-20"""
    q2 = "SKU-A|100"
    q3 = "YES"
    q4 = "-"
    q5 = "YES"  # Сортировка по дате
    q6 = "NO"
    
    report = run_allocation(q1, q2, q3, q4, q5, q6)
    
    assert report.status == "SUCCESS"
    result_map = {r.order_id: r for r in report.results}
    
    # ORD002 (2026-02-15) - самая ранняя дата, получает 50
    assert result_map["ORD002"].allocated == 50
    # ORD003 (2026-02-20) - следующая, получает 50
    assert result_map["ORD003"].allocated == 50
    # ORD001 (2026-03-01) - последняя, получает 0
    assert result_map["ORD001"].allocated == 0


def test_a7_metrics_green():
    """
    Тест метрик: GREEN статус
    Fill Rate >= 90% и zero_count = 0
    """
    q1 = """ORD001|SKU-A|50|A|-
ORD002|SKU-A|50|A|-"""
    q2 = "SKU-A|100"
    
    report = run_allocation(q1, q2)
    
    assert report.status == "SUCCESS"
    assert report.metrics["fill_rate"] == 100.0
    assert report.metrics["zero_count"] == 0
    assert report.metrics["risk_level"] == "GREEN"


def test_a8_metrics_yellow():
    """
    Тест метрик: YELLOW статус
    Fill Rate между 70-90%
    """
    q1 = """ORD001|SKU-A|100|A|-
ORD002|SKU-A|100|A|-"""
    q2 = "SKU-A|150"
    
    report = run_allocation(q1, q2)
    
    assert report.status == "SUCCESS"
    assert report.metrics["fill_rate"] == 75.0
    assert report.metrics["risk_level"] == "YELLOW"


def test_a9_metrics_red():
    """
    Тест метрик: RED статус
    Fill Rate < 70%
    """
    q1 = """ORD001|SKU-A|100|A|-
ORD002|SKU-A|100|A|-"""
    q2 = "SKU-A|100"
    
    report = run_allocation(q1, q2)
    
    assert report.status == "SUCCESS"
    assert report.metrics["fill_rate"] == 50.0
    assert report.metrics["risk_level"] == "RED"
