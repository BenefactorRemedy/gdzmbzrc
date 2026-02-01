"""Ядро распределения запасов по заказам с приоритетами"""

from typing import List, Dict
from collections import defaultdict
from src.models import InputData, Order, AllocationResult


class StockAllocator:
    """Распределитель запасов"""
    
    def __init__(self, data: InputData):
        self.data = data
        self.available_stock = self._calculate_available_stock()
        self.allocations: List[AllocationResult] = []
    
    def _calculate_available_stock(self) -> Dict[str, int]:
        """
        Вычисляет доступный запас: available = stock - reserved
        """
        available = {}
        
        # Заполняем начальными значениями из запасов
        for stock in self.data.stock:
            available[stock.sku] = stock.qty
        
        # Вычитаем зарезервированные количества
        for sku, reserved_qty in self.data.q4_reserved:
            if sku in available:
                available[sku] -= reserved_qty
                # Доступное не может быть отрицательным
                if available[sku] < 0:
                    available[sku] = 0
        
        return available
    
    def _sort_orders(self, orders: List[Order]) -> List[Order]:
        """
        Сортировка заказов согласно Q5
        
        Q5 = YES: Сортировка по due_date (раньше = выше приоритет)
        Q5 = NO: FIFO (в порядке поступления)
        """
        if not self.data.q5_use_due_date:
            # FIFO - оставляем в исходном порядке
            return orders
        
        # Сортируем по due_date
        # Заказы без даты идут в конец
        def sort_key(order):
            if order.due_date is None:
                # Используем очень далекую дату для заказов без срока
                from datetime import date
                return date(9999, 12, 31)
            return order.due_date
        
        return sorted(orders, key=sort_key)
    
    def _allocate_to_order(self, order: Order, available: int) -> int:
        """
        Выделяет запас заказу согласно Q3
        
        Q3 = YES (Partial): Можно выделить частично
        Q3 = NO (All-or-nothing): Только если хватает на весь заказ
        
        Returns: Выделенное количество
        """
        if self.data.q3_partial:
            # Partial allocation - выделяем сколько есть
            return min(order.qty, available)
        else:
            # All-or-nothing - только если хватает на весь заказ
            if available >= order.qty:
                return order.qty
            else:
                return 0
    
    def _apply_service_mode(self, orders_by_sku: Dict[str, List[Order]]) -> None:
        """
        Q6 Service Mode (Anti-zero): 
        
        Если есть дефицит и конкуренция между заказами одного SKU:
        1. Сначала раздать по 1 шт каждому заказу (чтобы никто не получил 0)
        2. Остаток распределить по FIFO
        
        Применяется только к заказам одного класса приоритета на одном SKU
        """
        for sku, orders in orders_by_sku.items():
            available = self.available_stock.get(sku, 0)
            
            if available <= 0 or len(orders) <= 1:
                continue
            
            total_requested = sum(o.qty for o in orders)
            
            # Проверяем дефицит и конкуренцию
            if total_requested <= available:
                # Нет дефицита - обычное распределение
                continue
            
            # Есть дефицит и конкуренция
            # Раздаем по 1 шт каждому
            for order in orders:
                if available > 0 and order.qty > 0:
                    allocation = min(1, order.qty, available)
                    order.allocated += allocation
                    available -= allocation
            
            # Остаток распределяем по FIFO
            for order in orders:
                if available <= 0:
                    break
                
                remaining_need = order.qty - order.allocated
                if remaining_need > 0:
                    allocation = min(remaining_need, available)
                    order.allocated += allocation
                    available -= allocation
            
            # Обновляем доступный запас
            self.available_stock[sku] = available
    
    def _allocate_by_priority_class(self, order_class: str) -> None:
        """
        Распределяет запас для заказов указанного класса приоритета
        """
        # Фильтруем заказы по классу
        class_orders = [o for o in self.data.orders if o.order_class == order_class]
        
        if not class_orders:
            return
        
        # Сортируем согласно Q5
        sorted_orders = self._sort_orders(class_orders)
        
        # Q6: Service mode
        if self.data.q6_service_mode:
            # Группируем заказы по SKU для применения Anti-zero логики
            orders_by_sku = defaultdict(list)
            for order in sorted_orders:
                orders_by_sku[order.sku].append(order)
            
            self._apply_service_mode(orders_by_sku)
        else:
            # Simplicity mode - обычное FIFO распределение
            for order in sorted_orders:
                sku = order.sku
                available = self.available_stock.get(sku, 0)
                
                # Выделяем согласно Q3
                allocated = self._allocate_to_order(order, available)
                order.allocated = allocated
                
                # Уменьшаем доступный запас
                self.available_stock[sku] = available - allocated
    
    def allocate(self) -> List[AllocationResult]:
        """
        Основной метод распределения
        
        Приоритеты: A -> B -> C
        """
        # Распределяем по приоритетам
        for priority_class in ['A', 'B', 'C']:
            self._allocate_by_priority_class(priority_class)
        
        # Формируем результаты
        results = []
        for order in self.data.orders:
            status = self._determine_status(order)
            
            result = AllocationResult(
                order_id=order.id,
                sku=order.sku,
                requested=order.qty,
                allocated=order.allocated,
                status=status
            )
            results.append(result)
        
        self.allocations = results
        return results
    
    def _determine_status(self, order: Order) -> str:
        """Определяет статус заказа"""
        if order.allocated == 0:
            return "ZERO"
        elif order.allocated < order.qty:
            return "PARTIAL"
        else:
            return "OK"
