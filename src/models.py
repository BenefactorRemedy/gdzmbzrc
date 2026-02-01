"""Модели данных для SC-PRIORITY-DEMO-LITE"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List


@dataclass
class Order:
    """Модель заказа"""
    id: str
    sku: str
    qty: int
    order_class: str  # A, B, или C
    due_date: Optional[date] = None
    allocated: int = 0  # Сколько выделено данному заказу
    
    def __post_init__(self):
        # Преобразуем класс в верхний регистр
        if isinstance(self.order_class, str):
            self.order_class = self.order_class.upper()


@dataclass
class Stock:
    """Модель запаса SKU"""
    sku: str
    qty: int


@dataclass
class InputData:
    """Входные данные системы"""
    orders: List[Order] = field(default_factory=list)
    stock: List[Stock] = field(default_factory=list)
    q3_partial: bool = True  # Q3: YES=Partial allocation, NO=All-or-nothing
    q4_reserved: Optional[List[tuple]] = None  # Q4: List of (sku, reserved_qty)
    q5_use_due_date: bool = False  # Q5: YES=Sort by due_date, NO=FIFO
    q6_service_mode: bool = False  # Q6: YES=Service (Anti-zero), NO=Simplicity
    
    def __post_init__(self):
        if self.q4_reserved is None:
            self.q4_reserved = []


@dataclass
class AllocationResult:
    """Результат распределения для одного заказа"""
    order_id: str
    sku: str
    requested: int
    allocated: int
    status: str  # "OK", "PARTIAL", "ZERO", "STOPPED"
    
    @property
    def fill_rate(self) -> float:
        """Процент заполнения заказа"""
        if self.requested == 0:
            return 0.0
        return (self.allocated / self.requested) * 100


@dataclass
class SystemReport:
    """Финальный отчет системы"""
    status: str  # "OK", "WARN", "STOP"
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    allocations: List[AllocationResult] = field(default_factory=list)
    fill_rate: float = 0.0
    count_zero: int = 0
    risk_level: str = "GREEN"  # GREEN, YELLOW, RED
    input_summary: dict = field(default_factory=dict)
