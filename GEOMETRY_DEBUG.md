# 🔍 Диагностика геометрии каналов (тонкие линии и невидимые каналы)

## 🧪 Фактически проверено (06.04.2026)

Тест-кейс:
- Дата: `24.01.1922`
- Время: `07:25`
- Часовой пояс: `UTC+3`

Полученные результаты:
- `Found in SVG: 36/36`
- `ch_1_8` -> `gradient black->grey`
- `ch_7_31` -> `solid black`
- `ch_46_29` -> `gradient red->grey`

Это подтверждает:
- API расчет ворот/каналов корректный для проблемного кейса.
- Логика окраски канала в renderer корректно выбирает режим (`same color`/`gradient`).
- Остаточная проблема, если вид в UI неверный, находится на этапе браузерного отображения (DOM/computed styles/кэш).

Рекомендуемый следующий шаг диагностики:
- Снимать и анализировать блок `DOM verification after SVG insertion` в браузере (F12 -> Console) для тех же 3 каналов.

## Проблема

На bodygraph видно:
- ❌ Канал 7-31 выглядит **очень тонко** вместо стандартной толщины
- ❌ Канал 3-60 **вообще не видно** (его как бы нет)
- ❌ Другие каналы тоже могут быть неправильно отображены

**Причина:** Скорее всего координаты ворот в коде **не совпадают** с реальным расположением на bodygraph в SVG.

---

## Новое расширенное логирование

Добавил логирование для проверки:

### 1. **Все ли каналы найдены в SVG?**
```
[DEBUG] === Channel elements check in SVG ===
[DEBUG] Found in SVG: 36/36
```
Или если что-то пропущено:
```
[DEBUG] ⚠️  MISSING: ch_3_60, ch_5_15  ← вот это потом не отрисуется
```

### 2. **Какое расстояние между воротами каждого канала?**
```
[DEBUG] BASE STYLE: ch_1_8
  gate 1 coords: (1080.84, 1601.94)
  gate 8 coords: (1082, 1329)
  distance: 272.94px
  stroke-width: 34
```

### 3. **Какие computed styles действительно применены?**
```
[DEBUG] ch_7_31 in DOM:
  computed stroke-width: 34px   ← если здесь 1px или 2px - проблема!
  computed opacity: 1           ← если 0 - канал скрыт!
  computed display: initial     ← если none - канал скрыт!
  computed visibility: visible  ← если hidden - канал скрыт!
  bbox: x=935.26, y=1325.52, w=0.00, h=362.03  ← если w=0 - линия точка!
```

---

## Как запустить расширенное логирование

### Шаг 1: Hard Refresh
```
Ctrl+Shift+R (Windows) или Cmd+Shift+R (Mac)
```

### Шаг 2: Откройте Console в DevTools
```
F12 → Console вкладка
```

### Шаг 3: Введите тестовую дату и рассчитайте
```
День: 24, Месяц: 1, Год: 1922, Час: 7, Минуты: 25, UTC+3
→ Нажмите "Рассчитать карту"
```

### Шаг 4: Посмотрите новые логи в консоли

Ищите три блока:

```
[DEBUG] === Channel elements check in SVG ===
[DEBUG] Found in SVG: 36/36
[DEBUG] FORCE: ch_1_8 - forced exact path
[DEBUG] FORCE: ch_7_31 - forced exact path
[DEBUG] FORCE: ch_46_29 - forced exact path
[DEBUG] BASE STYLE: ch_1_8
  gate 1 coords: (1080.84, 1601.94)
  gate 8 coords: (1082, 1329)
  distance: 272.94px
  stroke-width: 34
[DEBUG] BASE STYLE: ch_7_31
  ...
[DEBUG] === End channel check ===

[DEBUG] === DOM verification after SVG insertion ===
[DEBUG] ch_1_8 in DOM:
  attr stroke: #7f89ad
  attr stroke-width: 34
  attr filter: (none)
  attr d: M1080.84,1601.94 L1082,1329
  computed stroke: rgb(127, 137, 173)
  computed stroke-width: 34px
  computed opacity: 1
  computed display: initial
  computed visibility: visible
  bbox: x=1080.84, y=1329, w=1.16, h=272.94
[DEBUG] === End DOM verification ===
```

---

## Что проверять в логах

### ✅ Блок 1: Found in SVG
```
[DEBUG] Found in SVG: 36/36  ← OK, все каналы нашлись
```

**Если видно:**
```
[DEBUG] ⚠️  MISSING: ch_3_60  ← Канал вообще нет в SVG!
```
**Решение:** Нужно добавить в SVG или создать path для отсутствующего канала.

---

### ✅ Блок 2: BASE STYLE координаты ворот

```
[DEBUG] BASE STYLE: ch_7_31
  gate 7 coords: (935.26, 1687.55)
  gate 31 coords: (930.62, 1325.52)
  distance: 362.03px
  stroke-width: 34
```

**Проверяем:**
- [ ] Distance > 0? (Если = 0, то обе ворота на одной точке - неверно!)
- [ ] Координаты разумные? (Не выходят за пределы canvas?)

