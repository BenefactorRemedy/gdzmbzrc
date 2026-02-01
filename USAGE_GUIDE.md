# Как работать с запросами по ABC анализу для Supply Chain

## Ответ на вопрос из issue

Модуль ABC анализа предоставляет гибкую систему для работы с различными типами запросов в контексте управления цепями поставок. Вот как можно работать с разными типами запросов:

---

## 1. Запрос полного анализа инвентаря

**Описание**: Получить полный анализ всех товаров на складе с категоризацией, статистикой и рекомендациями.

**Код**:
```python
from abc_analysis import Product, SupplyChainABCRequest

products = [
    Product("SKU001", "Товар 1", 100, 500.0),
    Product("SKU002", "Товар 2", 200, 300.0),
    # ... другие товары
]

handler = SupplyChainABCRequest()
report = handler.process_inventory_analysis(products)

# Получить результаты
print(f"Статус: {report['status']}")
print(f"Всего товаров: {report['total_products']}")
```

**Что получите**:
- Статус выполнения
- Общее количество товаров
- Детальные результаты по каждому товару
- Сводную статистику по категориям
- Рекомендации по управлению

---

## 2. Запрос товаров по категории

**Описание**: Получить список товаров определенной категории (A, B или C).

**Код**:
```python
from abc_analysis import ABCCategory

# Получить товары категории A (критически важные)
a_items = handler.filter_by_category(report['results'], ABCCategory.A)

for item in a_items:
    print(f"{item.name}: стоимость {item.total_value:.2f}")
```

**Применение**:
- **Категория A**: Требуют максимального контроля и точного планирования
- **Категория B**: Требуют стандартных процедур контроля
- **Категория C**: Можно использовать упрощенные процедуры

---

## 3. Запрос топ товаров

**Описание**: Получить N самых ценных товаров.

**Код**:
```python
# Получить топ 10 товаров по общей стоимости
top_10 = handler.get_top_products(report['results'], n=10)

for i, item in enumerate(top_10, 1):
    print(f"{i}. {item.name}: {item.total_value:.2f}")
```

**Применение**:
- Приоритизация закупок
- Фокус на ключевых позициях
- Планирование ресурсов

---

## 4. Запрос сводной статистики

**Описание**: Получить детальную статистику по каждой категории.

**Код**:
```python
from abc_analysis import ABCAnalyzer

analyzer = ABCAnalyzer()
results = analyzer.analyze(products)
summary = analyzer.get_category_summary(results)

for category in ['A', 'B', 'C']:
    stats = summary[category]
    print(f"Категория {category}:")
    print(f"  Товаров: {stats['count']}")
    print(f"  Стоимость: {stats['total_value']:.2f}")
    print(f"  % от количества: {stats['percentage_of_items']:.1f}%")
    print(f"  % от стоимости: {stats['percentage_of_value']:.1f}%")
```

**Применение**:
- Анализ структуры запасов
- Оценка рисков
- Планирование инвестиций

---

## 5. Запрос с пользовательскими параметрами

**Описание**: Выполнить анализ с собственными порогами категорий.

**Код**:
```python
# Создать анализатор с пользовательскими порогами
# A: 0-70%, B: 70-90%, C: 90-100%
custom_analyzer = ABCAnalyzer(
    category_a_threshold=70.0,
    category_b_threshold=90.0
)

results = custom_analyzer.analyze(products)
```

**Применение**:
- Адаптация под специфику бизнеса
- Учет отраслевых особенностей
- Тестирование различных стратегий

---

## 6. Интеграция с внешними системами

### Запрос из базы данных

```python
import sqlite3

# Загрузка данных из БД
conn = sqlite3.connect('inventory.db')
cursor = conn.execute('SELECT sku, name, quantity, price FROM products')

products = [Product(*row) for row in cursor.fetchall()]

# Выполнение анализа
report = handler.process_inventory_analysis(products)

# Сохранение результатов обратно в БД
for result in report['results']:
    conn.execute(
        'UPDATE products SET abc_category = ? WHERE sku = ?',
        (result.category.value, result.sku)
    )
conn.commit()
```

