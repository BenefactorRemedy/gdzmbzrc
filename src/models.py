"""
Модели данных для SC-PRIORITY-DEMO-LITE RU v2.2
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date


@dataclass
class Order:
    """Заказ на товар"""
    id: str
    sku: str
    qty: int
    priority_class: str  # A, B, or C
    due_date: Optional[date] = None
    
    def __post_init__(self):
        if self.priority_class not in ['A', 'B', 'C']:
            raise ValueError(f"Недопустимый класс приоритета: {self.priority_class}")


@dataclass
class Stock:
    """Складской остаток"""
    sku: str
    qty: int


@dataclass
class InputData:
    """Входные данные из 6 вопросов"""
    orders: List[Order] = field(default_factory=list)  # Q1
    stock: List[Stock] = field(default_factory=list)   # Q2
    partial_allowed: bool = True                       # Q3 (YES=True, NO=False)
    reserved_stock: List[Stock] = field(default_factory=list)  # Q4
    use_due_date: bool = False                         # Q5 (YES=True, NO=False)
    service_mode: bool = False                         # Q6 (Service=True, Simplicity=False)


@dataclass
class AllocationResult:
    """Результат распределения для одного заказа"""
    order_id: str
    sku: str
    requested_qty: int
    allocated_qty: int
    priority_class: str
    
    @property
    def is_fulfilled(self) -> bool:
        """Полностью ли выполнен заказ"""
        return self.allocated_qty == self.requested_qty
    
    @property
    def is_zero(self) -> bool:
        """Получил ли заказ 0 единиц"""
        return self.allocated_qty == 0


@dataclass
class AllocationReport:
    """Полный отчет о распределении"""
    results: List[AllocationResult]
    warnings: List[str]
    errors: List[str]
    fill_rate: float
    count_zero: int
    risk_level: str  # Green, Yellow, Red
    input_data: InputData
