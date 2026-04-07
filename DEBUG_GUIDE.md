# 🔍 ГАЙД ОТЛАДКИ: Проверка ответа API

## Как проверить что вернёт API для кейса 20.05.1974

### Шаг 1: Запустите калькулятор
```
start_local_server.cmd
```

### Шаг 2: Откройте DevTools
1. Откройте браузер на `http://localhost:5000`
2. Нажмите **F12** → вкладка **Network**
3. Введите дату: **20.05.1974 15:25 Киев**
4. Нажмите **Рассчитать**

### Шаг 3: Найдите запрос к API
- В Network табе найдите запрос `/api/calc` (POST)
- Нажмите на него
- Откройте вкладку **Response** или **Preview**

### Шаг 4: Проверьте JSON ответ

**Ожидается в personality_planets:**
```json
{
  "planet": "Сев.Узел",
  "symbol": "☊",
  "longitude": 259.477,           ← ДОЛГОТА (не Gate!)
  "gate": 26,                     ← Gate должен быть 26
  "line": 3,                      ← Line
  "color": ...,
  "tone": ...,
  "gate_line": "26.3"             ← Ожидается 26.3, НЕ 11.5!
}
```

**И ещё в personality_planets должна быть:**
```json
{
  "planet": "Юж.Узел",            ← South Node
  "symbol": "☋",
  "longitude": 79.477,            ← ДОЛГОТА
  "gate": 45,                     ← Gate = 45! ← ТУТ GATE 45
  "line": 3,
  "color": ...,
  "tone": ...,
  "gate_line": "45.3"
}
```

---

## Возможные проблемы

### Проблема 1: North Node = 11.5 вместо 259.477°
- **Причина:** Фронтенд может неправильно парсить JSON
- **Проверка:** Посмотрите в Network Response — что точно вернул API

### Проблема 2: South Node отсутствует в personality_planets
- **Причина:** API не вычисляет South Node
- **Проверка:** В hd_api.py код South Node добавлен? (lines 419-444)

### Проблема 3: Gate 45 не в all_gates
- **Причина:** Ворота не добавлены в множество
- **Проверка:** `personality_gates.add(sg_p)` есть в коде?

---

## Прямой тест через Python

```bash
python3 << 'EOF'
import requests
import json

data = {
    "year": 1974,
    "month": 5,
    "day": 20,
    "hour": 15,
    "minute": 25,
    "second": 0,
    "tz_offset": 3,
}

r = requests.post("http://localhost:10000/api/calc", json=data)
result = r.json()

print("Personality planets:")
for p in result['personality_planets']:
    if 'Узел' in p['planet'] or p['planet'] == 'Юж.Узел':
        print(f"  {p['planet']}: lon={p['longitude']}, gate={p['gate']}")

print(f"\nAll gates: {result['all_gates']}")
print(f"Gate 45 present: {45 in result['all_gates']}")
EOF
```

---

## Если Gate 45 всё ещё отсутствует

1. Проверьте что используется **исправленный hd_api.py** (с South Node)
   ```bash
   grep -n "South Node" hd_api.py
   # Должно найти строки 419-444
   ```

2. Перезагрузите API (убейте процесс Python и перезагрузите)

3. Запустите регрессионный тест
   ```bash
   python3 regression_tests.py
   ```
   Должны быть все 9 PASS

4. Проверьте validate_lookup.py
   ```bash
   python3 validate_lookup.py
   ```
   Должны быть все PASS (включая 79.5° → Gate 45)
