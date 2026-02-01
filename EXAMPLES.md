# Примеры использования SC-PRIORITY-DEMO-LITE RU v2.2

## Пример 1: Базовое использование через CLI

### Подготовка данных

Создайте файлы с заказами и остатками:

**orders.txt:**
```
ORD001 | ITEM-A | 50 | B
ORD002 | ITEM-A | 30 | A
ORD003 | ITEM-A | 20 | C
```

**stock.txt:**
```
ITEM-A | 70
ITEM-B | 100
```

### Запуск

```bash
python -m src.main \
  --q1 orders.txt \
  --q2 stock.txt \
  --q3 YES \
  --q5 NO \
  --q6 Simplicity \
  -o report.md
```

### Результат

```markdown
## 🎯 Результаты распределения

### Метрики

- **Fill Rate**: 33.3%
- **Count Zero**: 1
- **Risk Level**: 🔴 Red

### Распределение по заказам

| Order ID | SKU | Запрошено | Выделено | Class | Статус |
|---|---|---|---|---|---|
| ORD002 | ITEM-A | 30 | 30 | A | ✅ Выполнен |
| ORD001 | ITEM-A | 50 | 40 | B | ⚠️ Частично |
| ORD003 | ITEM-A | 20 | 0 | C | ❌ Ноль |
```

**Объяснение:**
1. Приоритет A (ORD002) получает 30 единиц первым
2. Приоритет B (ORD001) получает оставшиеся 40 единиц (частично)
3. Приоритет C (ORD003) не получает ничего

---

## Пример 2: Режим Service (Anti-zero)

### Данные

**orders_service.txt:**
```
ORD001 | ITEM-A | 30 | A
ORD002 | ITEM-A | 30 | A
ORD003 | ITEM-A | 30 | A
```

**stock_service.txt:**
```
ITEM-A | 50
```

### Запуск

```bash
python -m src.main \
  --q1 orders_service.txt \
  --q2 stock_service.txt \
  --q3 YES \
  --q5 NO \
  --q6 Service \
  -o report_service.md
```

### Результат

```markdown
| Order ID | SKU | Запрошено | Выделено | Class | Статус |
|---|---|---|---|---|---|
| ORD001 | ITEM-A | 30 | 30 | A | ✅ Выполнен |
| ORD002 | ITEM-A | 30 | 19 | A | ⚠️ Частично |
| ORD003 | ITEM-A | 30 | 1 | A | ⚠️ Частично |
```

**Объяснение режима Service:**
1. Фаза 1: Каждому заказу выделяется 1 единица (всего 3)
2. Фаза 2: Остаток 47 распределяется по FIFO:
   - ORD001: 1 + 29 = 30 (полностью)
   - ORD002: 1 + 18 = 19
   - ORD003: 1 + 0 = 1
3. **Важно:** Count Zero = 0 (никто не получил ноль)

---

## Пример 3: All-or-nothing (Q3=NO)

### Данные

**orders_all.txt:**
```
ORD001 | ITEM-A | 30 | A
ORD002 | ITEM-A | 60 | A
```

**stock_all.txt:**
```
ITEM-A | 70
```

### Запуск

```bash
python -m src.main \
  --q1 orders_all.txt \
  --q2 stock_all.txt \
  --q3 NO \
  --q5 NO \
  --q6 Simplicity \
  -o report_all.md
```

### Результат

```markdown
| Order ID | SKU | Запрошено | Выделено | Class | Статус |
|---|---|---|---|---|---|
| ORD001 | ITEM-A | 30 | 30 | A | ✅ Выполнен |
| ORD002 | ITEM-A | 60 | 0 | A | ❌ Ноль |
```

**Объяснение:**
- ORD001 получает 30 единиц (хватает для полной отгрузки)
- ORD002 запрашивает 60, но остается только 40
- В режиме All-or-nothing: либо полностью (60), либо 0
- Результат: ORD002 получает 0

---

## Пример 4: Сортировка по Due Date (Q5=YES)

### Данные

**orders_duedate.txt:**
```
ORD001 | ITEM-A | 30 | A | 2024-12-31
ORD002 | ITEM-A | 30 | A | 2024-12-15
ORD003 | ITEM-A | 30 | A | 2024-12-20
```

