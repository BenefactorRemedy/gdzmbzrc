#!/usr/bin/env python
"""
Пример использования SC-PRIORITY-DEMO-LITE

Запуск: python examples.py
"""

from src.main import run_allocation
from src.formatter import format_report

def example_1_basic():
    """Пример 1: Базовое распределение по приоритетам"""
    print("=" * 70)
    print("ПРИМЕР 1: Базовое распределение по приоритетам A -> B")
    print("=" * 70)
    
    q1 = """ORD001|SKU-A|100|A|15.01.2026
ORD002|SKU-A|50|B|-"""
    
    q2 = "SKU-A|150"
    q3 = "YES"  # Partial allocation
    q4 = "NO"   # Нет резервов
    q5 = "NO"   # FIFO
    q6 = "NO"   # Simplicity
    
    report = run_allocation(q1, q2, q3, q4, q5, q6)
    print(format_report(report))
    print()


def example_2_service_mode():
    """Пример 2: Service Mode - Anti-zero логика"""
    print("=" * 70)
    print("ПРИМЕР 2: Service Mode - Anti-zero логика")
    print("=" * 70)
    
    q1 = """ORD001|SKU-A|100|A|-
ORD002|SKU-A|80|A|-"""
    
    q2 = "SKU-A|120"
    q3 = "YES"
    q4 = "NO"
    q5 = "NO"
    q6 = "YES"  # Service mode (Anti-zero)
    
    report = run_allocation(q1, q2, q3, q4, q5, q6)
    print(format_report(report))
    print()


def example_3_all_or_nothing():
    """Пример 3: All-or-nothing режим"""
    print("=" * 70)
    print("ПРИМЕР 3: All-or-nothing режим")
    print("=" * 70)
    
    q1 = """ORD001|SKU-A|80|A|-
ORD002|SKU-A|50|A|-"""
    
    q2 = "SKU-A|100"
    q3 = "NO"  # All-or-nothing
    q4 = "NO"
    q5 = "NO"
    q6 = "NO"
    
    report = run_allocation(q1, q2, q3, q4, q5, q6)
    print(format_report(report))
    print()


def example_4_reserved_stock():
    """Пример 4: Зарезервированные запасы"""
    print("=" * 70)
    print("ПРИМЕР 4: Зарезервированные запасы")
    print("=" * 70)
    
    q1 = "ORD001|SKU-A|100|A|-"
    q2 = "SKU-A|150"
    q3 = "YES"
    q4 = "SKU-A|50"  # 50 зарезервировано
    q5 = "NO"
    q6 = "NO"
    
    report = run_allocation(q1, q2, q3, q4, q5, q6)
    print(format_report(report))
    print()


def example_5_error_stop():
    """Пример 5: STOP - критическая ошибка"""
    print("=" * 70)
    print("ПРИМЕР 5: STOP - критическая ошибка (дубликаты ID)")
    print("=" * 70)
    
    q1 = """ORD001|SKU-A|100|A|-
ORD001|SKU-B|50|B|-"""  # Дубликат ID
    
    q2 = "SKU-A|100"
    q3 = "YES"
    q4 = "NO"
    q5 = "NO"
    q6 = "NO"
    
    report = run_allocation(q1, q2, q3, q4, q5, q6)
    print(format_report(report))
    print()


if __name__ == "__main__":
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "SC-PRIORITY-DEMO-LITE RU v2.2 - Примеры" + " " * 18 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    example_1_basic()
    example_2_service_mode()
    example_3_all_or_nothing()
    example_4_reserved_stock()
    example_5_error_stop()
    
    print("=" * 70)
    print("Все примеры выполнены!")
    print("=" * 70)
