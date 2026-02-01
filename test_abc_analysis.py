"""
Тесты для модуля ABC анализа
"""

import unittest
from abc_analysis import (
    Product, ABCCategory, ABCAnalyzer, ABCAnalysisResult,
    SupplyChainABCRequest
)


class TestProduct(unittest.TestCase):
    """Тесты для класса Product"""
    
    def test_product_creation(self):
        """Тест создания товара"""
        product = Product("SKU001", "Test Product", 100, 10.0)
        self.assertEqual(product.sku, "SKU001")
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.quantity, 100)
        self.assertEqual(product.unit_price, 10.0)
    
    def test_total_value_calculation(self):
        """Тест вычисления общей стоимости"""
        product = Product("SKU001", "Test Product", 100, 10.0)
        self.assertEqual(product.total_value, 1000.0)
        
        product2 = Product("SKU002", "Another Product", 50, 20.5)
        self.assertEqual(product2.total_value, 1025.0)


class TestABCAnalyzer(unittest.TestCase):
    """Тесты для класса ABCAnalyzer"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.analyzer = ABCAnalyzer()
        self.test_products = [
            Product("SKU001", "High Value Item", 10, 1000.0),  # 10000
            Product("SKU002", "Medium Value Item", 50, 100.0),  # 5000
            Product("SKU003", "Low Value Item", 1000, 2.0),  # 2000
            Product("SKU004", "Very Low Value Item", 500, 1.0),  # 500
        ]
    
    def test_analyze_empty_list(self):
        """Тест анализа пустого списка"""
        results = self.analyzer.analyze([])
        self.assertEqual(len(results), 0)
    
    def test_analyze_single_product(self):
        """Тест анализа одного товара"""
        products = [Product("SKU001", "Single Item", 10, 100.0)]
        results = self.analyzer.analyze(products)
        
        self.assertEqual(len(results), 1)
        # Single product gets 100% cumulative, which exceeds A threshold (80)
        # but should still be categorized based on business logic
        self.assertEqual(results[0].cumulative_percentage, 100.0)
    
    def test_analyze_sorting(self):
        """Тест сортировки по стоимости"""
        results = self.analyzer.analyze(self.test_products)
        
        # Проверка, что результаты отсортированы по убыванию стоимости
        for i in range(len(results) - 1):
            self.assertGreaterEqual(results[i].total_value, results[i + 1].total_value)
    
    def test_analyze_categories(self):
        """Тест правильности категоризации"""
        results = self.analyzer.analyze(self.test_products)
        
        # Первый товар (10000) должен быть в категории A
        self.assertEqual(results[0].category, ABCCategory.A)
        
        # Проверка накопительных процентов
        self.assertLess(results[0].cumulative_percentage, 100.0)
        self.assertEqual(results[-1].cumulative_percentage, 100.0)
    
    def test_custom_thresholds(self):
        """Тест с пользовательскими порогами"""
        analyzer = ABCAnalyzer(category_a_threshold=60.0, category_b_threshold=90.0)
        results = analyzer.analyze(self.test_products)
        
        # С более низким порогом, больше товаров может быть в категории A
        a_items = [r for r in results if r.category == ABCCategory.A]
        self.assertGreater(len(a_items), 0)
    
    def test_get_category_summary(self):
        """Тест получения сводной статистики"""
        results = self.analyzer.analyze(self.test_products)
        summary = self.analyzer.get_category_summary(results)
        
        # Проверка структуры сводки
        self.assertIn('A', summary)
        self.assertIn('B', summary)
        self.assertIn('C', summary)
        
        # Проверка, что все товары учтены
        total_count = sum(summary[cat]['count'] for cat in ['A', 'B', 'C'])
        self.assertEqual(total_count, len(self.test_products))
        
        # Проверка, что проценты сходятся
        total_percentage = sum(summary[cat]['percentage_of_items'] for cat in ['A', 'B', 'C'])
        self.assertAlmostEqual(total_percentage, 100.0, places=1)
    
    def test_category_summary_values(self):
        """Тест корректности значений в сводной статистике"""
        results = self.analyzer.analyze(self.test_products)
        summary = self.analyzer.get_category_summary(results)
        
        # Проверка общей стоимости
        total_value = sum(p.total_value for p in self.test_products)
        summary_total = sum(summary[cat]['total_value'] for cat in ['A', 'B', 'C'])
        self.assertAlmostEqual(summary_total, total_value, places=2)


class TestSupplyChainABCRequest(unittest.TestCase):
    """Тесты для класса SupplyChainABCRequest"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.request_handler = SupplyChainABCRequest()
        self.test_products = [
            Product("SKU001", "Product A", 100, 50.0),
            Product("SKU002", "Product B", 200, 25.0),
            Product("SKU003", "Product C", 300, 10.0),
        ]
    
    def test_process_inventory_analysis(self):
        """Тест обработки запроса на анализ инвентаря"""
        report = self.request_handler.process_inventory_analysis(self.test_products)
        
        # Проверка структуры отчета
        self.assertIn('status', report)
        self.assertIn('total_products', report)
        self.assertIn('results', report)
        self.assertIn('summary', report)
        self.assertIn('recommendations', report)
        
        # Проверка статуса
        self.assertEqual(report['status'], 'success')
        
        # Проверка количества товаров
        self.assertEqual(report['total_products'], len(self.test_products))
        
        # Проверка наличия результатов
        self.assertEqual(len(report['results']), len(self.test_products))
    
    def test_filter_by_category(self):
        """Тест фильтрации по категории"""
        results = self.request_handler.analyzer.analyze(self.test_products)
        
        # Фильтрация категории A
        a_items = self.request_handler.filter_by_category(results, ABCCategory.A)
        
        # Проверка, что все отфильтрованные товары имеют правильную категорию
        for item in a_items:
            self.assertEqual(item.category, ABCCategory.A)
        
        # Фильтрация категории B
        b_items = self.request_handler.filter_by_category(results, ABCCategory.B)
        for item in b_items:
            self.assertEqual(item.category, ABCCategory.B)
        
        # Фильтрация категории C
        c_items = self.request_handler.filter_by_category(results, ABCCategory.C)
        for item in c_items:
            self.assertEqual(item.category, ABCCategory.C)
    
    def test_get_top_products(self):
        """Тест получения топ товаров"""
        results = self.request_handler.analyzer.analyze(self.test_products)
        
        # Получение топ 2 товаров
        top_2 = self.request_handler.get_top_products(results, n=2)
        
        self.assertEqual(len(top_2), 2)
        
        # Проверка, что топ товары отсортированы по стоимости
        self.assertGreaterEqual(top_2[0].total_value, top_2[1].total_value)
    
    def test_recommendations_generation(self):
        """Тест генерации рекомендаций"""
        report = self.request_handler.process_inventory_analysis(self.test_products)
        
        # Проверка наличия рекомендаций
        self.assertGreater(len(report['recommendations']), 0)
        
        # Проверка, что рекомендации - это строки
        for recommendation in report['recommendations']:
            self.assertIsInstance(recommendation, str)
            self.assertGreater(len(recommendation), 0)


