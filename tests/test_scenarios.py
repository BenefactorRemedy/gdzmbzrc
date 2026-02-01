"""
Тестовые сценарии для SC-PRIORITY-DEMO-LITE RU v2.2
"""
import pytest
from datetime import date
from src.models import Order, Stock, InputData
from src.validator import validate_input_data, ValidationError
from src.allocator import Allocator
from src.metrics import calculate_all_metrics


class TestScenarioA1:
    """
    A1: Нормальный кейс без Q6
    - Приоритеты работают (A -> B -> C)
    - Частичные отгрузки разрешены
    - FIFO внутри приоритета
    """
    
    def test_a1_basic_priority(self):
        """Базовый тест приоритетов A -> B -> C"""
        data = InputData(
            orders=[
                Order(id='O1', sku='ITEM-A', qty=50, priority_class='B'),
                Order(id='O2', sku='ITEM-A', qty=30, priority_class='A'),
                Order(id='O3', sku='ITEM-A', qty=20, priority_class='C'),
            ],
            stock=[Stock(sku='ITEM-A', qty=70)],
            partial_allowed=True,
            reserved_stock=[],
            use_due_date=False,
            service_mode=False
        )
        
        allocator = Allocator(data)
        results = allocator.allocate()
        
        # Проверяем порядок обработки: A, B, C
        assert len(results) == 3
        
        # O2 (класс A) получает 30
        result_o2 = next(r for r in results if r.order_id == 'O2')
        assert result_o2.allocated_qty == 30
        
        # O1 (класс B) получает 40 (остаток)
        result_o1 = next(r for r in results if r.order_id == 'O1')
        assert result_o1.allocated_qty == 40
        
        # O3 (класс C) получает 0
        result_o3 = next(r for r in results if r.order_id == 'O3')
        assert result_o3.allocated_qty == 0


class TestScenarioA2:
    """
    A2: Q6 Simplicity (FIFO)
    - Дефицит + конкуренция
    - Режим Simplicity: обычный FIFO
    """
    
    def test_a2_simplicity_mode(self):
        """Тест режима Simplicity при конкуренции"""
        data = InputData(
            orders=[
                Order(id='O1', sku='ITEM-A', qty=30, priority_class='A'),
                Order(id='O2', sku='ITEM-A', qty=30, priority_class='A'),
                Order(id='O3', sku='ITEM-A', qty=30, priority_class='A'),
            ],
            stock=[Stock(sku='ITEM-A', qty=50)],
            partial_allowed=True,
            reserved_stock=[],
            use_due_date=False,
            service_mode=False  # Simplicity
        )
        
        allocator = Allocator(data)
        results = allocator.allocate()
        
        # В режиме Simplicity: FIFO распределение
        # O1 получает 30, O2 получает 20, O3 получает 0
        assert results[0].allocated_qty == 30
        assert results[1].allocated_qty == 20
        assert results[2].allocated_qty == 0


class TestScenarioA3:
    """
    A3: Q6 Service (Anti-zero)
    - Дефицит + конкуренция
    - Режим Service: сначала по 1, потом остаток
    """
    
    def test_a3_service_mode(self):
        """Тест режима Service (Anti-zero)"""
        data = InputData(
            orders=[
                Order(id='O1', sku='ITEM-A', qty=30, priority_class='A'),
                Order(id='O2', sku='ITEM-A', qty=30, priority_class='A'),
                Order(id='O3', sku='ITEM-A', qty=30, priority_class='A'),
            ],
            stock=[Stock(sku='ITEM-A', qty=50)],
            partial_allowed=True,
            reserved_stock=[],
            use_due_date=False,
            service_mode=True  # Service (Anti-zero)
        )
        
        allocator = Allocator(data)
        results = allocator.allocate()
        
        # В режиме Service: каждый получает минимум 1
        # Фаза 1: каждый получает 1 (всего 3)
        # Фаза 2: остаток 47 распределяется по FIFO
        # O1: 1 + 29 = 30
        # O2: 1 + 18 = 19
        # O3: 1 + 0 = 1
        assert results[0].allocated_qty == 30
        assert results[1].allocated_qty == 19
        assert results[2].allocated_qty == 1


