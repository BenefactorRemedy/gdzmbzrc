"""
Расчет метрик: Fill Rate, Count Zero, Risk Level
"""
from typing import List
from src.models import AllocationResult


def calculate_fill_rate(results: List[AllocationResult]) -> float:
    """
    Расчет общего Fill Rate (процент выполнения)
    Fill Rate = (сумма allocated / сумма requested) * 100
    """
    if not results:
        return 0.0
    
    total_requested = sum(r.requested for r in results)
    total_allocated = sum(r.allocated for r in results)
    
    if total_requested == 0:
        return 0.0
    
    return (total_allocated / total_requested) * 100


def calculate_zero_count(results: List[AllocationResult]) -> int:
    """
    Подсчет количества заказов с нулевым распределением
    """
    return sum(1 for r in results if r.allocated == 0)


def calculate_risk_level(fill_rate: float, zero_count: int, total_orders: int) -> str:
    """
    Расчет уровня риска
    
    Правила:
    - GREEN: Fill Rate >= 90% И zero_count = 0
    - RED: Fill Rate < 70% ИЛИ zero_count > 30% от общего числа заказов
    - YELLOW: все остальные случаи
    """
    if fill_rate >= 90 and zero_count == 0:
        return "GREEN"
    
    zero_rate = (zero_count / total_orders * 100) if total_orders > 0 else 0
    
    if fill_rate < 70 or zero_rate > 30:
        return "RED"
    
    return "YELLOW"


def calculate_metrics(results: List[AllocationResult]) -> dict:
    """
    Рассчитать все метрики
    Возвращает словарь с метриками
    """
    fill_rate = calculate_fill_rate(results)
    zero_count = calculate_zero_count(results)
    total_orders = len(results)
    risk_level = calculate_risk_level(fill_rate, zero_count, total_orders)
    
    total_requested = sum(r.requested for r in results)
    total_allocated = sum(r.allocated for r in results)
    
    return {
        "fill_rate": round(fill_rate, 2),
        "fill_rate_display": f"{fill_rate:.1f}%",
        "zero_count": zero_count,
        "total_orders": total_orders,
        "risk_level": risk_level,
        "total_requested": total_requested,
        "total_allocated": total_allocated,
        "unfulfilled": total_requested - total_allocated
    }
