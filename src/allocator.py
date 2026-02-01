"""
Ядро распределения товаров по заказам с приоритетами A → B → C
"""
from typing import List, Dict
from collections import defaultdict
from src.models import InputData, Order, Stock, AllocationResult


class Allocator:
    """Распределитель товаров по заказам"""
    
    def __init__(self, data: InputData):
        self.data = data
        self.available_stock = self._calculate_available_stock()
        self.results: List[AllocationResult] = []
    
    def _calculate_available_stock(self) -> Dict[str, int]:
        """
        Вычисление доступных остатков: available = stock - reserved
        """
        # Создаем словарь остатков
        stock_dict = {stock.sku: stock.qty for stock in self.data.stock}
        
        # Вычитаем резервы
        for reserved in self.data.reserved_stock:
            if reserved.sku in stock_dict:
                stock_dict[reserved.sku] = max(0, stock_dict[reserved.sku] - reserved.qty)
        
        return stock_dict
    
    def allocate(self) -> List[AllocationResult]:
        """
        Основная функция распределения с приоритетами A → B → C
        """
        # Сортируем заказы по приоритету (A, B, C)
        priority_order = {'A': 0, 'B': 1, 'C': 2}
        
        # Группируем заказы по приоритету
        orders_by_priority = {'A': [], 'B': [], 'C': []}
        for order in self.data.orders:
            orders_by_priority[order.priority_class].append(order)
        
        # Обрабатываем каждый приоритет последовательно
        for priority in ['A', 'B', 'C']:
            orders = orders_by_priority[priority]
            
            # Сортируем заказы внутри приоритета
            sorted_orders = self._sort_orders_within_priority(orders)
            
            # Распределяем товары
            self._allocate_orders(sorted_orders)
        
        return self.results
    
    def _sort_orders_within_priority(self, orders: List[Order]) -> List[Order]:
        """
        Сортировка заказов внутри одного приоритета
        """
        if self.data.use_due_date:
            # Сортировка по Due Date (раньше = выше приоритет)
            # Заказы без Due Date идут в конец
            return sorted(orders, key=lambda o: (
                o.due_date is None,
                o.due_date if o.due_date else None
            ))
        else:
            # FIFO - сохраняем исходный порядок
            return orders
    
    def _allocate_orders(self, orders: List[Order]) -> None:
        """
        Распределение товаров для списка заказов одного приоритета
        """
        # Группируем заказы по SKU для обнаружения конкуренции
        orders_by_sku = defaultdict(list)
        for order in orders:
            orders_by_sku[order.sku].append(order)
        
        # Обрабатываем каждую группу SKU отдельно
        for sku, sku_orders in orders_by_sku.items():
            self._allocate_sku_orders(sku, sku_orders)
    
    def _allocate_sku_orders(self, sku: str, orders: List[Order]) -> None:
        """
        Распределение товаров для заказов на один SKU
        """
        available = self.available_stock.get(sku, 0)
        total_demand = sum(order.qty for order in orders)
        
        # Проверяем наличие дефицита и конкуренции
        has_shortage = total_demand > available
        has_competition = len(orders) > 1
        
        # Режим Service (Anti-zero): если дефицит и конкуренция
        if self.data.service_mode and has_shortage and has_competition:
            self._allocate_service_mode(sku, orders, available)
        else:
            # Режим Simplicity или нет конкуренции: обычный FIFO
            self._allocate_fifo_mode(sku, orders, available)
    
    def _allocate_service_mode(self, sku: str, orders: List[Order], available: int) -> None:
        """
        Режим Service (Anti-zero):
        1. Раздать каждому заказу по 1 единице (если возможно)
        2. Оставшееся распределить по FIFO
        """
        # Фаза 1: Раздать по 1 единице каждому
        for order in orders:
            if available > 0:
                allocated = 1
                available -= 1
            else:
                allocated = 0
            
            result = AllocationResult(
                order_id=order.id,
                sku=order.sku,
                requested_qty=order.qty,
                allocated_qty=allocated,
                priority_class=order.priority_class
            )
            self.results.append(result)
        
        # Фаза 2: Распределить остаток по FIFO
        if available > 0:
            for i, order in enumerate(orders):
                # Уже выделено 1, можем добавить еще
                can_add = min(order.qty - self.results[-(len(orders) - i)].allocated_qty, available)
                if can_add > 0:
                    self.results[-(len(orders) - i)].allocated_qty += can_add
                    available -= can_add
        
        # Обновляем общий доступный остаток
        self.available_stock[sku] = available
    
    def _allocate_fifo_mode(self, sku: str, orders: List[Order], available: int) -> None:
        """
        Режим Simplicity: распределение по FIFO
        """
        for order in orders:
            if available <= 0:
                allocated = 0
            else:
                if self.data.partial_allowed:
                    # Частичная отгрузка разрешена
                    allocated = min(order.qty, available)
                else:
                    # All-or-nothing: либо полностью, либо 0
                    if available >= order.qty:
                        allocated = order.qty
                    else:
                        allocated = 0
                
                available -= allocated
            
            result = AllocationResult(
                order_id=order.id,
                sku=order.sku,
                requested_qty=order.qty,
                allocated_qty=allocated,
                priority_class=order.priority_class
            )
            self.results.append(result)
        
        # Обновляем общий доступный остаток
        self.available_stock[sku] = available
