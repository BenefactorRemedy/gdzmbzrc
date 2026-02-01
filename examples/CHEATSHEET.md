# 📝 Шпаргалка - Быстрые команды

## Готовые примеры (один клик)

```bash
# Базовый пример - приоритеты A → B → C
bash examples/scenario1_basic.sh

# Режим "Сервис" - анти-ноль
bash examples/scenario2_service_mode.sh

# Все или ничего (Q3=NO)
bash examples/scenario3_all_or_nothing.sh

# С резервами
bash examples/scenario4_with_reserves.sh

# Сортировка по дате
bash examples/scenario5_date_sorting.sh

# Критическая ошибка (STOP)
bash examples/scenario6_stop_error.sh

# Комплексный сценарий
bash examples/scenario7_complex.sh
```

## Собственные данные

### Простейший запуск
```bash
python -m src.main \
  --q1 "ORD001|SKU-A|100|A|-" \
  --q2 "SKU-A|150"
```

### С настройками
```bash
python -m src.main \
  --q1 "ORD001|SKU-A|100|A|-
ORD002|SKU-A|80|B|-" \
  --q2 "SKU-A|120" \
  --q3 YES \
  --q6 YES
```

### С резервами
```bash
python -m src.main \
  --q1 "ORD001|SKU-A|100|A|-" \
  --q2 "SKU-A|150" \
  --q4 "SKU-A|50"
```

### С датами
```bash
python -m src.main \
  --q1 "ORD001|SKU-A|50|A|2026-03-01
ORD002|SKU-A|50|A|2026-02-15" \
  --q2 "SKU-A|60" \
  --q5 YES
```

### С сохранением в файл
```bash
python -m src.main \
  --q1 "ORD001|SKU-A|100|A|-" \
  --q2 "SKU-A|150" \
  --output отчет.md
```

### Интерактивный режим
```bash
python -m src.main --interactive
```

## Параметры Q1-Q6

### Q1: Заказы
Формат: `OrderID|SKU|Qty|Class|DueDate`
```
ORD001|SKU-A|100|A|2026-02-15
ORD002|SKU-B|50|B|-
```

### Q2: Остатки
Формат: `SKU|Qty`
```
SKU-A|500
SKU-B|200
```

### Q3: Частичная отгрузка
- `YES` - частичная отгрузка разрешена (по умолчанию)
- `NO` - все или ничего

### Q4: Резервы
Формат: `SKU|Reserved`
```
SKU-A|50
```
Или `-` если нет резервов

### Q5: Сортировка
- `YES` - по дате
- `NO` - FIFO (по умолчанию)

### Q6: Режим
- `YES` - "Сервис" (анти-ноль)
- `NO` - "Простота" (по умолчанию)

## Тестирование

```bash
# Все тесты
pytest tests/

# Конкретная группа
pytest tests/test_normal.py
pytest tests/test_q6.py

# С покрытием
pytest --cov=src tests/
```

## Полезные комбинации

### Проверить приоритеты
```bash
python -m src.main \
  --q1 "ORD001|SKU-A|50|B|-
ORD002|SKU-A|30|A|-
ORD003|SKU-A|20|C|-" \
  --q2 "SKU-A|70"
```

### Проверить анти-ноль (Q6)
```bash
python -m src.main \
  --q1 "ORD001|SKU-A|100|A|-
ORD002|SKU-A|80|A|-
ORD003|SKU-A|50|A|-" \
  --q2 "SKU-A|150" \
  --q6 YES
```

### Проверить все или ничего (Q3)
```bash
python -m src.main \
  --q1 "ORD001|SKU-A|100|A|-
ORD002|SKU-A|80|A|-" \
  --q2 "SKU-A|120" \
  --q3 NO
```

### Проверить STOP ошибку
```bash
python -m src.main \
  --q1 "ORD001|SKU-A|0|A|-" \
  --q2 "SKU-A|100"
```

## Коды возврата

- `0` - SUCCESS
- `1` - WARN
- `2` - STOP

```bash
python -m src.main --q1 "..." --q2 "..."
echo "Код: $?"
```
