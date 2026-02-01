"""
Расчет метрик: Fill Rate, Count Zero, Risk Level
"""
from typing import List
from src.models import AllocationResult


def calculate_fill_rate(results: List[AllocationResult]) -> float:
    """
    Расчет Fill Rate (процент выполненных заказов)
    Fill Rate = (выполненные заказы) / (всего заказов) * 100%
    """
    if not results:
        return 0.0
    
    fulfilled = sum(1 for r in results if r.is_fulfilled)
    total = len(results)
    
    return (fulfilled / total) * 100.0


def calculate_count_zero(results: List[AllocationResult]) -> int:
    """
    Расчет Count Zero (количество заказов с нулевым выделением)
    """
    return sum(1 for r in results if r.is_zero)


def calculate_risk_level(fill_rate: float, count_zero: int, total_orders: int) -> str:
    """
    Расчет уровня риска на основе Fill Rate и Count Zero
    
    Правила:
    - Green: Fill Rate >= 90% И Count Zero = 0
    - Red: Fill Rate < 70% ИЛИ Count Zero > 20% заказов
    - Yellow: все остальные случаи
    """
    if total_orders == 0:
        return "Green"
    
    zero_percentage = (count_zero / total_orders) * 100.0
    
    # Green: высокий Fill Rate и нет нулевых заказов
    if fill_rate >= 90.0 and count_zero == 0:
        return "Green"
    
    # Red: низкий Fill Rate или много нулевых заказов
    if fill_rate < 70.0 or zero_percentage > 20.0:
        return "Red"
    
    # Yellow: все остальное
    return "Yellow"


def calculate_all_metrics(results: List[AllocationResult]) -> dict:
    """
    Расчет всех метрик
    """
    fill_rate = calculate_fill_rate(results)
    count_zero = calculate_count_zero(results)
    total_orders = len(results)
    risk_level = calculate_risk_level(fill_rate, count_zero, total_orders)
    
    return {
        'fill_rate': fill_rate,
        'count_zero': count_zero,
        'total_orders': total_orders,
        'risk_level': risk_level
    }
