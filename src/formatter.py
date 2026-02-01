"""Модуль форматирования отчетов в Markdown"""

from typing import List
from src.models import SystemReport, AllocationResult, InputData


def format_report(report: SystemReport) -> str:
    """
    Генерирует Markdown-отчет в 3 секции:
    1. Статус системы
    2. Входные данные (Q1-Q6)
    3. Результаты распределения
    """
    lines = []
    
    # === СЕКЦИЯ 1: СТАТУС СИСТЕМЫ ===
    lines.append("# ОТЧЕТ СИСТЕМЫ SC-PRIORITY-DEMO-LITE RU v2.2")
    lines.append("")
    lines.append("## 1. СТАТУС СИСТЕМЫ")
    lines.append("")
    
    if report.status == "STOP":
        lines.append("**СТАТУС:** ❌ STOP (КРИТИЧЕСКИЕ ОШИБКИ)")
        lines.append("")
        lines.append("### Критические ошибки:")
        for error in report.errors:
            lines.append(f"- {error}")
        lines.append("")
        return "\n".join(lines)
    
    elif report.status == "WARN":
        lines.append("**СТАТУС:** ⚠️ WARN (ПРЕДУПРЕЖДЕНИЯ)")
        lines.append("")
        if report.warnings:
            lines.append("### Предупреждения:")
            for warning in report.warnings:
                lines.append(f"- {warning}")
            lines.append("")
    
    else:
        lines.append("**СТАТУС:** ✅ OK")
        lines.append("")
    
    # === СЕКЦИЯ 2: ВХОДНЫЕ ДАННЫЕ ===
    lines.append("## 2. ВХОДНЫЕ ДАННЫЕ")
    lines.append("")
    
    summary = report.input_summary
    
    lines.append("| Вопрос | Ответ |")
    lines.append("|--------|-------|")
    lines.append(f"| Q1: Количество заказов | {summary.get('total_orders', 0)} |")
    lines.append(f"| Q2: Количество SKU | {summary.get('total_skus', 0)} |")
    lines.append(f"| Q3: Partial allocation | {summary.get('q3_partial', '-')} |")
    lines.append(f"| Q4: Есть резервы | {summary.get('q4_has_reserved', '-')} |")
    lines.append(f"| Q5: Sort by due date | {summary.get('q5_use_due_date', '-')} |")
    lines.append(f"| Q6: Service mode | {summary.get('q6_service_mode', '-')} |")
    lines.append("")
    
    # === СЕКЦИЯ 3: РЕЗУЛЬТАТЫ РАСПРЕДЕЛЕНИЯ ===
    lines.append("## 3. РЕЗУЛЬТАТЫ РАСПРЕДЕЛЕНИЯ")
    lines.append("")
    
    # Таблица распределения
    lines.append("### Распределение по заказам")
    lines.append("")
    lines.append("| ID заказа | SKU | Запрошено | Выделено | Fill Rate | Статус |")
    lines.append("|-----------|-----|-----------|----------|-----------|--------|")
    
    for alloc in report.allocations:
        status_icon = _get_status_icon(alloc.status)
        lines.append(
            f"| {alloc.order_id} | {alloc.sku} | {alloc.requested} | "
            f"{alloc.allocated} | {alloc.fill_rate:.1f}% | {status_icon} {alloc.status} |"
        )
    
    lines.append("")
    
    # Метрики
    lines.append("### Метрики")
    lines.append("")
    lines.append(f"- **Fill Rate:** {report.fill_rate:.2f}%")
    lines.append(f"- **Count Zero:** {report.count_zero}")
    lines.append(f"- **Risk Level:** {_get_risk_icon(report.risk_level)} {report.risk_level}")
    lines.append("")
    
    return "\n".join(lines)


def _get_status_icon(status: str) -> str:
    """Возвращает иконку для статуса заказа"""
    icons = {
        "OK": "✅",
        "PARTIAL": "⚠️",
        "ZERO": "❌",
        "STOPPED": "🛑"
    }
    return icons.get(status, "❓")


def _get_risk_icon(risk_level: str) -> str:
    """Возвращает иконку для уровня риска"""
    icons = {
        "GREEN": "🟢",
        "YELLOW": "🟡",
        "RED": "🔴"
    }
    return icons.get(risk_level, "⚪")


def format_input_summary(data: InputData) -> dict:
    """
    Формирует сводку входных данных для отчета
    """
    return {
        'total_orders': len(data.orders),
        'total_skus': len(data.stock),
        'q3_partial': 'YES' if data.q3_partial else 'NO',
        'q4_has_reserved': 'YES' if data.q4_reserved else 'NO',
        'q5_use_due_date': 'YES' if data.q5_use_due_date else 'NO',
        'q6_service_mode': 'YES' if data.q6_service_mode else 'NO'
    }
