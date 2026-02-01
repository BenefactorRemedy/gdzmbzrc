"""
Примеры работы с запросами по ABC анализу для Supply Chain

Этот файл демонстрирует различные типы запросов, которые можно 
выполнять с помощью модуля ABC анализа.
"""

from abc_analysis import (
    Product, 
    SupplyChainABCRequest, 
    ABCCategory,
    ABCAnalyzer
)


def example_1_basic_analysis():
    """
    Пример 1: Базовый анализ инвентаря
    
    Показывает как выполнить простой ABC анализ и получить результаты.
    """
    print("\n" + "="*80)
    print("ПРИМЕР 1: БАЗОВЫЙ АНАЛИЗ ИНВЕНТАРЯ")
    print("="*80)
    
    # Создание списка товаров
    products = [
        Product("A001", "Смартфон iPhone", 100, 800.0),
        Product("A002", "Планшет iPad", 50, 600.0),
        Product("A003", "Наушники AirPods", 300, 200.0),
        Product("A004", "Зарядное устройство", 500, 30.0),
        Product("A005", "Кабель Lightning", 1000, 15.0),
    ]
    
    # Выполнение анализа
    handler = SupplyChainABCRequest()
    report = handler.process_inventory_analysis(products)
    
    print(f"\nСтатус: {report['status']}")
    print(f"Всего товаров: {report['total_products']}")
    print("\nРезультаты:")
    
    for result in report['results']:
        print(f"  {result}")


def example_2_filter_by_category():
    """
    Пример 2: Фильтрация товаров по категориям
    
    Показывает как получить товары определенной категории.
    """
    print("\n" + "="*80)
    print("ПРИМЕР 2: ФИЛЬТРАЦИЯ ПО КАТЕГОРИЯМ")
    print("="*80)
    
    products = [
        Product("B001", "Ноутбук MacBook", 30, 2500.0),
        Product("B002", "Монитор LG", 100, 400.0),
        Product("B003", "Клавиатура механическая", 200, 150.0),
        Product("B004", "Мышь игровая", 300, 80.0),
        Product("B005", "Коврик для мыши", 1000, 10.0),
    ]
    
    handler = SupplyChainABCRequest()
    report = handler.process_inventory_analysis(products)
    
    # Фильтрация товаров категории A
    print("\nТовары категории A (высокая важность):")
    a_items = handler.filter_by_category(report['results'], ABCCategory.A)
    for item in a_items:
        print(f"  • {item.name}: {item.total_value:.2f} руб.")
    
    # Фильтрация товаров категории C
    print("\nТовары категории C (низкая важность):")
    c_items = handler.filter_by_category(report['results'], ABCCategory.C)
    for item in c_items:
        print(f"  • {item.name}: {item.total_value:.2f} руб.")


def example_3_top_products():
    """
    Пример 3: Получение топ товаров
    
    Показывает как получить N самых ценных товаров.
    """
    print("\n" + "="*80)
    print("ПРИМЕР 3: ТОП ТОВАРОВ ПО СТОИМОСТИ")
    print("="*80)
    
    products = [
        Product("C001", "Сервер Dell PowerEdge", 5, 5000.0),
        Product("C002", "Рабочая станция HP", 15, 3000.0),
        Product("C003", "Ноутбук бизнес-класса", 50, 1500.0),
        Product("C004", "Принтер МФУ", 30, 500.0),
        Product("C005", "Сканер документов", 20, 300.0),
        Product("C006", "Веб-камера HD", 100, 100.0),
        Product("C007", "USB-хаб", 200, 25.0),
        Product("C008", "Адаптер HDMI", 500, 15.0),
    ]
    
    handler = SupplyChainABCRequest()
    report = handler.process_inventory_analysis(products)
    
    # Топ 3 товара
    print("\nТоп 3 товара по общей стоимости:")
    top_3 = handler.get_top_products(report['results'], n=3)
    for i, item in enumerate(top_3, 1):
        print(f"  {i}. {item.name}: {item.total_value:.2f} руб. " +
              f"(Категория: {item.category.value})")
    
    # Топ 5 товаров
    print("\nТоп 5 товаров по общей стоимости:")
    top_5 = handler.get_top_products(report['results'], n=5)
    for i, item in enumerate(top_5, 1):
        print(f"  {i}. {item.name}: {item.total_value:.2f} руб.")


