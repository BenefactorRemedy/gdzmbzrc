"""
CLI точка входа для SC-PRIORITY-DEMO-LITE RU v2.2
"""
import sys
import argparse
from typing import Optional
from src.parser import parse_input_data
from src.validator import validate_input_data, ValidationError
from src.allocator import Allocator
from src.metrics import calculate_all_metrics
from src.formatter import format_report
from src.models import AllocationReport


def read_multiline_input(prompt: str) -> str:
    """
    Чтение многострочного ввода (завершается пустой строкой)
    """
    print(f"\n{prompt}")
    print("(Введите данные, пустая строка для завершения)")
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    return '\n'.join(lines)


def interactive_mode() -> AllocationReport:
    """
    Интерактивный режим ввода данных
    """
    print("=" * 60)
    print("SC-PRIORITY-DEMO-LITE RU v2.2 - Интерактивный режим")
    print("=" * 60)
    
    # Ввод Q1-Q6
    q1 = read_multiline_input("Q1: Введите заказы (Формат: ID | SKU | Qty | Class [| Due_Date])")
    q2 = read_multiline_input("Q2: Введите складские остатки (Формат: SKU | Qty)")
    q3 = input("\nQ3: Разрешены частичные отгрузки? (YES/NO): ")
    q4 = read_multiline_input("Q4: Введите зарезервированные остатки (Формат: SKU | Qty)")
    q5 = input("\nQ5: Использовать сортировку по Due Date? (YES/NO): ")
    q6 = input("\nQ6: Режим обслуживания при дефиците (Service/Simplicity): ")
    
    # Парсинг
    data = parse_input_data(q1, q2, q3, q4, q5, q6)
    
    # Валидация
    errors, warnings = validate_input_data(data)
    
    if errors:
        # Критические ошибки - останавливаем
        report = AllocationReport(
            results=[],
            warnings=warnings,
            errors=errors,
            fill_rate=0.0,
            count_zero=0,
            risk_level='Red',
            input_data=data
        )
        return report
    
    # Распределение
    allocator = Allocator(data)
    results = allocator.allocate()
    
    # Метрики
    metrics = calculate_all_metrics(results)
    
    # Формируем отчет
    report = AllocationReport(
        results=results,
        warnings=warnings,
        errors=[],
        fill_rate=metrics['fill_rate'],
        count_zero=metrics['count_zero'],
        risk_level=metrics['risk_level'],
        input_data=data
    )
    
    return report


def file_mode(q1_file: str, q2_file: str, q3: str, q4_file: Optional[str], 
              q5: str, q6: str) -> AllocationReport:
    """
    Режим чтения из файлов
    """
    # Чтение файлов
    with open(q1_file, 'r', encoding='utf-8') as f:
        q1 = f.read()
    
    with open(q2_file, 'r', encoding='utf-8') as f:
        q2 = f.read()
    
    q4 = ''
    if q4_file:
        with open(q4_file, 'r', encoding='utf-8') as f:
            q4 = f.read()
    
    # Парсинг
    data = parse_input_data(q1, q2, q3, q4, q5, q6)
    
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
        return report
    
    # Распределение
    allocator = Allocator(data)
    results = allocator.allocate()
    
    # Метрики
    metrics = calculate_all_metrics(results)
    
    # Формируем отчет
    report = AllocationReport(
        results=results,
        warnings=warnings,
        errors=[],
        fill_rate=metrics['fill_rate'],
        count_zero=metrics['count_zero'],
        risk_level=metrics['risk_level'],
        input_data=data
    )
    
    return report


def main():
    """
    Главная функция CLI
    """
    parser = argparse.ArgumentParser(
        description='SC-PRIORITY-DEMO-LITE RU v2.2 - Система распределения с приоритетами'
    )
    
    parser.add_argument('--q1', help='Файл с заказами (Q1)')
    parser.add_argument('--q2', help='Файл с остатками (Q2)')
    parser.add_argument('--q3', help='Частичные отгрузки (YES/NO)')
    parser.add_argument('--q4', help='Файл с резервами (Q4)')
    parser.add_argument('--q5', help='Сортировка по Due Date (YES/NO)')
    parser.add_argument('--q6', help='Режим обслуживания (Service/Simplicity)')
    parser.add_argument('-o', '--output', help='Файл для сохранения отчета')
    
    args = parser.parse_args()
    
    # Определяем режим работы
    if args.q1 and args.q2 and args.q3 and args.q5 and args.q6:
        # Режим файлов
        report = file_mode(args.q1, args.q2, args.q3, args.q4, args.q5, args.q6)
    else:
        # Интерактивный режим
        report = interactive_mode()
    
    # Генерация отчета
    markdown_report = format_report(report)
    
    # Вывод отчета
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        print(f"\nОтчет сохранен в файл: {args.output}")
    else:
        print("\n" + "=" * 60)
        print(markdown_report)
        print("=" * 60)
    
    # Возвращаем код выхода
    if report.errors:
        return 1
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main())
