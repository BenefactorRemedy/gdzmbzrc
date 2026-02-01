# SC-PRIORITY-DEMO-LITE RU v2.2

## Описание

Система распределения товаров по заказам с учетом приоритетов (A → B → C).

Проект реализует алгоритмическую логику распределения складских остатков между заказами различных приоритетных классов с учетом:
- Приоритетов заказов (A, B, C)
- Резервов на складе
- Режимов частичной отгрузки
- Сортировки по дате (Due Date) или FIFO
- Режимов обслуживания при дефиците (Service/Simplicity)

## Структура проекта

```
.
├── src/
│   ├── __init__.py
│   ├── models.py       # Модели данных (Order, Stock, InputData)
│   ├── parser.py       # Парсинг входных данных Q1-Q6
│   ├── validator.py    # Валидация (STOP/WARN)
│   ├── allocator.py    # Ядро распределения
│   ├── metrics.py      # Расчет метрик (Fill Rate, Risk Level)
│   ├── formatter.py    # Генерация Markdown-отчетов
│   └── main.py         # CLI точка входа
├── tests/
│   ├── test_scenarios.py  # Тестовые сценарии A1-A4, B1-B3, C1-C4
│   └── test_parser.py     # Тесты парсера
├── requirements.txt
└── README.md
```

## Установка

```bash
# Клонировать репозиторий
git clone https://github.com/BenefactorRemedy/gdzmbzrc.git
cd gdzmbzrc

# Установить зависимости
pip install -r requirements.txt
```

## Использование

### Интерактивный режим

```bash
python -m src.main
```

Система запросит ввод данных для каждого из 6 вопросов (Q1-Q6).

### Режим с файлами

```bash
python -m src.main \
  --q1 orders.txt \
  --q2 stock.txt \
  --q3 YES \
  --q4 reserved.txt \
  --q5 NO \
  --q6 Simplicity \
  -o report.md
```

### Формат входных данных

**Q1 - Заказы** (orders.txt):
```
ORD001 | ITEM-A | 10 | A | 2024-12-31
ORD002 | ITEM-B | 20 | B
ORD003 | ITEM-A | 15 | C
```

**Q2 - Складские остатки** (stock.txt):
```
ITEM-A | 100
ITEM-B | 50
```

**Q3 - Частичные отгрузки**: `YES` или `NO`

**Q4 - Резервы** (reserved.txt):
```
ITEM-A | 20
```

**Q5 - Сортировка по Due Date**: `YES` или `NO`

**Q6 - Режим обслуживания**: `Service` или `Simplicity`

## Запуск тестов

```bash
# Запустить все тесты
pytest

# Запустить с подробным выводом
pytest -v

# Запустить конкретный тест
pytest tests/test_scenarios.py::TestScenarioA1
```

## Логика работы

### Приоритеты

Система обрабатывает заказы строго по приоритетам:
1. **Приоритет A** - обрабатывается первым
2. **Приоритет B** - обрабатывается вторым
3. **Приоритет C** - обрабатывается последним

### Сортировка внутри приоритета

- **Q5 = YES**: Заказы сортируются по Due Date (раньше = выше)
- **Q5 = NO**: FIFO (порядок поступления)

### Режимы обслуживания (Q6)

При наличии **дефицита И конкуренции** (несколько заказов на один SKU):

- **Service (Anti-zero)**: 
  - Фаза 1: Раздать каждому по 1 единице
  - Фаза 2: Остаток распределить по FIFO
  
- **Simplicity**: 
  - Обычное распределение по FIFO

### Частичные отгрузки (Q3)

- **YES**: Разрешены частичные отгрузки
- **NO**: All-or-nothing (либо полностью, либо 0)

### Метрики

- **Fill Rate**: % полностью выполненных заказов
- **Count Zero**: Количество заказов с нулевым выделением
- **Risk Level**:
  - 🟢 **Green**: Fill Rate ≥ 90% И Count Zero = 0
  - 🔴 **Red**: Fill Rate < 70% ИЛИ Count Zero > 20%
  - 🟡 **Yellow**: Все остальные случаи

## Валидация

### STOP (критические ошибки)

- Дублирующиеся ID заказов
- Qty ≤ 0 в заказах
- Qty < 0 в остатках или резервах
- Дублирующиеся SKU в остатках

### WARN (предупреждения)

- SKU заказа отсутствует в остатках
- Резерв превышает остаток

## Примеры использования

### Пример 1: Базовое распределение

```bash
python -m src.main --q1 examples/orders1.txt --q2 examples/stock1.txt \
  --q3 YES --q5 NO --q6 Simplicity -o report1.md
```

### Пример 2: Режим Service с Due Date

```bash
python -m src.main --q1 examples/orders2.txt --q2 examples/stock2.txt \
  --q3 YES --q5 YES --q6 Service -o report2.md
```

## Лицензия

MIT License

## Контакты

Вопросы и предложения приветствуются через GitHub Issues.
