"""CLI точка входа для SC-PRIORITY-DEMO-LITE"""

import sys
import argparse
from src.parser import parse_input_data
from src.validator import validate_input_data, ValidationError
from src.allocator import StockAllocator
from src.metrics import calculate_metrics
from src.formatter import format_report, format_input_summary
from src.models import SystemReport


def run_allocation(q1: str, q2: str, q3: str, q4: str, q5: str, q6: str) -> SystemReport:
    """
    Основная функция выполнения распределения
    
    Args:
        q1-q6: Строковые ответы на вопросы Q1-Q6
        
    Returns:
        SystemReport с результатами
    """
    # Парсинг входных данных
    try:
        data = parse_input_data(q1, q2, q3, q4, q5, q6)
    except Exception as e:
        return SystemReport(
            status="STOP",
            errors=[f"Ошибка парсинга данных: {str(e)}"]
        )
    
    # Валидация
    errors, warnings = validate_input_data(data)
    
    # Если есть критические ошибки - останавливаемся
    if errors:
        return SystemReport(
            status="STOP",
            errors=errors,
            warnings=warnings,
            input_summary=format_input_summary(data)
        )
    
    # Распределение
    try:
        allocator = StockAllocator(data)
        allocations = allocator.allocate()
    except Exception as e:
        return SystemReport(
            status="STOP",
            errors=[f"Ошибка распределения: {str(e)}"],
            warnings=warnings,
            input_summary=format_input_summary(data)
        )
    
    # Расчет метрик
    metrics = calculate_metrics(allocations)
    
    # Формирование отчета
    status = "WARN" if warnings else "OK"
    
    report = SystemReport(
        status=status,
        warnings=warnings,
        errors=[],
        allocations=allocations,
        fill_rate=metrics['fill_rate'],
        count_zero=metrics['count_zero'],
        risk_level=metrics['risk_level'],
        input_summary=format_input_summary(data)
    )
    
    return report


def interactive_mode():
    """Интерактивный режим ввода данных"""
    print("=" * 60)
    print("SC-PRIORITY-DEMO-LITE RU v2.2 - Интерактивный режим")
    print("=" * 60)
    print()
    
    print("Q1: Список заказов (формат: ID|SKU|QTY|CLASS|DUE_DATE)")
    print("Введите строки, пустая строка для завершения:")
    q1_lines = []
    while True:
        line = input()
        if not line.strip():
            break
        q1_lines.append(line)
    q1 = "\n".join(q1_lines)
    
    print("\nQ2: Список запасов (формат: SKU|QTY)")
    print("Введите строки, пустая строка для завершения:")
    q2_lines = []
    while True:
        line = input()
        if not line.strip():
            break
        q2_lines.append(line)
    q2 = "\n".join(q2_lines)
    
    print("\nQ3: Partial allocation? (YES/NO):")
    q3 = input().strip()
    
    print("\nQ4: Зарезервированные количества (формат: SKU|QTY, или NO)")
    print("Введите строки, пустая строка для завершения:")
    q4_lines = []
    while True:
        line = input()
        if not line.strip():
            break
        q4_lines.append(line)
    q4 = "\n".join(q4_lines) if q4_lines else "NO"
    
    print("\nQ5: Sort by due date? (YES/NO):")
    q5 = input().strip()
    
    print("\nQ6: Service mode (Anti-zero)? (YES/NO):")
    q6 = input().strip()
    
    return q1, q2, q3, q4, q5, q6


def main():
    """CLI точка входа"""
    parser = argparse.ArgumentParser(
        description='SC-PRIORITY-DEMO-LITE RU v2.2 - Система распределения запасов'
    )
    
    parser.add_argument('--q1', help='Q1: Список заказов')
    parser.add_argument('--q2', help='Q2: Список запасов')
    parser.add_argument('--q3', help='Q3: Partial allocation (YES/NO)')
    parser.add_argument('--q4', help='Q4: Зарезервированные количества')
    parser.add_argument('--q5', help='Q5: Sort by due date (YES/NO)')
    parser.add_argument('--q6', help='Q6: Service mode (YES/NO)')
    parser.add_argument('--output', '-o', help='Выходной файл для отчета')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Интерактивный режим ввода')
    
    args = parser.parse_args()
    
    # Интерактивный режим
    if args.interactive or not all([args.q1, args.q2, args.q3, args.q5, args.q6]):
        if not args.interactive:
            print("Недостаточно аргументов. Переход в интерактивный режим...")
            print()
        q1, q2, q3, q4, q5, q6 = interactive_mode()
    else:
        q1 = args.q1
        q2 = args.q2
        q3 = args.q3
        q4 = args.q4 or "NO"
        q5 = args.q5
        q6 = args.q6
    
    # Выполнение распределения
    print("\nВыполнение распределения...")
    report = run_allocation(q1, q2, q3, q4, q5, q6)
    
    # Форматирование отчета
    markdown_report = format_report(report)
    
    # Вывод отчета
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        print(f"\nОтчет сохранен в файл: {args.output}")
    else:
        print("\n")
        print(markdown_report)
    
    # Возвращаем код выхода
    if report.status == "STOP":
        return 1
    elif report.status == "WARN":
        return 0  # Предупреждения не являются ошибкой
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
