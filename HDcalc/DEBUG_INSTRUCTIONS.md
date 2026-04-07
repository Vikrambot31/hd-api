# Debug инструкции для проблемы отрисовки каналов

## Что было добавлено
В `bodygraph_renderer.js` добавлены debug-логи, которые выводят в консоль браузера:
1. Значения цветов для ворот канала (ca, cb)
2. Итоговый `stroke` (цвет или градиент)
3. Итоговый `stroke-width`
4. Итоговый `d` (путь линии)
5. Присутствие фильтра `filter`
6. Computed styles после вставки в DOM

Логи выводятся **только для трех проблемных каналов:**
- `ch_1_8`
- `ch_7_31`
- `ch_46_29`

## Как запустить тест

### Шаг 1: Откройте калькулятор
Откройте `calculator_web.html` через локальный HTTP-сервер (не как файл).

### Шаг 2: Откройте DevTools
Нажмите **F12** (или Ctrl+Shift+I / Cmd+Option+I на Mac) → перейдите на вкладку **Console**

### Шаг 3: Введите тестовые данные
Вверху слева в форме введите:
- **День:** 24
- **Месяц:** 1
- **Год:** 1922
- **Час:** 7
- **Минуты:** 25
- **Секунды:** 0
- **Часовой пояс:** UTC+3 (Москва)

### Шаг 4: Запустите расчет
Нажмите кнопку **"Рассчитать карту"**

### Шаг 5: Смотрите логи в Console
В консоли браузера должны появиться логи вида:

```
PERS: [1, 7, 18, 26, 31, 37, 41, 48, 49, 52, 57, 60]
DES: [6, 7, 18, 27, 28, 37, 39, 44, 46, 48, 57]

[DEBUG] ch_1_8: ca=black, cb=null
[DEBUG] ch_1_8: gradient mode
  c1: #111111 (gate 1)
  c2: #888888 (gate 8)
  stroke: url(#grad_ch_1_8)
  stroke-width: 34
  filter: url(#activeGlow)
  gradient from (1080.84,1601.94) to (1082,1329)
  d: M1080.84,1601.94 L1082,1329

[DEBUG] ch_7_31: ca=black, cb=black
[DEBUG] ch_7_31: same color mode
  stroke: #111111
  stroke-width: 34
  filter: url(#activeGlow)
  d: M935.26,1687.55 L930.62,1325.52

[DEBUG] ch_46_29: ca=red, cb=null
[DEBUG] ch_46_29: gradient mode
  c1: #cc2200 (gate 46)
  c2: #888888 (gate 29)
  stroke: url(#grad_ch_46_29)
  stroke-width: 34
  filter: url(#activeGlow)
  gradient from (1207.19,1924.23) to (1216.1,2519.65)
  d: M1207.19,1924.23 L1216.1,2519.65

[DEBUG] === DOM verification after SVG insertion ===
[DEBUG] ch_1_8 in DOM:
  attr stroke: url(#grad_ch_1_8)
  attr stroke-width: 34
  attr filter: url(#activeGlow)
  attr d: M1080.84,1601.94 L1082,1329
  computed stroke: ...
  computed stroke-width: ...
[DEBUG] ch_7_31 in DOM:
  attr stroke: #111111
  ...
[DEBUG] ch_46_29 in DOM:
  attr stroke: url(#grad_ch_46_29)
  ...
[DEBUG] === End DOM verification ===
```

## Что проверить в логах

### 1. Правильное определение цветов ворот
Проверьте, что логи показывают:
- `ch_1_8: ca=black, cb=null` → **ожидается** (gate 1 в personality, gate 8 не активна)
- `ch_7_31: ca=black, cb=black` → **ожидается** (обе ворота в personality)
- `ch_46_29: ca=red, cb=null` → **ожидается** (gate 46 в design, gate 29 не активна)

**Если видны другие значения** → проблема в API или логике определения ворот.

### 2. Правильность stroke и градиентов
Проверьте:
- Для `ch_1_8` и `ch_46_29` должны быть созданы **градиенты** `url(#grad_...)`
- Для `ch_7_31` должен быть **solid black** `#111111`
- Все три должны иметь `stroke-width: 34` и `filter: url(#activeGlow)`

### 3. DOM-состояние после вставки
В секции `=== DOM verification after SVG insertion ===`:
- Проверьте, что атрибуты совпадают с тем, что было установлено выше
- Если stroke вдруг изменился на что-то другое → **style overwrite** от CSS или другого скрипта

## Если видно проблему

### Проблема 1: Неверные ca/cb (цвета ворот)
Значит, логика в `gateColorFromSets()` или нормализация ворот работает неправильно.
→ Проверьте: получают ли consciousGates и unconsciousGates правильные значения.

### Проблема 2: Логи показывают правильные значения, но в браузере каналы не видны
Значит, **стиль перетирается после вставки** CSS или другим скриптом.
→ В DevTools найдите элемент `<path id="ch_1_8">`, нажмите правую кнопку → Inspect
→ Посмотрите на Styles панель: есть ли red/blue правила CSS, которые перезаписывают stroke?

### Проблема 3: `ch_1_8` в DOM имеет `attr d: M1080.84,1601.94 L1082,1329` но визуально это не линия
Проверьте:
- Точки `(1080.84,1601.94)` и `(1082,1329)` действительно находятся на дизайне?
- Может быть, canvas/SVG viewBox некорректный?

## После диагностики

Когда найдете проблему:
1. Зафиксируйте скриншот консоли с логами
2. Опишите, какой именно лог отличается от ожидаемого
3. Удалите debug-код из `bodygraph_renderer.js` (или замените версию в HTML на финальную)

---

**Тестовые данные:**
- Date: 24.01.1922, 07:25, UTC+3
- Expected personality_gates: 1,7,18,26,31,37,41,48,49,52,57,60
- Expected design_gates: 6,7,18,27,28,37,39,44,46,48,57

**Expected visual result:**
- `ch_7_31`: solid black
- `ch_1_8`: black → gray gradient
- `ch_46_29`: red → gray gradient
