# ABC Анализ для Supply Chain Management

## Описание

Модуль ABC анализа предназначен для классификации товарных запасов на основе их важности и стоимости. Это критически важный инструмент управления цепями поставок, который помогает оптимизировать управление складом и снизить затраты.

## Что такое ABC анализ?

ABC анализ - это метод категоризации товарно-материальных запасов, основанный на принципе Парето (правило 80/20). Товары классифицируются на три категории:

### Категория A (Высокая важность)
- **Доля товаров**: ~20% от общего количества
- **Доля стоимости**: ~80% от общей стоимости
- **Характеристики**: Высокая стоимость, критически важны для бизнеса
- **Управление**: Требует максимального контроля, точного планирования, регулярного мониторинга

### Категория B (Средняя важность)
- **Доля товаров**: ~30% от общего количества
- **Доля стоимости**: ~15% от общей стоимости
- **Характеристики**: Умеренная стоимость, средняя важность
- **Управление**: Стандартные процедуры контроля и заказа

### Категория C (Низкая важность)
- **Доля товаров**: ~50% от общего количества
- **Доля стоимости**: ~5% от общей стоимости
- **Характеристики**: Низкая стоимость, минимальное влияние на бизнес
- **Управление**: Упрощенные процедуры, большие партии заказов

## Установка и использование

### Требования
- Python 3.7+
- Нет внешних зависимостей (использует только стандартную библиотеку)

### Быстрый старт

```python
from abc_analysis import Product, SupplyChainABCRequest, ABCCategory

# Создание списка товаров
products = [
    Product("SKU001", "Компьютер Dell XPS", 50, 1500.0),
    Product("SKU002", "Монитор Samsung", 120, 300.0),
    Product("SKU003", "Клавиатура Logitech", 500, 50.0),
]

# Создание обработчика запросов
request_handler = SupplyChainABCRequest()

# Выполнение анализа
report = request_handler.process_inventory_analysis(products)

# Вывод результатов
print(f"Всего товаров: {report['total_products']}")
for result in report['results']:
    print(result)
```

## Основные возможности

### 1. Анализ инвентаря

```python
# Обработка полного анализа инвентаря
report = request_handler.process_inventory_analysis(products)

# Отчет содержит:
# - status: статус выполнения
# - total_products: общее количество товаров
# - results: детальные результаты по каждому товару
# - summary: сводная статистика по категориям
# - recommendations: рекомендации по управлению
```

### 2. Фильтрация по категориям

```python
# Получение результатов анализа
results = report['results']

# Фильтрация товаров категории A (требующих особого внимания)
category_a = request_handler.filter_by_category(results, ABCCategory.A)

# Фильтрация товаров категории B
category_b = request_handler.filter_by_category(results, ABCCategory.B)

# Фильтрация товаров категории C
category_c = request_handler.filter_by_category(results, ABCCategory.C)
```

### 3. Получение топ товаров

```python
# Топ 10 товаров по стоимости
top_10 = request_handler.get_top_products(results, n=10)

# Топ 5 товаров
top_5 = request_handler.get_top_products(results, n=5)
```

### 4. Настройка порогов категорий

```python
from abc_analysis import ABCAnalyzer

# Создание анализатора с пользовательскими порогами
# A: 0-70%, B: 70-90%, C: 90-100%
custom_analyzer = ABCAnalyzer(
    category_a_threshold=70.0,
    category_b_threshold=90.0
)

# Использование пользовательского анализатора
results = custom_analyzer.analyze(products)
```

## Типы запросов

### 1. Запрос полного анализа

```python
# Получение полного отчета с рекомендациями
report = request_handler.process_inventory_analysis(products)
```

**Ответ включает**:
- Детальные результаты по каждому товару
- Сводную статистику по категориям
- Рекомендации по управлению запасами

### 2. Запрос по конкретной категории

```python
# Получить все товары категории A
a_items = request_handler.filter_by_category(results, ABCCategory.A)

# Вывод информации о критически важных товарах
for item in a_items:
    print(f"{item.name}: стоимость {item.total_value:.2f}")
```

### 3. Запрос топ товаров

```python
# Получить 20 самых ценных товаров
top_20 = request_handler.get_top_products(results, n=20)
```

### 4. Запрос сводной статистики

```python
# Получение детальной статистики по категориям
summary = custom_analyzer.get_category_summary(results)

for category in ['A', 'B', 'C']:
    stats = summary[category]
    print(f"Категория {category}:")
    print(f"  Товаров: {stats['count']}")
    print(f"  Стоимость: {stats['total_value']:.2f}")
    print(f"  % от количества: {stats['percentage_of_items']:.1f}%")
    print(f"  % от стоимости: {stats['percentage_of_value']:.1f}%")
```

## Примеры использования в Supply Chain

### Пример 1: Оптимизация складских запасов

```python
# Анализ текущих запасов
report = request_handler.process_inventory_analysis(warehouse_inventory)

# Фокус на товарах категории A для точного планирования
critical_items = request_handler.filter_by_category(
    report['results'], 
    ABCCategory.A
)

# Установка частого мониторинга для критических товаров
for item in critical_items:
    setup_daily_monitoring(item.sku)
    setup_automated_reorder(item.sku, min_stock_level=item.quantity * 0.3)
```

