"""Модуль расчета метрик и уровня риска"""

from typing import List
from src.models import AllocationResult


def calculate_fill_rate(allocations: List[AllocationResult]) -> float:
    """
    Расчет Fill Rate (процент заполнения заказов)
    
    Fill Rate = (Σ allocated / Σ requested) * 100
    """
    if not allocations:
        return 0.0
    
    total_requested = sum(a.requested for a in allocations)
    total_allocated = sum(a.allocated for a in allocations)
    
    if total_requested == 0:
        return 0.0
    
    return (total_allocated / total_requested) * 100


def count_zero_allocations(allocations: List[AllocationResult]) -> int:
    """
    Подсчет количества заказов с нулевым выделением
    """
    return sum(1 for a in allocations if a.allocated == 0)


def calculate_risk_level(fill_rate: float, count_zero: int, total_orders: int) -> str:
    """
    Определение уровня риска
    
    GREEN: Fill Rate >= 95% и Count Zero = 0
    YELLOW: Fill Rate >= 80% или Count Zero <= 2
    RED: Fill Rate < 80% или Count Zero > 2
    """
    if fill_rate >= 95.0 and count_zero == 0:
        return "GREEN"
    elif fill_rate >= 80.0 and count_zero <= 2:
        return "YELLOW"
    else:
        return "RED"


def calculate_metrics(allocations: List[AllocationResult]) -> dict:
    """
    Расчет всех метрик
    
    Returns:
        dict с ключами: fill_rate, count_zero, risk_level
    """
    fill_rate = calculate_fill_rate(allocations)
    count_zero = count_zero_allocations(allocations)
    total_orders = len(allocations)
    risk_level = calculate_risk_level(fill_rate, count_zero, total_orders)
    
    return {
        'fill_rate': fill_rate,
        'count_zero': count_zero,
        'risk_level': risk_level,
        'total_orders': total_orders
    }
