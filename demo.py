#!/usr/bin/env python
"""
Демонстрация возможностей SC-PRIORITY-DEMO-LITE RU v2.2
"""
import os
import sys

# Добавляем путь к src для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models import Order, Stock, InputData, AllocationReport
from src.allocator import Allocator
from src.validator import validate_input_data
from src.metrics import calculate_all_metrics
from src.formatter import format_report


def demo_scenario(name: str, description: str, data: InputData):
    """
    Демонстрация одного сценария
    """
    print("\n" + "=" * 80)
    print(f"🔹 {name}")
    print(f"📝 {description}")
    print("=" * 80)
    
    # Валидация
    errors, warnings = validate_input_data(data)
    
    if errors:
        report = AllocationReport(
            results=[],
            warnings=warnings,
            errors=errors,
            fill_rate=0.0,
            count_zero=0,
            risk_level='Red',
            input_data=data
        )
        print("\n❌ КРИТИЧЕСКИЕ ОШИБКИ:\n")
        for error in errors:
            print(f"  {error}")
        return
    
    # Распределение
    allocator = Allocator(data)
    results = allocator.allocate()
    
    # Метрики
    metrics = calculate_all_metrics(results)
    
    # Отчет
    report = AllocationReport(
        results=results,
        warnings=warnings,
        errors=[],
        fill_rate=metrics['fill_rate'],
        count_zero=metrics['count_zero'],
        risk_level=metrics['risk_level'],
        input_data=data
    )
    
    # Вывод результатов
    markdown = format_report(report)
    print(markdown)


def main():
    """
    Главная функция демонстрации
    """
    print("\n" + "=" * 80)
    print(" SC-PRIORITY-DEMO-LITE RU v2.2 - Демонстрация")
    print("=" * 80)
    
    # Сценарий A1: Базовое распределение с приоритетами
    demo_scenario(
        "Сценарий A1: Базовое распределение с приоритетами",
        "Приоритет A получает товары первым, затем B, затем C",
        InputData(
            orders=[
                Order(id='ORD001', sku='ITEM-A', qty=50, priority_class='B'),
                Order(id='ORD002', sku='ITEM-A', qty=30, priority_class='A'),
                Order(id='ORD003', sku='ITEM-A', qty=20, priority_class='C'),
            ],
            stock=[Stock(sku='ITEM-A', qty=70)],
            partial_allowed=True,
            reserved_stock=[],
            use_due_date=False,
            service_mode=False
        )
    )
    
    # Сценарий A3: Режим Service (Anti-zero)
    demo_scenario(
        "Сценарий A3: Режим Service (Anti-zero)",
        "При дефиците каждый заказ получает минимум 1 единицу",
        InputData(
            orders=[
                Order(id='ORD001', sku='ITEM-A', qty=30, priority_class='A'),
                Order(id='ORD002', sku='ITEM-A', qty=30, priority_class='A'),
                Order(id='ORD003', sku='ITEM-A', qty=30, priority_class='A'),
            ],
            stock=[Stock(sku='ITEM-A', qty=50)],
            partial_allowed=True,
            reserved_stock=[],
            use_due_date=False,
            service_mode=True  # Service mode
        )
    )
    
    # Сценарий A4: All-or-nothing
    demo_scenario(
        "Сценарий A4: All-or-nothing",
        "Частичные отгрузки запрещены - либо полностью, либо 0",
        InputData(
            orders=[
                Order(id='ORD001', sku='ITEM-A', qty=30, priority_class='A'),
                Order(id='ORD002', sku='ITEM-A', qty=60, priority_class='A'),
            ],
            stock=[Stock(sku='ITEM-A', qty=70)],
            partial_allowed=False,  # All-or-nothing
            reserved_stock=[],
            use_due_date=False,
            service_mode=False
        )
    )
    
    # Сценарий C1: Ошибка - дублирующиеся ID
    demo_scenario(
        "Сценарий C1: Критическая ошибка - дублирующиеся ID заказов",
        "Система должна остановиться при обнаружении дублей",
        InputData(
            orders=[
                Order(id='ORD001', sku='ITEM-A', qty=10, priority_class='A'),
                Order(id='ORD001', sku='ITEM-B', qty=20, priority_class='B'),
            ],
            stock=[Stock(sku='ITEM-A', qty=100)],
            partial_allowed=True,
            reserved_stock=[],
            use_due_date=False,
            service_mode=False
        )
    )
    
    print("\n" + "=" * 80)
    print("✅ Демонстрация завершена!")
    print("=" * 80)


if __name__ == '__main__':
    main()