### Пример 2: Планирование закупок

```python
# Получение топ товаров для приоритетной закупки
top_items = request_handler.get_top_products(report['results'], n=50)

# Создание заказов на закупку с учетом важности
for item in top_items:
    if item.category == ABCCategory.A:
        # Категория A: малые партии, частые заказы
        create_purchase_order(item.sku, order_quantity=item.quantity * 0.1)
    elif item.category == ABCCategory.B:
        # Категория B: средние партии
        create_purchase_order(item.sku, order_quantity=item.quantity * 0.25)
    else:
        # Категория C: большие партии, редкие заказы
        create_purchase_order(item.sku, order_quantity=item.quantity * 0.5)
```

### Пример 3: Управление поставщиками

```python
# Анализ товаров для переговоров с поставщиками
a_items = request_handler.filter_by_category(report['results'], ABCCategory.A)

# Товары категории A требуют работы с надежными поставщиками
for item in a_items:
    assign_premium_supplier(item.sku)
    negotiate_favorable_terms(item.sku)
    setup_backup_supplier(item.sku)
```

## Структура данных

### Product (Товар)

```python
@dataclass
class Product:
    sku: str           # Артикул товара
    name: str          # Название товара
    quantity: int      # Количество на складе
    unit_price: float  # Цена за единицу
```

### ABCAnalysisResult (Результат анализа)

```python
@dataclass
class ABCAnalysisResult:
    sku: str                      # Артикул товара
    name: str                     # Название товара
    quantity: int                 # Количество
    unit_price: float             # Цена за единицу
    total_value: float            # Общая стоимость
    cumulative_percentage: float  # Накопительный процент
    category: ABCCategory         # Категория (A, B, или C)
```

## API Reference

### ABCAnalyzer

**`__init__(category_a_threshold=80.0, category_b_threshold=95.0)`**
- Создание анализатора с порогами категорий

**`analyze(products: List[Product]) -> List[ABCAnalysisResult]`**
- Выполнение ABC анализа для списка товаров

**`get_category_summary(results: List[ABCAnalysisResult]) -> Dict`**
- Получение сводной статистики по категориям

### SupplyChainABCRequest

**`process_inventory_analysis(products: List[Product]) -> Dict`**
- Обработка запроса на полный анализ инвентаря

**`filter_by_category(results: List[ABCAnalysisResult], category: ABCCategory) -> List[ABCAnalysisResult]`**
- Фильтрация результатов по категории

**`get_top_products(results: List[ABCAnalysisResult], n: int) -> List[ABCAnalysisResult]`**
- Получение топ N товаров по стоимости

## Запуск примера

```bash
# Запуск демонстрации модуля
python abc_analysis.py
```

## Запуск тестов

```bash
# Запуск всех тестов
python -m unittest test_abc_analysis.py -v

# Запуск конкретного теста
python -m unittest test_abc_analysis.TestABCAnalyzer.test_analyze_categories -v
```

## Рекомендации по использованию

1. **Регулярность анализа**: Проводите ABC анализ минимум раз в квартал
2. **Обновление данных**: Используйте актуальные данные о запасах и ценах
3. **Адаптация порогов**: Настраивайте пороги категорий под ваш бизнес
4. **Комбинирование с другими методами**: Используйте совместно с XYZ анализом
5. **Автоматизация**: Интегрируйте в системы управления складом (WMS)

## Преимущества использования

- ✅ **Оптимизация запасов**: Фокус на важнейших товарах
- ✅ **Снижение затрат**: Уменьшение складских издержек
- ✅ **Улучшение обслуживания**: Гарантия наличия критических товаров
- ✅ **Эффективное планирование**: Приоритизация закупок
- ✅ **Простота использования**: Интуитивный API без зависимостей

## Интеграция с другими системами

### Интеграция с ERP

```python
# Получение данных из ERP системы
erp_data = fetch_from_erp_system()

# Преобразование в формат Product
products = [
    Product(item['sku'], item['name'], item['qty'], item['price'])
    for item in erp_data
]

# Анализ
report = request_handler.process_inventory_analysis(products)

# Отправка результатов обратно в ERP
send_abc_results_to_erp(report)
```

### Интеграция с базой данных

```python
import sqlite3

# Загрузка из БД
conn = sqlite3.connect('inventory.db')
cursor = conn.execute('SELECT sku, name, quantity, price FROM products')

products = [Product(*row) for row in cursor.fetchall()]

# Анализ
report = request_handler.process_inventory_analysis(products)

# Сохранение результатов
for result in report['results']:
    conn.execute(
        'UPDATE products SET abc_category = ? WHERE sku = ?',
        (result.category.value, result.sku)
    )
conn.commit()
```

## Поддержка и контакты

Для вопросов и предложений создавайте issue в репозитории проекта.

## Лицензия

Этот модуль является частью проекта SC-PRIORITY-DEMO-LITE RU v2.2