def example_4_custom_thresholds():
    """
    Пример 4: Настройка пользовательских порогов
    
    Показывает как использовать собственные пороги для категоризации.
    """
    print("\n" + "="*80)
    print("ПРИМЕР 4: ПОЛЬЗОВАТЕЛЬСКИЕ ПОРОГИ КАТЕГОРИЙ")
    print("="*80)
    
    products = [
        Product("D001", "Товар 1", 100, 1000.0),
        Product("D002", "Товар 2", 150, 600.0),
        Product("D003", "Товар 3", 200, 400.0),
        Product("D004", "Товар 4", 300, 200.0),
        Product("D005", "Товар 5", 500, 100.0),
    ]
    
    # Стандартные пороги (A: 80%, B: 95%)
    print("\nСтандартные пороги (A: 80%, B: 95%):")
    standard_analyzer = ABCAnalyzer()
    results_standard = standard_analyzer.analyze(products)
    
    for result in results_standard:
        print(f"  [{result.category.value}] {result.name}")
    
    # Пользовательские пороги (A: 60%, B: 85%)
    print("\nПользовательские пороги (A: 60%, B: 85%):")
    custom_analyzer = ABCAnalyzer(
        category_a_threshold=60.0,
        category_b_threshold=85.0
    )
    results_custom = custom_analyzer.analyze(products)
    
    for result in results_custom:
        print(f"  [{result.category.value}] {result.name}")


def example_5_category_summary():
    """
    Пример 5: Сводная статистика по категориям
    
    Показывает как получить детальную статистику по каждой категории.
    """
    print("\n" + "="*80)
    print("ПРИМЕР 5: СВОДНАЯ СТАТИСТИКА")
    print("="*80)
    
    products = [
        Product("E001", "Дорогой товар 1", 10, 5000.0),
        Product("E002", "Дорогой товар 2", 15, 4000.0),
        Product("E003", "Средний товар 1", 50, 1000.0),
        Product("E004", "Средний товар 2", 75, 800.0),
        Product("E005", "Средний товар 3", 100, 600.0),
        Product("E006", "Дешевый товар 1", 500, 50.0),
        Product("E007", "Дешевый товар 2", 1000, 30.0),
        Product("E008", "Дешевый товар 3", 2000, 20.0),
    ]
    
    analyzer = ABCAnalyzer()
    results = analyzer.analyze(products)
    summary = analyzer.get_category_summary(results)
    
    print("\nДетальная статистика по категориям:\n")
    
    for category in ['A', 'B', 'C']:
        stats = summary[category]
        print(f"Категория {category}:")
        print(f"  Количество товаров: {stats['count']}")
        print(f"  Процент от количества: {stats['percentage_of_items']:.1f}%")
        print(f"  Общая стоимость: {stats['total_value']:,.2f} руб.")
        print(f"  Процент от стоимости: {stats['percentage_of_value']:.1f}%")
        print(f"  Артикулы: {', '.join(stats['items'])}")
        print()


