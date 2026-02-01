"""
Модуль ABC анализа для Supply Chain Management

ABC анализ - это метод классификации товаров/запасов на основе их важности:
- Категория A: Высокая стоимость, низкое количество (20% товаров = 80% стоимости)
- Категория B: Средняя стоимость, среднее количество (30% товаров = 15% стоимости)
- Категория C: Низкая стоимость, высокое количество (50% товаров = 5% стоимости)
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class ABCCategory(Enum):
    """Категории ABC классификации"""
    A = "A"
    B = "B"
    C = "C"


@dataclass
class Product:
    """Класс для представления товара"""
    sku: str  # Артикул товара
    name: str  # Название товара
    quantity: int  # Количество на складе
    unit_price: float  # Цена за единицу
    
    @property
    def total_value(self) -> float:
        """Общая стоимость товара на складе"""
        return self.quantity * self.unit_price


@dataclass
class ABCAnalysisResult:
    """Результат ABC анализа"""
    sku: str
    name: str
    quantity: int
    unit_price: float
    total_value: float
    cumulative_percentage: float
    category: ABCCategory
    
    def __str__(self):
        return (f"[{self.category.value}] {self.sku} - {self.name}: "
                f"Кол-во: {self.quantity}, Цена: {self.unit_price:.2f}, "
                f"Стоимость: {self.total_value:.2f}, "
                f"Накоп. %: {self.cumulative_percentage:.2f}%")


class ABCAnalyzer:
    """Класс для выполнения ABC анализа"""
    
    def __init__(self, category_a_threshold: float = 80.0, 
                 category_b_threshold: float = 95.0):
        """
        Инициализация анализатора
        
        Args:
            category_a_threshold: Порог для категории A (по умолчанию 80%)
            category_b_threshold: Порог для категории B (по умолчанию 95%)
        """
        self.category_a_threshold = category_a_threshold
        self.category_b_threshold = category_b_threshold
    
    def analyze(self, products: List[Product]) -> List[ABCAnalysisResult]:
        """
        Выполнить ABC анализ для списка товаров
        
        Args:
            products: Список товаров для анализа
            
        Returns:
            Список результатов ABC анализа, отсортированный по стоимости
        """
        if not products:
            return []
        
        # Сортировка товаров по общей стоимости (от большей к меньшей)
        sorted_products = sorted(products, 
                                key=lambda p: p.total_value, 
                                reverse=True)
        
        # Вычисление общей стоимости всех товаров
        total_value = sum(p.total_value for p in sorted_products)
        
        # Создание результатов с накопительными процентами
        results = []
        cumulative_value = 0.0
        
        for product in sorted_products:
            cumulative_value += product.total_value
            cumulative_percentage = (cumulative_value / total_value) * 100
            
            # Определение категории
            if cumulative_percentage <= self.category_a_threshold:
                category = ABCCategory.A
            elif cumulative_percentage <= self.category_b_threshold:
                category = ABCCategory.B
            else:
                category = ABCCategory.C
            
            result = ABCAnalysisResult(
                sku=product.sku,
                name=product.name,
                quantity=product.quantity,
                unit_price=product.unit_price,
                total_value=product.total_value,
                cumulative_percentage=cumulative_percentage,
                category=category
            )
            results.append(result)
        
        return results
    
    def get_category_summary(self, results: List[ABCAnalysisResult]) -> Dict[str, Dict]:
        """
        Получить сводную статистику по категориям
        
        Args:
            results: Результаты ABC анализа
            
        Returns:
            Словарь со статистикой по каждой категории
        """
        summary = {
            'A': {'count': 0, 'total_value': 0.0, 'items': []},
            'B': {'count': 0, 'total_value': 0.0, 'items': []},
            'C': {'count': 0, 'total_value': 0.0, 'items': []}
        }
        
        for result in results:
            cat = result.category.value
            summary[cat]['count'] += 1
            summary[cat]['total_value'] += result.total_value
            summary[cat]['items'].append(result.sku)
        
        # Добавление процентов
        total_items = len(results)
        total_value = sum(r.total_value for r in results)
        
        for cat in summary:
            if total_items > 0:
                summary[cat]['percentage_of_items'] = (summary[cat]['count'] / total_items) * 100
            else:
                summary[cat]['percentage_of_items'] = 0.0
            
            if total_value > 0:
                summary[cat]['percentage_of_value'] = (summary[cat]['total_value'] / total_value) * 100
            else:
                summary[cat]['percentage_of_value'] = 0.0
        
        return summary


class SupplyChainABCRequest:
    """Класс для обработки запросов по ABC анализу"""
    
    def __init__(self):
        self.analyzer = ABCAnalyzer()
    
    def process_inventory_analysis(self, products: List[Product]) -> Dict:
        """
        Обработка запроса на анализ инвентаря
        
        Args:
            products: Список товаров
            
        Returns:
            Полный отчет с результатами и статистикой
        """
        results = self.analyzer.analyze(products)
        summary = self.analyzer.get_category_summary(results)
        
        return {
            'status': 'success',
            'total_products': len(products),
            'results': results,
            'summary': summary,
            'recommendations': self._generate_recommendations(summary)
        }
    
    def filter_by_category(self, results: List[ABCAnalysisResult], 
                          category: ABCCategory) -> List[ABCAnalysisResult]:
        """
        Фильтрация результатов по категории
        
        Args:
            results: Результаты ABC анализа
            category: Категория для фильтрации
            
        Returns:
            Отфильтрованный список результатов
        """
        return [r for r in results if r.category == category]
    
    def get_top_products(self, results: List[ABCAnalysisResult], 
                        n: int = 10) -> List[ABCAnalysisResult]:
        """
        Получить топ N товаров по стоимости
        
        Args:
            results: Результаты ABC анализа
            n: Количество товаров
            
        Returns:
            Список топ N товаров
        """
        return results[:n]
    
    def _generate_recommendations(self, summary: Dict) -> List[str]:
        """
        Генерация рекомендаций на основе ABC анализа
        
        Args:
            summary: Сводная статистика
            
        Returns:
            Список рекомендаций
        """
        recommendations = []
        
        # Рекомендации для категории A
        if summary['A']['count'] > 0:
            recommendations.append(
                f"Категория A ({summary['A']['count']} товаров, "
                f"{summary['A']['percentage_of_value']:.1f}% стоимости): "
                "Требует максимального контроля, точного планирования заказов, "
                "регулярного мониторинга уровня запасов."
            )
        
        # Рекомендации для категории B
        if summary['B']['count'] > 0:
            recommendations.append(
                f"Категория B ({summary['B']['count']} товаров, "
                f"{summary['B']['percentage_of_value']:.1f}% стоимости): "
                "Требует умеренного контроля, стандартных процедур заказа."
            )
        
        # Рекомендации для категории C
        if summary['C']['count'] > 0:
            recommendations.append(
                f"Категория C ({summary['C']['count']} товаров, "
                f"{summary['C']['percentage_of_value']:.1f}% стоимости): "
                "Можно использовать упрощенные процедуры заказа, "
                "увеличенные партии поставок."
            )
        
        return recommendations


def main():
    """Пример использования модуля ABC анализа"""
    
    # Создание примера данных
    sample_products = [
        Product("SKU001", "Компьютер Dell XPS", 50, 1500.0),
        Product("SKU002", "Монитор Samsung", 120, 300.0),
        Product("SKU003", "Клавиатура Logitech", 500, 50.0),
        Product("SKU004", "Мышь беспроводная", 800, 25.0),
        Product("SKU005", "USB кабель", 2000, 5.0),
        Product("SKU006", "Наушники Sony", 200, 150.0),
        Product("SKU007", "Веб-камера", 100, 80.0),
        Product("SKU008", "Принтер HP LaserJet", 30, 500.0),
        Product("SKU009", "Картриджи для принтера", 150, 60.0),
        Product("SKU010", "Бумага A4 (пачка)", 1000, 3.0),
    ]
    
    # Создание обработчика запросов
    request_handler = SupplyChainABCRequest()
    
    # Обработка запроса на анализ
    print("=" * 80)
    print("ABC АНАЛИЗ ИНВЕНТАРЯ SUPPLY CHAIN")
    print("=" * 80)
    
    report = request_handler.process_inventory_analysis(sample_products)
    
    print(f"\nВсего товаров: {report['total_products']}")
    print("\nРЕЗУЛЬТАТЫ ABC АНАЛИЗА:")
    print("-" * 80)
    
    for result in report['results']:
        print(result)
    
    print("\n" + "=" * 80)
    print("СВОДНАЯ СТАТИСТИКА ПО КАТЕГОРИЯМ")
    print("=" * 80)
    
    for category in ['A', 'B', 'C']:
        stats = report['summary'][category]
        print(f"\nКатегория {category}:")
        print(f"  Количество товаров: {stats['count']} ({stats['percentage_of_items']:.1f}%)")
        print(f"  Общая стоимость: {stats['total_value']:.2f} ({stats['percentage_of_value']:.1f}%)")
        print(f"  Товары: {', '.join(stats['items'][:5])}" + 
              (f" ..." if len(stats['items']) > 5 else ""))
    
    print("\n" + "=" * 80)
    print("РЕКОМЕНДАЦИИ")
    print("=" * 80)
    
    for i, recommendation in enumerate(report['recommendations'], 1):
        print(f"\n{i}. {recommendation}")
    
    print("\n" + "=" * 80)
    print("ТОВАРЫ КАТЕГОРИИ A (требуют особого внимания)")
    print("=" * 80)
    
    category_a_items = request_handler.filter_by_category(
        report['results'], ABCCategory.A
    )
    
    for item in category_a_items:
        print(f"  • {item.name} ({item.sku}): стоимость {item.total_value:.2f}")


if __name__ == "__main__":
    main()
