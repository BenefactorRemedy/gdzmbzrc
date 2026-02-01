"""
Тестовые сценарии для SC-PRIORITY-DEMO-LITE RU v2.2

A1: Нормальный кейс (нет Q6)
A2: Q6 Simplicity (FIFO)
A3: Q6 Service (Anti-zero)
A4: All-or-nothing (Q3=NO)
B1-B3: WARN сценарии
C1-C4: STOP сценарии
"""

import pytest
from src.parser import parse_input_data
from src.validator import validate_input_data
from src.allocator import StockAllocator
from src.metrics import calculate_metrics
from src.main import run_allocation


class TestScenarioA1:
    """A1: Нормальный кейс - базовое распределение"""
    
    def test_basic_allocation(self):
        """Проверка базового распределения по приоритетам A -> B"""
        q1 = """ORD001|SKU-A|100|A|15.01.2026
ORD002|SKU-A|50|B|-"""
        
        q2 = "SKU-A|150"
        q3 = "YES"
        q4 = "NO"
        q5 = "NO"
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        assert report.status == "OK"
        assert len(report.allocations) == 2
        
        # Проверяем распределение по приоритетам
        alloc_dict = {a.order_id: a for a in report.allocations}
        
        # A-класс должен получить всё запрошенное
        assert alloc_dict['ORD001'].allocated == 100
        assert alloc_dict['ORD001'].status == "OK"
        
        # B-класс получает остаток (150 - 100 = 50)
        assert alloc_dict['ORD002'].allocated == 50
        assert alloc_dict['ORD002'].status == "OK"


class TestScenarioA2:
    """A2: Q6 Simplicity - простое FIFO распределение"""
    
    def test_simplicity_mode(self):
        """Проверка режима Simplicity (Q6=NO) - FIFO без Anti-zero"""
        q1 = """ORD001|SKU-A|100|A|-
ORD002|SKU-A|80|A|-"""
        
        q2 = "SKU-A|120"
        q3 = "YES"
        q4 = "NO"
        q5 = "NO"
        q6 = "NO"  # Simplicity mode
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        assert report.status == "OK"
        alloc_dict = {a.order_id: a for a in report.allocations}
        
        # FIFO: первый заказ получает 100, второй - 20
        assert alloc_dict['ORD001'].allocated == 100
        assert alloc_dict['ORD002'].allocated == 20


class TestScenarioA3:
    """A3: Q6 Service - Anti-zero режим"""
    
    def test_service_anti_zero(self):
        """Проверка режима Service (Q6=YES) - Anti-zero логика"""
        q1 = """ORD001|SKU-A|100|A|-
ORD002|SKU-A|80|A|-"""
        
        q2 = "SKU-A|120"
        q3 = "YES"
        q4 = "NO"
        q5 = "NO"
        q6 = "YES"  # Service mode (Anti-zero)
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        assert report.status == "OK"
        alloc_dict = {a.order_id: a for a in report.allocations}
        
        # Anti-zero: каждый получает по 1, потом остаток по FIFO
        # ORD001: 1 + 99 = 100
        # ORD002: 1 + 19 = 20
        assert alloc_dict['ORD001'].allocated == 100
        assert alloc_dict['ORD002'].allocated == 20


class TestScenarioA4:
    """A4: All-or-nothing режим (Q3=NO)"""
    
    def test_all_or_nothing(self):
        """Проверка режима All-or-nothing (Q3=NO)"""
        q1 = """ORD001|SKU-A|80|A|-
ORD002|SKU-A|50|A|-"""
        
        q2 = "SKU-A|100"
        q3 = "NO"  # All-or-nothing
        q4 = "NO"
        q5 = "NO"
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        assert report.status == "OK"
        alloc_dict = {a.order_id: a for a in report.allocations}
        
        # ORD001 получает 80 (хватает)
        assert alloc_dict['ORD001'].allocated == 80
        
        # ORD002 не получает ничего (остаток 20 < 50)
        assert alloc_dict['ORD002'].allocated == 0


class TestScenarioB_Warnings:
    """B1-B3: WARN сценарии (предупреждения)"""
    
    def test_b1_missing_sku(self):
        """B1: SKU заказа нет в запасах"""
        q1 = "ORD001|SKU-MISSING|100|A|-"
        q2 = "SKU-A|100"
        q3 = "YES"
        q4 = "NO"
        q5 = "NO"
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        assert report.status == "WARN"
        assert any("B1" in w for w in report.warnings)
        assert any("SKU-MISSING" in w for w in report.warnings)
    
    def test_b2_reserved_exceeds_stock(self):
        """B2: Зарезервированное количество > доступного запаса"""
        q1 = "ORD001|SKU-A|50|A|-"
        q2 = "SKU-A|100"
        q3 = "YES"
        q4 = "SKU-A|150"  # Зарезервировано больше чем в наличии
        q5 = "NO"
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        assert report.status == "WARN"
        assert any("B2" in w for w in report.warnings)
    
    def test_b3_class_c_warning(self):
        """B3: Заказы класса C (низкий приоритет)"""
        q1 = "ORD001|SKU-A|50|C|-"
        q2 = "SKU-A|100"
        q3 = "YES"
        q4 = "NO"
        q5 = "NO"
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        assert report.status == "WARN"
        assert any("B3" in w for w in report.warnings)
        assert any("класса C" in w for w in report.warnings)


