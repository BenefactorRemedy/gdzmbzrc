"""
Генерация Markdown отчетов
"""
from typing import List
from src.models import AllocationReport, AllocationResult, ValidationError, InputData


def format_report(report: AllocationReport, input_data: InputData) -> str:
    """
    Сформировать полный Markdown отчет
    
    Структура отчета:
    1. Статус (SUCCESS/WARN/STOP)
    2. Ошибки и предупреждения (если есть)
    3. Таблица входных данных (Q1-Q6)
    4. Результаты распределения
    5. Метрики
    """
    sections = []
    
    # Секция 1: Статус
    sections.append(_format_status_section(report))
    
    # Секция 2: Ошибки (если есть)
    if report.errors:
        sections.append(_format_errors_section(report.errors))
    
    # Секция 3: Входные данные
    sections.append(_format_input_section(input_data))
    
    # Секция 4: Результаты (только если нет STOP ошибок)
    if report.status != "STOP":
        sections.append(_format_results_section(report.results))
        
        # Секция 5: Метрики
        if report.metrics:
            sections.append(_format_metrics_section(report.metrics))
    
    return "\n\n".join(sections)


def _format_status_section(report: AllocationReport) -> str:
    """Форматирование секции статуса"""
    status_icons = {
        "SUCCESS": "✅",
        "WARN": "⚠️",
        "STOP": "🛑"
    }
    
    icon = status_icons.get(report.status, "")
    
    lines = [
        f"# {icon} Статус: {report.status}",
        ""
    ]
    
    if report.status == "SUCCESS":
        lines.append("Распределение выполнено успешно.")
    elif report.status == "WARN":
        lines.append("Распределение выполнено с предупреждениями.")
    elif report.status == "STOP":
        lines.append("Распределение остановлено из-за критических ошибок.")
    
    return "\n".join(lines)


def _format_errors_section(errors: List[ValidationError]) -> str:
    """Форматирование секции ошибок"""
    lines = ["## Ошибки и предупреждения", ""]
    
    # Группировать по уровню
    stop_errors = [e for e in errors if e.level == "STOP"]
    warn_errors = [e for e in errors if e.level == "WARN"]
    
    if stop_errors:
        lines.append("### 🛑 Критические ошибки (STOP)")
        lines.append("")
        for err in stop_errors:
            lines.append(f"**{err.code}**: {err.message}")
            if err.details:
                lines.append(f"  - {err.details}")
            lines.append("")
    
    if warn_errors:
        lines.append("### ⚠️ Предупреждения (WARN)")
        lines.append("")
        for err in warn_errors:
            lines.append(f"**{err.code}**: {err.message}")
            if err.details:
                lines.append(f"  - {err.details}")
            lines.append("")
    
    return "\n".join(lines)


def _format_input_section(data: InputData) -> str:
    """Форматирование секции входных данных"""
    lines = ["## Входные данные", ""]
    
    # Q1: Заказы
    lines.append("### Q1: Заказы")
    lines.append("")
    lines.append("| Order ID | SKU | Qty | Class | Due Date |")
    lines.append("|----------|-----|-----|-------|----------|")
    for order in data.orders:
        due_date_str = order.due_date.strftime("%Y-%m-%d") if order.due_date else "-"
        lines.append(f"| {order.order_id} | {order.sku} | {order.qty} | {order.priority_class} | {due_date_str} |")
    lines.append("")
    
    # Q2: Остатки
    lines.append("### Q2: Остатки")
    lines.append("")
    lines.append("| SKU | Qty | Reserved | Available |")
    lines.append("|-----|-----|----------|-----------|")
    for stock in data.stock:
        lines.append(f"| {stock.sku} | {stock.qty} | {stock.reserved} | {stock.available} |")
    lines.append("")
    
    # Q3-Q6: Настройки
    lines.append("### Настройки")
    lines.append("")
    lines.append(f"- **Q3** (Частичная отгрузка): {'ДА' if data.allow_partial else 'НЕТ'}")
    lines.append(f"- **Q5** (Сортировка по дате): {'ДА' if data.sort_by_due_date else 'НЕТ'}")
    lines.append(f"- **Q6** (Режим Сервис - анти-ноль): {'ДА' if data.service_mode else 'НЕТ'}")
    
    return "\n".join(lines)


def _format_results_section(results: List[AllocationResult]) -> str:
    """Форматирование секции результатов"""
    lines = ["## Результаты распределения", ""]
    
    lines.append("| Order ID | SKU | Запрошено | Выделено | Fill Rate | Class |")
    lines.append("|----------|-----|-----------|----------|-----------|-------|")
    
    for result in results:
        fill_rate_str = f"{result.fill_rate:.1f}%"
        lines.append(f"| {result.order_id} | {result.sku} | {result.requested} | {result.allocated} | {fill_rate_str} | {result.priority_class} |")
    
    return "\n".join(lines)


def _format_metrics_section(metrics: dict) -> str:
    """Форматирование секции метрик"""
    lines = ["## Метрики", ""]
    
    # Уровень риска с эмодзи
    risk_icons = {
        "GREEN": "🟢",
        "YELLOW": "🟡",
        "RED": "🔴"
    }
    risk_level = metrics.get("risk_level", "UNKNOWN")
    risk_icon = risk_icons.get(risk_level, "")
    
    lines.append(f"**Уровень риска**: {risk_icon} {risk_level}")
    lines.append("")
    lines.append(f"- **Fill Rate**: {metrics.get('fill_rate_display', '0.0%')}")
    lines.append(f"- **Количество нулевых распределений**: {metrics.get('zero_count', 0)}")
    lines.append(f"- **Всего заказов**: {metrics.get('total_orders', 0)}")
    lines.append(f"- **Запрошено (всего)**: {metrics.get('total_requested', 0)}")
    lines.append(f"- **Выделено (всего)**: {metrics.get('total_allocated', 0)}")
    lines.append(f"- **Невыполнено**: {metrics.get('unfulfilled', 0)}")
    
    return "\n".join(lines)