class TestABCAnalysisResult(unittest.TestCase):
    """Тесты для класса ABCAnalysisResult"""
    
    def test_result_creation(self):
        """Тест создания результата анализа"""
        result = ABCAnalysisResult(
            sku="SKU001",
            name="Test Product",
            quantity=100,
            unit_price=10.0,
            total_value=1000.0,
            cumulative_percentage=50.0,
            category=ABCCategory.A
        )
        
        self.assertEqual(result.sku, "SKU001")
        self.assertEqual(result.category, ABCCategory.A)
        self.assertEqual(result.total_value, 1000.0)
    
    def test_result_string_representation(self):
        """Тест строкового представления результата"""
        result = ABCAnalysisResult(
            sku="SKU001",
            name="Test Product",
            quantity=100,
            unit_price=10.0,
            total_value=1000.0,
            cumulative_percentage=50.0,
            category=ABCCategory.A
        )
        
        result_str = str(result)
        
        # Проверка, что в строке есть основная информация
        self.assertIn("SKU001", result_str)
        self.assertIn("Test Product", result_str)
        self.assertIn("A", result_str)


class TestABCCategoryEnum(unittest.TestCase):
    """Тесты для enum ABCCategory"""
    
    def test_category_values(self):
        """Тест значений категорий"""
        self.assertEqual(ABCCategory.A.value, "A")
        self.assertEqual(ABCCategory.B.value, "B")
        self.assertEqual(ABCCategory.C.value, "C")
    
    def test_category_comparison(self):
        """Тест сравнения категорий"""
        self.assertEqual(ABCCategory.A, ABCCategory.A)
        self.assertNotEqual(ABCCategory.A, ABCCategory.B)


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""
    
    def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        # Создание товаров
        # Total values: Premium=50000, Standard=40000, Budget=30000, Mouse=10000, USB=5000
        products = [
            Product("SKU001", "Premium Laptop", 25, 2000.0),  # 50,000
            Product("SKU002", "Standard Laptop", 40, 1000.0),  # 40,000
            Product("SKU003", "Budget Laptop", 60, 500.0),     # 30,000
            Product("SKU004", "Mouse", 500, 20.0),             # 10,000
            Product("SKU005", "USB Cable", 1000, 5.0),         # 5,000
        ]
        
        # Создание обработчика запросов
        handler = SupplyChainABCRequest()
        
        # Выполнение анализа
        report = handler.process_inventory_analysis(products)
        
        # Проверка успешности
        self.assertEqual(report['status'], 'success')
        
        # Проверка результатов
        self.assertEqual(len(report['results']), 5)
        
        # Получение топ товаров
        top_3 = handler.get_top_products(report['results'], n=3)
        self.assertEqual(len(top_3), 3)
        
        # Проверка, что самый дорогой товар - Premium Laptop
        self.assertEqual(top_3[0].name, "Premium Laptop")
        
        # Фильтрация категории A
        a_items = handler.filter_by_category(report['results'], ABCCategory.A)
        
        # Premium Laptop должен быть в категории A
        a_skus = [item.sku for item in a_items]
        self.assertIn("SKU001", a_skus)


if __name__ == '__main__':
    unittest.main()