**Если distance очень маленькое (< 10px):**
→ Линия будет выглядеть как точка или невидима.
→ Вероятно, координаты ворот в коде **неверные**.

---

### ✅ Блок 3: Computed styles в DOM

```
[DEBUG] ch_7_31 in DOM:
  computed stroke-width: 34px     ← Must be 34px!
  computed opacity: 1             ← Must be 1!
  computed display: initial       ← Must NOT be none!
  computed visibility: visible    ← Must NOT be hidden!
  bbox: x=935.26, y=1325.52, w=0.00, h=362.03
```

**Проверяем:**

| Параметр | Ожидаемо | Если другое | Что делать |
|----------|----------|-----------|-----------|
| stroke-width | 34px | 1px, 2px, undefined | CSS перетирает или stroke-width не применился |
| opacity | 1 | 0 | Канал полностью прозрачный |
| display | initial / block | none | Канал скрыт CSS-правилом |
| visibility | visible | hidden | Канал скрыт CSS-правилом |
| bbox width | > 0 | 0.00 | Линия вырождается в точку (неверные координаты ворот) |
| bbox height | > 0 | 0.00 | Линия вырождается в точку (неверные координаты ворот) |

---

## 🚨 Вероятные причины тонких линий и невидимых каналов

### Причина 1: Неверные координаты ворот в коде
**Признак:**
```
[DEBUG] BASE STYLE: ch_3_60
  gate 3 coords: (1076.19, 2797.16)
  gate 60 coords: (1082, 3004)
  distance: 207.25px     ← есть расстояние, должно быть видно

[DEBUG] ch_3_60 in DOM:
  bbox: x=1076.19, y=2797.16, w=0.00, h=0.00  ← ❌ НОЛЬ!
```

**Решение:** Нужно проверить координаты ворот 3 и 60 на реальном bodygraph в SVG.

### Причина 2: Исходный path в SVG неверный
**Признак:**
```
[DEBUG] BASE STYLE: ch_7_31
  distance: 362.03px  ← хорошее расстояние

[DEBUG] ch_7_31 in DOM:
  bbox: x=935.26, y=1325.52, w=0.03, h=0.00  ← ❌ Ширина и высота почти НОЛЬ!
```

**Решение:** Нужно проверить исходный path в BODY-02-colored.svg для ch_7_31.

### Причина 3: CSS скрывает каналы
**Признак:**
```
[DEBUG] ch_7_31 in DOM:
  computed stroke-width: 1px  ← ❌ 1px вместо 34px!
  computed opacity: 0         ← ❌ Скрыт!
```

**Решение:** Посмотреть в DevTools → Inspect element → какое CSS-правило переписывает stroke-width?

---

## Как найти правильные координаты ворот в SVG

### Способ 1: Inspect в браузере
1. Откройте bodygraph в браузере
2. Нажмите F12 → Elements
3. Найдите элемент `<circle cx="..." cy="...">` для ворот 7
4. Посмотрите значения cx и cy
5. Это должны быть координаты в gateCoords[7]

### Способ 2: Откройте BODY-02-colored.svg в текстовом редакторе
```xml
<circle cx="935.26" cy="1687.55" ... id="gate_7" />
```
Это координаты для gate 7.

---

## Чеклист проверки каждого канала

Для **ch_7_31** проверяем:

- [ ] В console логе видно `[DEBUG] Found in SVG: 36/36` или есть MISSING?
- [ ] Distance > 0? Пример: `distance: 362.03px`
- [ ] stroke-width в DOM = 34px?
- [ ] bbox width > 0 и height > 0?
- [ ] На экране видна линия между ворот 7 и 31?

**Если все ОК, но линия тонкая:**
→ Вероятно CSS перетирает stroke-width
→ Откройте DevTools → Inspect → Styles → ищите скрывающее правило

---

## Действия по результатам

### Если найдено: координаты ворот неверные

1. **Откройте BODY-02-colored.svg** в текстовом редакторе
2. **Найдите реальные координаты ворот** (cx, cy для каждой)
3. **Обновите gateCoords** в bodygraph_renderer.js
4. **Hard Refresh и пересчитайте**

### Если найдено: пути в SVG неверные

1. **Откройте BODY-02-colored.svg**
2. **Найдите path для канала** (id="ch_7_31")
3. **Проверьте, совпадает ли path с геометрией ворот**
4. **Исправьте path или используйте FORCE_EXACT_PATH_CHANNELS** (уже включено для трех каналов)

### Если найдено: CSS скрывает

1. **Откройте DevTools → Inspect на невидимом канале**
2. **Посмотрите Styles панель**
3. **Найдите какое правило переписывает stroke-width или opacity**
4. **Отключите это правило** (нажать на галочку)
5. **Посмотрите, станет ли видно**

---

## Следующие шаги

1. **Запустите новое логирование** (с версией `v=20260406-debug-geometry`)
2. **Скопируйте все логи от `[DEBUG] === Channel elements check` до конца**
3. **Скриншот bodygraph** (видно ли каналы?)
4. **Отправьте результаты для анализа**

После этого будем знать точно, где проблема!

---

**Версия:** 1.0 (расширенное логирование для геометрии)
**Время диагностики:** 5-10 минут
