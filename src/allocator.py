"""
Ядро распределения запасов с приоритетами A → B → C
"""
from typing import List, Dict
from src.models import InputData, Order, Stock, AllocationResult


class Allocator:
    """Движок распределения запасов"""
    
    def __init__(self, data: InputData):
        self.data = data
        # Создаем рабочую копию доступных остатков
        self.available_stock: Dict[str, int] = {}
        for stock in data.stock:
            self.available_stock[stock.sku] = stock.available
    
    def allocate(self) -> List[AllocationResult]:
        """
        Выполнить распределение запасов
        Основная логика:
        1. Сортировка заказов по приоритету (A → B → C)
        2. Внутри приоритета: по дате (Q5) или FIFO
        3. Распределение с учетом Q3 (частичная/полная) и Q6 (сервис/простота)
        """
        results = []
        
        # Подготовить заказы к распределению
        orders = self._prepare_orders()
        
        # Если режим "Сервис" (Q6), применить анти-ноль логику
        if self.data.service_mode:
            orders = self._apply_anti_zero(orders)
        
        # Распределить остатки по заказам
        for order in orders:
            allocated = self._allocate_order(order)
            
            results.append(AllocationResult(
                order_id=order.order_id,
                sku=order.sku,
                requested=order.qty,
                allocated=allocated,
                priority_class=order.priority_class
            ))
        
        return results
    
    def _prepare_orders(self) -> List[Order]:
        """
        Подготовить и отсортировать заказы
        1. Сортировка по приоритету: A → B → C
        2. Внутри приоритета: по дате (Q5=YES) или FIFO (Q5=NO)
        """
        orders = self.data.orders.copy()
        
        # Определить порядок приоритетов
        priority_order = {'A': 1, 'B': 2, 'C': 3}
        
        if self.data.sort_by_due_date:
            # Сортировка: сначала по приоритету, затем по дате
            orders.sort(key=lambda o: (
                priority_order.get(o.priority_class, 999),
                o.due_date if o.due_date else datetime.date(9999, 12, 31)
            ))
        else:
            # Сортировка: только по приоритету (FIFO внутри каждого)
            orders.sort(key=lambda o: priority_order.get(o.priority_class, 999))
        
        return orders
    
    def _apply_anti_zero(self, orders: List[Order]) -> List[Order]:
        """
        Применить логику "Сервис" (Q6=YES): Анти-ноль
        
        Если есть дефицит и конкуренция за один SKU:
        1. Сначала раздать по 1 шт каждому заказу
        2. Остаток распределить по FIFO
        
        Возвращает модифицированные заказы с предварительным выделением
        """
        # Группировать заказы по SKU
        sku_groups: Dict[str, List[Order]] = {}
        for order in orders:
            if order.sku not in sku_groups:
                sku_groups[order.sku] = []
            sku_groups[order.sku].append(order)
        
        # Для каждого SKU проверить дефицит и конкуренцию
        for sku, sku_orders in sku_groups.items():
            available = self.available_stock.get(sku, 0)
            total_demand = sum(o.qty for o in sku_orders)
            
            # Дефицит + конкуренция (более 1 заказа)
            if available < total_demand and len(sku_orders) > 1:
                # Раздать по 1 каждому заказу
                anti_zero_count = min(available, len(sku_orders))
                for i, order in enumerate(sku_orders):
                    if i < anti_zero_count:
                        order.allocated = 1
                        self.available_stock[sku] -= 1
        
        return orders
    
    def _allocate_order(self, order: Order) -> int:
        """
        Распределить остатки для одного заказа
        Учитывает Q3 (частичная/полная отгрузка)
        """
        available = self.available_stock.get(order.sku, 0)
        
        # Уже есть предварительное выделение (анти-ноль)?
        already_allocated = order.allocated
        remaining_need = order.qty - already_allocated
        
        if self.data.allow_partial:
            # Q3=YES: Частичная отгрузка разрешена
            can_allocate = min(remaining_need, available)
            self.available_stock[order.sku] = available - can_allocate
            return already_allocated + can_allocate
        else:
            # Q3=NO: Все или ничего
            if available >= remaining_need:
                self.available_stock[order.sku] = available - remaining_need
                return already_allocated + remaining_need
            else:
                # Не хватает для полной отгрузки - возврат предварительного выделения
                if already_allocated > 0:
                    self.available_stock[order.sku] = available + already_allocated
                return 0


import datetime
