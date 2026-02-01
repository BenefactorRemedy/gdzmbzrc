"""
Модели данных для SC-PRIORITY-DEMO-LITE RU v2.2
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date


@dataclass
class Order:
    """Заказ на товар"""
    order_id: str
    sku: str
    qty: int
    priority_class: str  # A, B, или C
    due_date: Optional[date] = None
    allocated: int = 0
    
    def __post_init__(self):
        # Нормализация класса приоритета
        if self.priority_class:
            self.priority_class = self.priority_class.upper()


@dataclass
class Stock:
    """Остаток товара на складе"""
    sku: str
    qty: int
    reserved: int = 0
    
    @property
    def available(self) -> int:
        """Доступное количество = остаток - резерв"""
        return max(0, self.qty - self.reserved)


@dataclass
class AllocationResult:
    """Результат распределения для одного заказа"""
    order_id: str
    sku: str
    requested: int
    allocated: int
    priority_class: str
    
    @property
    def fill_rate(self) -> float:
        """Процент выполнения заказа"""
        if self.requested == 0:
            return 0.0
        return (self.allocated / self.requested) * 100


@dataclass
class InputData:
    """Входные данные из Q1-Q6"""
    orders: List[Order] = field(default_factory=list)
    stock: List[Stock] = field(default_factory=list)
    allow_partial: bool = True  # Q3: YES = частичная отгрузка, NO = все или ничего
    reserved_stock: List[Stock] = field(default_factory=list)  # Q4
    sort_by_due_date: bool = False  # Q5: YES = сортировка по дате, NO = FIFO
    service_mode: bool = False  # Q6: YES = анти-ноль (сервис), NO = простота
    
    def get_stock_for_sku(self, sku: str) -> Optional[Stock]:
        """Получить остаток по SKU"""
        for s in self.stock:
            if s.sku == sku:
                return s
        return None


@dataclass
class ValidationError:
    """Ошибка валидации"""
    level: str  # STOP или WARN
    code: str  # C1, C2, B1, B2 и т.д.
    message: str
    details: Optional[str] = None


@dataclass
class AllocationReport:
    """Полный отчет о распределении"""
    status: str  # SUCCESS, WARN, STOP
    errors: List[ValidationError] = field(default_factory=list)
    results: List[AllocationResult] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    input_summary: dict = field(default_factory=dict)
