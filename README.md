# SC-PRIORITY-DEMO-LITE RU v2.2

**Система распределения складских запасов с приоритетами A → B → C**

## Описание

SC-PRIORITY-DEMO-LITE RU v2.2 — это детерминированная Python-реализация системы распределения товаров по заказам с учетом приоритетов. Система обеспечивает строгую последовательность обработки (A → B → C) и поддерживает различные режимы распределения.

### Основные возможности

- ✅ **Приоритезация A → B → C** — строгая иерархия классов заказов
- 📊 **Метрики** — Fill Rate, Zero Count, Risk Level (Green/Yellow/Red)
- 🛡️ **Валидация** — критические ошибки (STOP) и предупреждения (WARN)
- 🎯 **Режим "Сервис"** — анти-ноль логика для предотвращения нулевых распределений
- 📅 **Сортировка по дате** — обработка заказов по срокам или FIFO
- 🔄 **Частичная отгрузка** — режимы "все или ничего" и частичное выполнение
- 📝 **Markdown отчеты** — детальные отчеты о распределении

## Быстрый старт

### Установка

```bash
git clone https://github.com/BenefactorRemedy/gdzmbzrc.git
cd gdzmbzrc
```

Требования: Python 3.7+

### Запуск

#### Интерактивный режим

```bash
python -m src.main --interactive
```

#### Режим командной строки

```bash
python -m src.main \
  --q1 "ORD001|SKU-A|100|A|-" \
  --q2 "SKU-A|150" \
  --q3 YES \
  --q6 YES
```

#### С сохранением в файл

```bash
python -m src.main \
  --q1 "ORD001|SKU-A|100|A|-" \
  --q2 "SKU-A|150" \
  --output report.md
```

## Входные параметры (Q1-Q6)

| Параметр | Описание | Формат | Пример |
|----------|----------|--------|--------|
| Q1 | Заказы | `OrderID\|SKU\|Qty\|Class\|DueDate` | `ORD001\|SKU-A\|100\|A\|2026-02-15` |
| Q2 | Остатки | `SKU\|Qty` | `SKU-A\|500` |
| Q3 | Частичная отгрузка | `YES/NO` | `YES` |
| Q4 | Резервы | `SKU\|Reserved` | `SKU-A\|50` |
| Q5 | Сортировка по дате | `YES/NO` | `NO` |
| Q6 | Режим сервис (анти-ноль) | `YES/NO` | `YES` |

## Примеры использования

### Пример 1: Базовое распределение с приоритетами

```bash
python -m src.main \
  --q1 "ORD001|SKU-A|50|B|-
ORD002|SKU-A|30|A|-
ORD003|SKU-A|20|C|-" \
  --q2 "SKU-A|70" \
  --q3 YES
```

**Результат:**
- ORD002 (A): 30 шт ← обработан первым (высший приоритет)
- ORD001 (B): 40 шт ← получает остаток
- ORD003 (C): 0 шт ← ничего не осталось

### Пример 2: Режим "Сервис" (анти-ноль)

```bash
python -m src.main \
  --q1 "ORD001|SKU-A|100|A|-
ORD002|SKU-A|80|A|-" \
  --q2 "SKU-A|120" \
  --q6 YES
```

**Результат (с Q6=YES):**
- ORD001: 100 шт (1 + 99)
- ORD002: 20 шт (1 + 19)
- Zero Count: 0 ← анти-ноль работает

**Результат (с Q6=NO):**
- ORD001: 100 шт
- ORD002: 20 шт
- Без изменений в этом случае

### Пример 3: All-or-nothing

```bash
python -m src.main \
  --q1 "ORD001|SKU-A|100|A|-
ORD002|SKU-A|80|A|-" \
  --q2 "SKU-A|120" \
  --q3 NO
```

**Результат:**
- ORD001: 100 шт ← полный запрос (хватает)
- ORD002: 0 шт ← недостаточно для полной отгрузки

## Программный API

```python
from src.main import run_allocation

report = run_allocation(
    q1="ORD001|SKU-A|100|A|-\nORD002|SKU-A|80|A|-",
    q2="SKU-A|120",
    q3="YES",
    q4="-",
    q5="NO",
    q6="YES"  # Режим сервис
)

print(f"Статус: {report.status}")
print(f"Fill Rate: {report.metrics['fill_rate']}%")
print(f"Zero Count: {report.metrics['zero_count']}")
print(f"Risk Level: {report.metrics['risk_level']}")

for result in report.results:
    print(f"{result.order_id}: {result.allocated} шт")
```

## Тестирование

Запуск тестов:

```bash
# Все тесты
pytest tests/

# Нормальные сценарии
pytest tests/test_normal.py

# Предупреждения
pytest tests/test_warn.py

# Критические ошибки
pytest tests/test_stop.py

# Режим сервис (Q6)
pytest tests/test_q6.py

# С покрытием
pytest --cov=src tests/
```

## Структура проекта

```
gdzmbzrc/
├── src/
│   ├── __init__.py
│   ├── models.py          # Модели данных
│   ├── parser.py          # Парсинг Q1-Q6
│   ├── validator.py       # STOP/WARN валидация
│   ├── allocator.py       # Ядро распределения
│   ├── metrics.py         # Расчет метрик
│   ├── formatter.py       # Markdown отчеты
│   └── main.py            # CLI точка входа
├── tests/
│   ├── test_normal.py     # Сценарии A1-A9
│   ├── test_warn.py       # Сценарии B1-B4
│   ├── test_stop.py       # Сценарии C1-C5
│   └── test_q6.py         # Тесты Q6 (сервис)
├── docs/
│   ├── architecture.md    # Архитектура системы
│   └── rules.md           # Правила и алгоритмы
└── README.md
```

## Валидация

### STOP (критические ошибки)

Останавливают распределение:
- **C1**: Дубликаты Order ID
- **C2**: Дубликаты SKU в остатках
- **C3**: Quantity <= 0 в заказах
- **C4**: Quantity < 0 в остатках

### WARN (предупреждения)

Не блокируют распределение:
- **B1**: SKU отсутствует в остатках
- **B2**: Резерв превышает остаток
- **B3**: Есть заказы класса C

## Метрики

### Fill Rate
```
Fill Rate = (Σ allocated / Σ requested) × 100%
```

### Risk Level
- 🟢 **GREEN**: Fill Rate ≥ 90% И zero_count = 0
- 🟡 **YELLOW**: Промежуточные значения
- 🔴 **RED**: Fill Rate < 70% ИЛИ zero_count > 30%

## Документация

- [Архитектура](docs/architecture.md) — компоненты системы и поток данных
- [Правила](docs/rules.md) — детальное описание алгоритмов и правил

## Коды возврата CLI

- `0` — SUCCESS (успешное выполнение)
- `1` — WARN (выполнено с предупреждениями)
- `2` — STOP (критические ошибки)

## Лицензия

MIT

## Контакты

Репозиторий: https://github.com/BenefactorRemedy/gdzmbzrc
