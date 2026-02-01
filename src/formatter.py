"""
Генерация Markdown-отчета о распределении
"""
from typing import List
from src.models import AllocationReport, InputData, AllocationResult


def format_report(report: AllocationReport) -> str:
    """
    Генерация полного Markdown-отчета в 3 секции:
    1. Статус (ошибки, предупреждения)
    2. Таблица входных данных Q1-Q6
    3. Результаты распределения
    """
    sections = []
    
    # Секция 1: Статус
    sections.append(_format_status_section(report))
    
    # Секция 2: Входные данные
    sections.append(_format_input_section(report.input_data))
    
    # Секция 3: Результаты
    sections.append(_format_results_section(report))
    
    return '\n\n'.join(sections)


def _format_status_section(report: AllocationReport) -> str:
    """Секция статуса с ошибками и предупреждениями"""
    lines = ['## 📊 Статус обработки', '']
    
    if report.errors:
        lines.append('### ❌ КРИТИЧЕСКИЕ ОШИБКИ (STOP)')
        for error in report.errors:
            lines.append(f'- {error}')
        lines.append('')
    
    if report.warnings:
        lines.append('### ⚠️ ПРЕДУПРЕЖДЕНИЯ (WARN)')
        for warning in report.warnings:
            lines.append(f'- {warning}')
        lines.append('')
    
    if not report.errors and not report.warnings:
        lines.append('✅ Валидация пройдена успешно, ошибок не обнаружено')
        lines.append('')
    
    return '\n'.join(lines)


def _format_input_section(data: InputData) -> str:
    """Секция входных данных Q1-Q6"""
    lines = ['## 📝 Входные данные', '']
    
    # Q1: Заказы
    lines.append('### Q1: Заказы')
    lines.append('')
    lines.append('| ID | SKU | Qty | Class | Due Date |')
    lines.append('|---|---|---|---|---|')
    for order in data.orders:
        due_date = order.due_date.strftime('%Y-%m-%d') if order.due_date else '-'
        lines.append(f'| {order.id} | {order.sku} | {order.qty} | {order.priority_class} | {due_date} |')
    lines.append('')
    
    # Q2: Складские остатки
    lines.append('### Q2: Складские остатки')
    lines.append('')
    lines.append('| SKU | Qty |')
    lines.append('|---|---|')
    for stock in data.stock:
        lines.append(f'| {stock.sku} | {stock.qty} |')
    lines.append('')
    
    # Q3: Частичные отгрузки
    lines.append('### Q3: Частичные отгрузки')
    lines.append('')
    partial_text = 'YES (разрешены)' if data.partial_allowed else 'NO (все или ничего)'
    lines.append(f'**{partial_text}**')
    lines.append('')
    
    # Q4: Зарезервированные остатки
    lines.append('### Q4: Зарезервированные остатки')
    lines.append('')
    if data.reserved_stock:
        lines.append('| SKU | Qty |')
        lines.append('|---|---|')
        for reserved in data.reserved_stock:
            lines.append(f'| {reserved.sku} | {reserved.qty} |')
    else:
        lines.append('_Резервов нет_')
    lines.append('')
    
    # Q5: Сортировка по Due Date
    lines.append('### Q5: Сортировка по Due Date')
    lines.append('')
    due_date_text = 'YES (по дате)' if data.use_due_date else 'NO (FIFO)'
    lines.append(f'**{due_date_text}**')
    lines.append('')
    
    # Q6: Режим обслуживания
    lines.append('### Q6: Режим обслуживания при дефиците')
    lines.append('')
    service_text = 'Service (Anti-zero)' if data.service_mode else 'Simplicity (FIFO)'
    lines.append(f'**{service_text}**')
    lines.append('')
    
    return '\n'.join(lines)


def _format_results_section(report: AllocationReport) -> str:
    """Секция результатов распределения"""
    lines = ['## 🎯 Результаты распределения', '']
    
    # Метрики
    lines.append('### Метрики')
    lines.append('')
    lines.append(f'- **Fill Rate**: {report.fill_rate:.1f}%')
    lines.append(f'- **Count Zero**: {report.count_zero}')
    lines.append(f'- **Risk Level**: {_format_risk_badge(report.risk_level)}')
    lines.append('')
    
    # Таблица результатов
    lines.append('### Распределение по заказам')
    lines.append('')
    lines.append('| Order ID | SKU | Запрошено | Выделено | Class | Статус |')
    lines.append('|---|---|---|---|---|---|')
    
    for result in report.results:
        status = _format_status_badge(result)
        lines.append(
            f'| {result.order_id} | {result.sku} | {result.requested_qty} | '
            f'{result.allocated_qty} | {result.priority_class} | {status} |'
        )
    lines.append('')
    
    return '\n'.join(lines)


def _format_risk_badge(risk_level: str) -> str:
    """Форматирование бейджа уровня риска"""
    badges = {
        'Green': '🟢 Green',
        'Yellow': '🟡 Yellow',
        'Red': '🔴 Red'
    }
    return badges.get(risk_level, risk_level)


def _format_status_badge(result: AllocationResult) -> str:
    """Форматирование статуса заказа"""
    if result.is_fulfilled:
        return '✅ Выполнен'
    elif result.is_zero:
        return '❌ Ноль'
    else:
        return '⚠️ Частично'