class TestScenarioC_Stops:
    """C1-C4: STOP сценарии (критические ошибки)"""
    
    def test_c1_duplicate_order_ids(self):
        """C1: Дубликаты ID заказов"""
        q1 = """ORD001|SKU-A|100|A|-
ORD001|SKU-B|50|B|-"""
        
        q2 = "SKU-A|100"
        q3 = "YES"
        q4 = "NO"
        q5 = "NO"
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        assert report.status == "STOP"
        assert any("C1" in e for e in report.errors)
        assert any("Дубликат" in e for e in report.errors)
    
    def test_c2_duplicate_stock_skus(self):
        """C2: Дубликаты SKU в запасах"""
        q1 = "ORD001|SKU-A|100|A|-"
        q2 = """SKU-A|100
SKU-A|50"""
        q3 = "YES"
        q4 = "NO"
        q5 = "NO"
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        assert report.status == "STOP"
        assert any("C2" in e for e in report.errors)
    
    def test_c3_invalid_order_qty(self):
        """C3: QTY заказа <= 0"""
        q1 = "ORD001|SKU-A|0|A|-"
        q2 = "SKU-A|100"
        q3 = "YES"
        q4 = "NO"
        q5 = "NO"
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        assert report.status == "STOP"
        assert any("C3" in e for e in report.errors)
    
    def test_c4_negative_stock_qty(self):
        """C4: QTY запаса < 0"""
        q1 = "ORD001|SKU-A|100|A|-"
        q2 = "SKU-A|-10"
        q3 = "YES"
        q4 = "NO"
        q5 = "NO"
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        assert report.status == "STOP"
        assert any("C4" in e for e in report.errors)


class TestPriorityOrder:
    """Тесты порядка приоритетов A -> B -> C"""
    
    def test_priority_abc(self):
        """Проверка что приоритеты соблюдаются: A -> B -> C"""
        q1 = """ORD001|SKU-A|50|C|-
ORD002|SKU-A|50|A|-
ORD003|SKU-A|50|B|-"""
        
        q2 = "SKU-A|100"
        q3 = "YES"
        q4 = "NO"
        q5 = "NO"
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        alloc_dict = {a.order_id: a for a in report.allocations}
        
        # A получает всё запрошенное
        assert alloc_dict['ORD002'].allocated == 50
        
        # B получает остаток
        assert alloc_dict['ORD003'].allocated == 50
        
        # C не получает ничего
        assert alloc_dict['ORD001'].allocated == 0


class TestDueDateSorting:
    """Тесты сортировки по due_date (Q5)"""
    
    def test_due_date_sorting(self):
        """Q5=YES: Сортировка по due_date"""
        q1 = """ORD001|SKU-A|50|A|20.01.2026
ORD002|SKU-A|50|A|15.01.2026
ORD003|SKU-A|50|A|25.01.2026"""
        
        q2 = "SKU-A|100"
        q3 = "YES"
        q4 = "NO"
        q5 = "YES"  # Sort by due_date
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        alloc_dict = {a.order_id: a for a in report.allocations}
        
        # ORD002 имеет самую раннюю дату - получает первым
        assert alloc_dict['ORD002'].allocated == 50
        
        # ORD001 вторая по дате
        assert alloc_dict['ORD001'].allocated == 50
        
        # ORD003 последняя по дате - не получает
        assert alloc_dict['ORD003'].allocated == 0


class TestReservedStock:
    """Тесты зарезервированных запасов (Q4)"""
    
    def test_reserved_reduces_available(self):
        """Q4: Зарезервированные запасы уменьшают доступное"""
        q1 = "ORD001|SKU-A|100|A|-"
        q2 = "SKU-A|150"
        q3 = "YES"
        q4 = "SKU-A|50"  # Зарезервировано 50
        q5 = "NO"
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        alloc_dict = {a.order_id: a for a in report.allocations}
        
        # Доступно только 100 (150 - 50)
        assert alloc_dict['ORD001'].allocated == 100


class TestMetrics:
    """Тесты расчета метрик"""
    
    def test_fill_rate_calculation(self):
        """Проверка расчета Fill Rate"""
        q1 = """ORD001|SKU-A|100|A|-
ORD002|SKU-A|100|A|-"""
        
        q2 = "SKU-A|150"
        q3 = "YES"
        q4 = "NO"
        q5 = "NO"
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        # Запрошено 200, выделено 150 = 75%
        assert report.fill_rate == 75.0
    
    def test_count_zero(self):
        """Проверка Count Zero"""
        q1 = """ORD001|SKU-A|100|A|-
ORD002|SKU-A|100|A|-"""
        
        q2 = "SKU-A|100"
        q3 = "YES"
        q4 = "NO"
        q5 = "NO"
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        # Один заказ получит 0
        assert report.count_zero == 1
    
    def test_risk_level_green(self):
        """Проверка GREEN уровня риска"""
        q1 = "ORD001|SKU-A|100|A|-"
        q2 = "SKU-A|100"
        q3 = "YES"
        q4 = "NO"
        q5 = "NO"
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        # Fill Rate = 100%, Count Zero = 0
        assert report.risk_level == "GREEN"
    
    def test_risk_level_red(self):
        """Проверка RED уровня риска"""
        q1 = """ORD001|SKU-A|100|A|-
ORD002|SKU-A|100|A|-
ORD003|SKU-A|100|A|-
ORD004|SKU-A|100|A|-"""
        
        q2 = "SKU-A|100"
        q3 = "YES"
        q4 = "NO"
        q5 = "NO"
        q6 = "NO"
        
        report = run_allocation(q1, q2, q3, q4, q5, q6)
        
        # Fill Rate = 25%, Count Zero = 3
        assert report.risk_level == "RED"
