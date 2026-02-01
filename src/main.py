"""
CLI для SC-PRIORITY-DEMO-LITE RU v2.2
"""
import sys
import argparse
from src.parser import parse_input_data
from src.validator import validate_input_data, has_stop_errors
from src.allocator import Allocator
from src.metrics import calculate_metrics
from src.formatter import format_report
from src.models import AllocationReport


def run_allocation(q1: str, q2: str, q3: str = "YES", q4: str = "-", 
                   q5: str = "NO", q6: str = "NO") -> AllocationReport:
    """
    Основная функция распределения
    
    Параметры:
        q1: Заказы (OrderID|SKU|Qty|Class|DueDate)
        q2: Остатки (SKU|Qty)
        q3: Частичная отгрузка (YES/NO)
        q4: Резервы (SKU|Reserved)
        q5: Сортировка по дате (YES/NO)
        q6: Режим сервис (YES/NO)
    
    Возвращает:
        AllocationReport с результатами
    """
    # Парсинг входных данных
    input_data = parse_input_data(q1, q2, q3, q4, q5, q6)
    
    # Валидация
    errors = validate_input_data(input_data)
    
    # Определить статус
    if has_stop_errors(errors):
        status = "STOP"
        results = []
        metrics = {}
    else:
        # Выполнить распределение
        allocator = Allocator(input_data)
        results = allocator.allocate()
        metrics = calculate_metrics(results)
        
        # Определить статус: WARN если есть предупреждения, иначе SUCCESS
        status = "WARN" if errors else "SUCCESS"
    
    return AllocationReport(
        status=status,
        errors=errors,
        results=results,
        metrics=metrics,
        input_summary={
            "orders_count": len(input_data.orders),
            "stock_items": len(input_data.stock),
            "allow_partial": input_data.allow_partial,
            "service_mode": input_data.service_mode
        }
    )


def interactive_mode():
    """Интерактивный режим ввода данных"""
    print("=== SC-PRIORITY-DEMO-LITE RU v2.2 ===")
    print("Интерактивный режим")
    print()
    
    print("Q1: Введите заказы (формат: OrderID|SKU|Qty|Class|DueDate)")
    print("    Для завершения ввода введите пустую строку")
    q1_lines = []
    while True:
        line = input("> ")
        if not line.strip():
            break
        q1_lines.append(line)
    q1 = "\n".join(q1_lines) if q1_lines else "-"
    
    print()
    print("Q2: Введите остатки (формат: SKU|Qty)")
    print("    Для завершения ввода введите пустую строку")
    q2_lines = []
    while True:
        line = input("> ")
        if not line.strip():
            break
        q2_lines.append(line)
    q2 = "\n".join(q2_lines) if q2_lines else "-"
    
    print()
    q3 = input("Q3: Разрешена частичная отгрузка? (YES/NO) [YES]: ").strip() or "YES"
    
    print()
    print("Q4: Введите резервы (формат: SKU|Reserved)")
    print("    Для завершения ввода или пропуска введите пустую строку")
    q4_lines = []
    while True:
        line = input("> ")
        if not line.strip():
            break
        q4_lines.append(line)
    q4 = "\n".join(q4_lines) if q4_lines else "-"
    
    print()
    q5 = input("Q5: Сортировать по дате? (YES/NO) [NO]: ").strip() or "NO"
    
    print()
    q6 = input("Q6: Режим 'Сервис' (анти-ноль)? (YES/NO) [NO]: ").strip() or "NO"
    
    # Выполнить распределение
    print()
    print("=" * 60)
    print("Выполняется распределение...")
    print("=" * 60)
    print()
    
    report = run_allocation(q1, q2, q3, q4, q5, q6)
    input_data = parse_input_data(q1, q2, q3, q4, q5, q6)
    
    # Вывести отчет
    output = format_report(report, input_data)
    print(output)
    
    return report


def file_mode(args):
    """Режим работы с файлами"""
    # Чтение входных данных из файла или аргументов
    q1 = args.q1 or "-"
    q2 = args.q2 or "-"
    q3 = args.q3 or "YES"
    q4 = args.q4 or "-"
    q5 = args.q5 or "NO"
    q6 = args.q6 or "NO"
    
    # Выполнить распределение
    report = run_allocation(q1, q2, q3, q4, q5, q6)
    input_data = parse_input_data(q1, q2, q3, q4, q5, q6)
    
    # Сформировать отчет
    output = format_report(report, input_data)
    
    # Вывод в файл или консоль
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Отчет сохранен в {args.output}")
    else:
        print(output)
    
    return report


def main():
    """Точка входа CLI"""
    parser = argparse.ArgumentParser(
        description='SC-PRIORITY-DEMO-LITE RU v2.2 - Распределение запасов с приоритетами'
    )
    
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Интерактивный режим ввода')
    parser.add_argument('--q1', help='Q1: Заказы (OrderID|SKU|Qty|Class|DueDate)')
    parser.add_argument('--q2', help='Q2: Остатки (SKU|Qty)')
    parser.add_argument('--q3', default='YES', help='Q3: Частичная отгрузка (YES/NO)')
    parser.add_argument('--q4', default='-', help='Q4: Резервы (SKU|Reserved)')
    parser.add_argument('--q5', default='NO', help='Q5: Сортировка по дате (YES/NO)')
    parser.add_argument('--q6', default='NO', help='Q6: Режим сервис (YES/NO)')
    parser.add_argument('--output', '-o', help='Файл для сохранения отчета')
    
    args = parser.parse_args()
    
    if args.interactive:
        report = interactive_mode()
    else:
        if not args.q1 and not args.q2:
            print("Ошибка: Требуются параметры --q1 и --q2, или используйте --interactive")
            parser.print_help()
            sys.exit(1)
        report = file_mode(args)
    
    # Код возврата зависит от статуса
    if report.status == "STOP":
        sys.exit(2)
    elif report.status == "WARN":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