class TestScenarioA4:
    """
    A4: All-or-nothing (Q3=NO)
    - Частичные отгрузки запрещены
    """
    
    def test_a4_all_or_nothing(self):
        """Тест режима All-or-nothing"""
        data = InputData(
            orders=[
                Order(id='O1', sku='ITEM-A', qty=30, priority_class='A'),
                Order(id='O2', sku='ITEM-A', qty=60, priority_class='A'),
            ],
            stock=[Stock(sku='ITEM-A', qty=70)],
            partial_allowed=False,  # All-or-nothing
            reserved_stock=[],
            use_due_date=False,
            service_mode=False
        )
        
        allocator = Allocator(data)
        results = allocator.allocate()
        
        # O1 получает 30 (полностью)
        # O2 получает 0 (не хватает на полную отгрузку)
        assert results[0].allocated_qty == 30
        assert results[1].allocated_qty == 0


class TestScenarioB1:
    """
    B1: WARN - SKU отсутствует в остатках
    """
    
    def test_b1_missing_sku_warning(self):
        """Предупреждение об отсутствующем SKU"""
        data = InputData(
            orders=[Order(id='O1', sku='ITEM-X', qty=10, priority_class='A')],
            stock=[Stock(sku='ITEM-A', qty=100)],
            partial_allowed=True,
            reserved_stock=[],
            use_due_date=False,
            service_mode=False
        )
        
        errors, warnings = validate_input_data(data)
        
        assert len(errors) == 0
        assert len(warnings) == 1
        assert 'ITEM-X' in warnings[0]
        assert 'отсутствует в остатках' in warnings[0]


class TestScenarioB2:
    """
    B2: WARN - Резерв превышает остаток
    """
    
    def test_b2_reserved_exceeds_stock(self):
        """Предупреждение о превышении резерва"""
        data = InputData(
            orders=[],
            stock=[Stock(sku='ITEM-A', qty=50)],
            partial_allowed=True,
            reserved_stock=[Stock(sku='ITEM-A', qty=60)],
            use_due_date=False,
            service_mode=False
        )
        
        errors, warnings = validate_input_data(data)
        
        assert len(errors) == 0
        assert len(warnings) == 1
        assert 'превышает остаток' in warnings[0]


class TestScenarioC1:
    """
    C1: STOP - Дублирующиеся ID заказов
    """
    
    def test_c1_duplicate_order_ids(self):
        """Критическая ошибка: дубли в ID заказов"""
        data = InputData(
            orders=[
                Order(id='O1', sku='ITEM-A', qty=10, priority_class='A'),
                Order(id='O1', sku='ITEM-B', qty=20, priority_class='B'),
            ],
            stock=[Stock(sku='ITEM-A', qty=100)],
            partial_allowed=True,
            reserved_stock=[],
            use_due_date=False,
            service_mode=False
        )
        
        errors, warnings = validate_input_data(data)
        
        assert len(errors) == 1
        assert 'STOP' in errors[0]
        assert 'дублирующиеся ID' in errors[0]


class TestScenarioC2:
    """
    C2: STOP - Qty <= 0 в заказе
    """
    
    def test_c2_invalid_order_qty(self):
        """Критическая ошибка: недопустимое количество"""
        data = InputData(
            orders=[Order(id='O1', sku='ITEM-A', qty=0, priority_class='A')],
            stock=[Stock(sku='ITEM-A', qty=100)],
            partial_allowed=True,
            reserved_stock=[],
            use_due_date=False,
            service_mode=False
        )
        
        errors, warnings = validate_input_data(data)
        
        assert len(errors) == 1
        assert 'STOP' in errors[0]
        assert 'недопустимое количество' in errors[0]


class TestScenarioC3:
    """
    C3: STOP - Отрицательный остаток
    """
    
    def test_c3_negative_stock(self):
        """Критическая ошибка: отрицательный остаток"""
        data = InputData(
            orders=[],
            stock=[Stock(sku='ITEM-A', qty=-10)],
            partial_allowed=True,
            reserved_stock=[],
            use_due_date=False,
            service_mode=False
        )
        
        errors, warnings = validate_input_data(data)
        
        assert len(errors) == 1
        assert 'STOP' in errors[0]
        assert 'отрицательный остаток' in errors[0]


class TestScenarioC4:
    """
    C4: STOP - Дублирующиеся SKU в остатках
    """
    
    def test_c4_duplicate_stock_skus(self):
        """Критическая ошибка: дубли SKU в остатках"""
        data = InputData(
            orders=[],
            stock=[
                Stock(sku='ITEM-A', qty=50),
                Stock(sku='ITEM-A', qty=30),
            ],
            partial_allowed=True,
            reserved_stock=[],
            use_due_date=False,
            service_mode=False
        )
        
        errors, warnings = validate_input_data(data)
        
        assert len(errors) == 1
        assert 'STOP' in errors[0]
        assert 'дублирующиеся SKU' in errors[0]