def example_6_supply_chain_workflow():
    """
    Пример 6: Полный рабочий процесс для Supply Chain
    
    Демонстрирует практическое применение ABC анализа 
    в управлении цепями поставок.
    """
    print("\n" + "="*80)
    print("ПРИМЕР 6: ПОЛНЫЙ РАБОЧИЙ ПРОЦЕСС SUPPLY CHAIN")
    print("="*80)
    
    # Реальный сценарий: склад запчастей для электроники
    warehouse_inventory = [
        Product("PART001", "Процессор Intel i9", 50, 500.0),
        Product("PART002", "Материнская плата ASUS", 60, 300.0),
        Product("PART003", "Оперативная память 16GB", 200, 100.0),
        Product("PART004", "SSD накопитель 1TB", 150, 120.0),
        Product("PART005", "Блок питания 750W", 100, 80.0),
        Product("PART006", "Корпус ПК", 80, 60.0),
        Product("PART007", "Кулер для процессора", 300, 40.0),
        Product("PART008", "Термопаста", 1000, 5.0),
        Product("PART009", "Винты и крепеж", 5000, 2.0),
        Product("PART010", "Кабель-стяжки", 10000, 0.5),
    ]
    
    handler = SupplyChainABCRequest()
    report = handler.process_inventory_analysis(warehouse_inventory)
    
    print("\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
    print(f"Всего SKU на складе: {report['total_products']}")
    
    # Категория A - Критические товары
    a_items = handler.filter_by_category(report['results'], ABCCategory.A)
    print(f"\n🔴 Категория A - {len(a_items)} товаров (КРИТИЧНЫЕ):")
    print("   Действия:")
    print("   • Ежедневный мониторинг остатков")
    print("   • Точка повторного заказа: 30% от текущего запаса")
    print("   • Приоритетная обработка заказов")
    print("   • Работа с проверенными поставщиками")
    print("\n   Товары:")
    for item in a_items:
        reorder_point = int(item.quantity * 0.3)
        print(f"   - {item.name}: остаток {item.quantity}, заказывать при {reorder_point}")
    
    # Категория B - Важные товары
    b_items = handler.filter_by_category(report['results'], ABCCategory.B)
    print(f"\n🟡 Категория B - {len(b_items)} товаров (ВАЖНЫЕ):")
    print("   Действия:")
    print("   • Еженедельный мониторинг")
    print("   • Точка повторного заказа: 25% от текущего запаса")
    print("   • Стандартные процедуры заказа")
    print("\n   Товары:")
    for item in b_items:
        reorder_point = int(item.quantity * 0.25)
        print(f"   - {item.name}: остаток {item.quantity}, заказывать при {reorder_point}")
    
    # Категория C - Массовые товары
    c_items = handler.filter_by_category(report['results'], ABCCategory.C)
    print(f"\n🟢 Категория C - {len(c_items)} товаров (МАССОВЫЕ):")
    print("   Действия:")
    print("   • Ежемесячный мониторинг")
    print("   • Точка повторного заказа: 20% от текущего запаса")
    print("   • Заказ большими партиями для снижения затрат")
    print("\n   Товары:")
    for item in c_items:
        reorder_point = int(item.quantity * 0.2)
        print(f"   - {item.name}: остаток {item.quantity}, заказывать при {reorder_point}")
    
    # Рекомендации
    print("\n📋 РЕКОМЕНДАЦИИ:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. {rec}")


def example_7_comparison_scenarios():
    """
    Пример 7: Сравнение разных сценариев
    
    Показывает как ABC анализ помогает в принятии решений.
    """
    print("\n" + "="*80)
    print("ПРИМЕР 7: СРАВНЕНИЕ СЦЕНАРИЕВ")
    print("="*80)
    
    # Сценарий: сравнение двух складов
    warehouse_1 = [
        Product("W1-001", "Товар 1", 100, 1000.0),
        Product("W1-002", "Товар 2", 200, 500.0),
        Product("W1-003", "Товар 3", 300, 300.0),
        Product("W1-004", "Товар 4", 500, 100.0),
    ]
    
    warehouse_2 = [
        Product("W2-001", "Товар 1", 50, 2000.0),
        Product("W2-002", "Товар 2", 100, 1000.0),
        Product("W2-003", "Товар 3", 200, 500.0),
        Product("W2-004", "Товар 4", 400, 200.0),
    ]
    
    handler = SupplyChainABCRequest()
    
    print("\nСклад 1:")
    report_1 = handler.process_inventory_analysis(warehouse_1)
    summary_1 = report_1['summary']
    print(f"  Категория A: {summary_1['A']['count']} товаров, " +
          f"{summary_1['A']['percentage_of_value']:.1f}% стоимости")
    print(f"  Общая стоимость: {sum(p.total_value for p in warehouse_1):,.2f} руб.")
    
    print("\nСклад 2:")
    report_2 = handler.process_inventory_analysis(warehouse_2)
    summary_2 = report_2['summary']
    print(f"  Категория A: {summary_2['A']['count']} товаров, " +
          f"{summary_2['A']['percentage_of_value']:.1f}% стоимости")
    print(f"  Общая стоимость: {sum(p.total_value for p in warehouse_2):,.2f} руб.")
    
    print("\nВывод:")
    if summary_1['A']['percentage_of_value'] > summary_2['A']['percentage_of_value']:
        print("  Склад 1 имеет более концентрированные активы (выше риск)")
    else:
        print("  Склад 2 имеет более концентрированные активы (выше риск)")


def main():
    """Запуск всех примеров"""
    print("\n" + "="*80)
    print("ПРИМЕРЫ РАБОТЫ С ЗАПРОСАМИ ПО ABC АНАЛИЗУ ДЛЯ SUPPLY CHAIN")
    print("="*80)
    
    examples = [
        example_1_basic_analysis,
        example_2_filter_by_category,
        example_3_top_products,
        example_4_custom_thresholds,
        example_5_category_summary,
        example_6_supply_chain_workflow,
        example_7_comparison_scenarios,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nОшибка в примере: {e}")
    
    print("\n" + "="*80)
    print("ЗАВЕРШЕНО")
    print("="*80)


if __name__ == "__main__":
    main()