**stock_duedate.txt:**
```
ITEM-A | 50
```

### Запуск

```bash
python -m src.main \
  --q1 orders_duedate.txt \
  --q2 stock_duedate.txt \
  --q3 YES \
  --q5 YES \
  --q6 Simplicity \
  -o report_duedate.md
```

### Результат

```markdown
| Order ID | SKU | Запрошено | Выделено | Class | Статус |
|---|---|---|---|---|---|
| ORD002 | ITEM-A | 30 | 30 | A | ✅ Выполнен |
| ORD003 | ITEM-A | 30 | 20 | A | ⚠️ Частично |
| ORD001 | ITEM-A | 30 | 0 | A | ❌ Ноль |
```

**Объяснение:**
- Заказы сортируются по Due Date (раньше = выше приоритет)
- ORD002 (15 декабря) обрабатывается первым
- ORD003 (20 декабря) вторым
- ORD001 (31 декабря) последним

---

## Пример 5: Учет резервов (Q4)

### Данные

**orders_reserved.txt:**
```
ORD001 | ITEM-A | 100 | A
```

**stock_reserved.txt:**
```
ITEM-A | 100
```

**reserved.txt:**
```
ITEM-A | 30
```

### Запуск

```bash
python -m src.main \
  --q1 orders_reserved.txt \
  --q2 stock_reserved.txt \
  --q3 YES \
  --q4 reserved.txt \
  --q5 NO \
  --q6 Simplicity \
  -o report_reserved.md
```

### Результат

```markdown
| Order ID | SKU | Запрошено | Выделено | Class | Статус |
|---|---|---|---|---|---|
| ORD001 | ITEM-A | 100 | 70 | A | ⚠️ Частично |
```

**Объяснение:**
- Складской остаток: 100 единиц
- Резерв: 30 единиц
- Доступно для распределения: 100 - 30 = 70
- ORD001 получает только 70 из запрошенных 100

---

## Пример 6: Обработка ошибок (STOP)

### Данные с ошибкой

**orders_error.txt:**
```
ORD001 | ITEM-A | 10 | A
ORD001 | ITEM-B | 20 | B
```

### Запуск

```bash
python -m src.main \
  --q1 orders_error.txt \
  --q2 stock.txt \
  --q3 YES \
  --q5 NO \
  --q6 Simplicity \
  -o report_error.md
```

### Результат

```markdown
## 📊 Статус обработки

### ❌ КРИТИЧЕСКИЕ ОШИБКИ (STOP)
- STOP: Найдены дублирующиеся ID заказов: ORD001
```

**Объяснение:**
- Система обнаруживает дубликаты ID
- Обработка останавливается (STOP)
- Распределение не выполняется

---

## Интерактивный режим

Запустите без аргументов для интерактивного ввода:

```bash
python -m src.main
```

Система запросит ввод данных для каждого вопроса:

```
Q1: Введите заказы (Формат: ID | SKU | Qty | Class [| Due_Date])
(Введите данные, пустая строка для завершения)
ORD001 | ITEM-A | 10 | A
ORD002 | ITEM-B | 20 | B

Q2: Введите складские остатки (Формат: SKU | Qty)
ITEM-A | 100
ITEM-B | 50

Q3: Разрешены частичные отгрузки? (YES/NO): YES

Q4: Введите зарезервированные остатки (Формат: SKU | Qty)

Q5: Использовать сортировку по Due Date? (YES/NO): NO

Q6: Режим обслуживания при дефиците (Service/Simplicity): Simplicity
```

---

## Запуск демонстрации

Запустите готовые сценарии:

```bash
python demo.py
```

Демонстрация покажет:
- Сценарий A1: Базовое распределение с приоритетами
- Сценарий A3: Режим Service (Anti-zero)
- Сценарий A4: All-or-nothing
- Сценарий C1: Обработка критических ошибок

---

## Запуск тестов

```bash
# Все тесты
pytest

# Детальный вывод
pytest -v

# Конкретный тест
pytest tests/test_scenarios.py::TestScenarioA1

# С покрытием
pytest --cov=src tests/
```