class TestDueDateSorting:
    """
    Тесты сортировки по Due Date (Q5)
    """
    
    def test_due_date_sorting(self):
        """Заказы сортируются по Due Date"""
        data = InputData(
            orders=[
                Order(id='O1', sku='ITEM-A', qty=30, priority_class='A', 
                      due_date=date(2024, 12, 31)),
                Order(id='O2', sku='ITEM-A', qty=30, priority_class='A',
                      due_date=date(2024, 12, 15)),
                Order(id='O3', sku='ITEM-A', qty=30, priority_class='A',
                      due_date=date(2024, 12, 20)),
            ],
            stock=[Stock(sku='ITEM-A', qty=50)],
            partial_allowed=True,
            reserved_stock=[],
            use_due_date=True,  # Включаем сортировку по Due Date
            service_mode=False
        )
        
        allocator = Allocator(data)
        results = allocator.allocate()
        
        # O2 (15 декабря) обрабатывается первым
        # O3 (20 декабря) вторым
        # O1 (31 декабря) третьим
        result_o2 = next(r for r in results if r.order_id == 'O2')
        result_o3 = next(r for r in results if r.order_id == 'O3')
        result_o1 = next(r for r in results if r.order_id == 'O1')
        
        assert result_o2.allocated_qty == 30
        assert result_o3.allocated_qty == 20
        assert result_o1.allocated_qty == 0


class TestReservedStock:
    """
    Тесты учета зарезервированных остатков (Q4)
    """
    
    def test_reserved_reduces_available(self):
        """Резерв уменьшает доступный остаток"""
        data = InputData(
            orders=[Order(id='O1', sku='ITEM-A', qty=100, priority_class='A')],
            stock=[Stock(sku='ITEM-A', qty=100)],
            partial_allowed=True,
            reserved_stock=[Stock(sku='ITEM-A', qty=30)],  # 30 зарезервировано
            use_due_date=False,
            service_mode=False
        )
        
        allocator = Allocator(data)
        results = allocator.allocate()
        
        # Доступно только 70 (100 - 30)
        assert results[0].allocated_qty == 70


class TestMetrics:
    """
    Тесты расчета метрик
    """
    
    def test_fill_rate_calculation(self):
        """Расчет Fill Rate"""
        from src.models import AllocationResult
        
        results = [
            AllocationResult('O1', 'ITEM-A', 10, 10, 'A'),  # Выполнен
            AllocationResult('O2', 'ITEM-A', 10, 5, 'A'),   # Частично
            AllocationResult('O3', 'ITEM-A', 10, 0, 'A'),   # Ноль
        ]
        
        metrics = calculate_all_metrics(results)
        
        assert metrics['fill_rate'] == pytest.approx(33.33, rel=0.1)
        assert metrics['count_zero'] == 1
        assert metrics['total_orders'] == 3
    
    def test_risk_level_green(self):
        """Уровень риска: Green"""
        from src.models import AllocationResult
        
        results = [
            AllocationResult('O1', 'ITEM-A', 10, 10, 'A'),
            AllocationResult('O2', 'ITEM-A', 10, 10, 'A'),
        ]
        
        metrics = calculate_all_metrics(results)
        assert metrics['risk_level'] == 'Green'
    
    def test_risk_level_red(self):
        """Уровень риска: Red"""
        from src.models import AllocationResult
        
        results = [
            AllocationResult('O1', 'ITEM-A', 10, 5, 'A'),
            AllocationResult('O2', 'ITEM-A', 10, 0, 'A'),
        ]
        
        metrics = calculate_all_metrics(results)
        assert metrics['risk_level'] == 'Red'
    
    def test_risk_level_yellow(self):
        """Уровень риска: Yellow"""
        from src.models import AllocationResult
        
        # Yellow: Fill Rate между 70-90% и Count Zero = 0
        results = [
            AllocationResult('O1', 'ITEM-A', 10, 10, 'A'),
            AllocationResult('O2', 'ITEM-A', 10, 10, 'A'),
            AllocationResult('O3', 'ITEM-A', 10, 10, 'A'),
            AllocationResult('O4', 'ITEM-A', 10, 10, 'A'),
            AllocationResult('O5', 'ITEM-A', 10, 5, 'A'),  # Частично
        ]
        
        metrics = calculate_all_metrics(results)
        # Fill Rate = 80% (4 из 5), Count Zero = 0
        assert metrics['risk_level'] == 'Yellow'