### Запрос из ERP системы

```python
# Получение данных из ERP
erp_data = get_from_erp()  # Ваша функция для получения данных

# Преобразование в формат модуля
products = [
    Product(item['sku'], item['name'], item['qty'], item['price'])
    for item in erp_data
]

# Анализ
report = handler.process_inventory_analysis(products)

# Отправка результатов обратно
send_to_erp(report)  # Ваша функция для отправки
```

---

## 7. Запрос для принятия решений

**Сценарий**: Определение стратегии закупок на основе ABC анализа.

**Код**:
```python
report = handler.process_inventory_analysis(products)

# Для товаров категории A
a_items = handler.filter_by_category(report['results'], ABCCategory.A)
for item in a_items:
    # Малые партии, частые заказы, точка заказа 30%
    create_order_strategy(
        sku=item.sku,
        frequency='weekly',
        order_quantity=item.quantity * 0.1,
        reorder_point=item.quantity * 0.3
    )

# Для товаров категории C
c_items = handler.filter_by_category(report['results'], ABCCategory.C)
for item in c_items:
    # Большие партии, редкие заказы, точка заказа 20%
    create_order_strategy(
        sku=item.sku,
        frequency='monthly',
        order_quantity=item.quantity * 0.5,
        reorder_point=item.quantity * 0.2
    )
```

---

## 8. Запрос для мониторинга

**Сценарий**: Настройка автоматического мониторинга в зависимости от категории.

**Код**:
```python
report = handler.process_inventory_analysis(products)

for result in report['results']:
    if result.category == ABCCategory.A:
        # Ежедневный мониторинг для категории A
        setup_monitoring(result.sku, frequency='daily', alert_threshold=0.3)
    elif result.category == ABCCategory.B:
        # Еженедельный мониторинг для категории B
        setup_monitoring(result.sku, frequency='weekly', alert_threshold=0.25)
    else:
        # Ежемесячный мониторинг для категории C
        setup_monitoring(result.sku, frequency='monthly', alert_threshold=0.2)
```

---

## Типичные сценарии использования

### 1. Оптимизация складских запасов
```python
# Анализ текущих запасов
report = handler.process_inventory_analysis(warehouse_inventory)

# Фокус на товарах категории A
critical_items = handler.filter_by_category(report['results'], ABCCategory.A)

for item in critical_items:
    # Установка точного контроля для критических товаров
    setup_daily_monitoring(item.sku)
    setup_automated_reorder(item.sku, min_level=item.quantity * 0.3)
```

### 2. Планирование закупок
```python
# Получение топ товаров для приоритизации
top_items = handler.get_top_products(report['results'], n=50)

for item in top_items:
    prioritize_purchase_order(item.sku, priority=item.category.value)
```

### 3. Работа с поставщиками
```python
# Анализ для переговоров с поставщиками
a_items = handler.filter_by_category(report['results'], ABCCategory.A)

for item in a_items:
    # Товары A требуют работы с надежными поставщиками
    assign_premium_supplier(item.sku)
    negotiate_favorable_terms(item.sku)
```

---

## Преимущества модуля

✅ **Простота использования**: Интуитивный API
✅ **Гибкость**: Настраиваемые пороги и параметры
✅ **Полнота**: Все необходимые типы запросов
✅ **Безопасность**: Нет внешних зависимостей
✅ **Производительность**: Быстрая обработка больших объемов данных
✅ **Документация**: Подробные примеры и руководства

---

## Быстрый запуск

```bash
# Запуск демонстрации
python abc_analysis.py

# Запуск примеров
python examples.py

# Запуск тестов
python -m unittest test_abc_analysis.py -v
```

---

## Дополнительная информация

Подробная документация доступна в файле [ABC_ANALYSIS_GUIDE.md](ABC_ANALYSIS_GUIDE.md)
