# ⚡ Быстрая диагностика геометрии (5 минут)

## ✅ Уже собранные данные (24.01.1922, 07:25, UTC+3)

Ниже фактический debug-блок, который уже получен:

```text
[DEBUG] === Channel elements check in SVG ===
[DEBUG] Found in SVG: 36/36
[DEBUG] BASE STYLE: ch_1_8
  gate 1 coords: (1080.84, 1601.94)
  gate 8 coords: (1082, 1329)
  distance: 272,94px
  stroke-width: 34
[DEBUG] ch_1_8: ca=black, cb=
[DEBUG] ch_1_8: gradient mode
  c1: #111111 (gate 1)
  c2: #888888 (gate 8)
  stroke: url(#grad_ch_1_8)
  stroke-width: 34
  filter: url(#activeGlow)
  gradient from (1080.84,1601.94) to (1082,1329)
  d: M1080.84,1601.94 L1082,1329
[DEBUG] BASE STYLE: ch_7_31
  gate 7 coords: (935.26, 1687.55)
  gate 31 coords: (930.62, 1325.52)
  distance: 362,06px
  stroke-width: 34
[DEBUG] ch_7_31: ca=black, cb=black
[DEBUG] ch_7_31: same color mode
  stroke: #111111
  stroke-width: 34
  filter: url(#activeGlow)
  d: M935.26,1687.55 L930.62,1325.52
[DEBUG] BASE STYLE: ch_46_29
  gate 46 coords: (1207.19, 1924.23)
  gate 29 coords: (1216.1, 2519.65)
  distance: 595,49px
  stroke-width: 34
[DEBUG] ch_46_29: ca=red, cb=
[DEBUG] ch_46_29: gradient mode
  c1: #cc2200 (gate 46)
  c2: #888888 (gate 29)
  stroke: url(#grad_ch_46_29)
  stroke-width: 34
  filter: url(#activeGlow)
  gradient from (1207.19,1924.23) to (1216.1,2519.65)
  d: M1207.19,1924.23 L1216.1,2519.65
```

Ключевой вывод по этим данным:
- Проблемные каналы рассчитываются и стилизуются правильно.
- Если на экране несоответствие остается, нужно добрать именно браузерные `computed styles` и `bbox` из DevTools.

## 🎯 Что это найдет

Проверит, почему некоторые каналы **выглядят тонко** или **совсем не видны**.

---

## 🚀 Запустить тест

### 1️⃣ Hard Refresh
```
Ctrl+Shift+R (Windows) или Cmd+Shift+R (Mac)
```

### 2️⃣ F12 → Console

### 3️⃣ Введите данные
```
День: 24
Месяц: 1
Год: 1922
Час: 7
Минуты: 25
Часовой пояс: UTC+3
```

### 4️⃣ Нажмите "Рассчитать карта"

### 5️⃣ Посмотрите логи в Console

---

## 📊 Что проверять в логах

### Блок 1: Найдены ли все каналы в SVG?
```
[DEBUG] === Channel elements check in SVG ===
[DEBUG] Found in SVG: 36/36     ← Отлично, все нашлись
```

❌ **Если видно:**
```
[DEBUG] ⚠️  MISSING: ch_3_60, ch_5_15
```
→ Это каналы пропущены в SVG, их нет вообще.

---

### Блок 2: Какое расстояние между воротами?
```
[DEBUG] BASE STYLE: ch_7_31
  gate 7 coords: (935.26, 1687.55)
  gate 31 coords: (930.62, 1325.52)
  distance: 362.03px
```

**Проверяем:**
- ✅ Distance > 100px? (Хорошо, видно)
- ❌ Distance < 10px? (Проблема! линия как точка)
- ❌ Distance = 0? (Проблема! обе ворота на одном месте)

---

### Блок 3: Какие computed styles в браузере?
```
[DEBUG] ch_7_31 in DOM:
  computed stroke-width: 34px      ← ✅ Правильно!
  computed opacity: 1              ← ✅ Видно!
  computed display: initial        ← ✅ Не скрыто!
  computed visibility: visible     ← ✅ Видно!
  bbox: x=935.26, y=1325.52, w=0.00, h=362.03
```

**Проверяем:**

| Если видно | Проблема |
|----------|---------|
| stroke-width: 1px | Stroke-width не применился (CSS скрыл) |
| opacity: 0 | Канал скрыт (opacity = 0) |
| display: none | Канал скрыт (display) |
| visibility: hidden | Канал скрыт (visibility) |
| bbox width = 0.00 | Линия вырождается в точку |

---

## 📸 Скопировать результаты

Скопируйте из консоли:

**От этой строки:**
```
[DEBUG] === Channel elements check in SVG ===
```

**До этой строки:**
```
[DEBUG] === End DOM verification ===
```

Затем пришлите вместе со скриншотом bodygraph.

---

## 🔍 Примеры результатов

### ✅ Если проблема в координатах ворот
```
[DEBUG] BASE STYLE: ch_3_60
  distance: 207.25px

[DEBUG] ch_3_60 in DOM:
  bbox: x=1076.19, y=2797.16, w=0.00, h=0.00  ← ❌ НОЛЬ размер!
```
**→ Координаты ворот 3 и 60 неверные в gateCoords**

### ❌ Если проблема в CSS
```
[DEBUG] ch_7_31 in DOM:
  attr stroke-width: 34
  computed stroke-width: 2px  ← ❌ CSS переписал с 34px на 2px!
```
**→ Какое-то CSS-правило скрывает stroke-width**

### ❌ Если проблема в исходном path
```
[DEBUG] BASE STYLE: ch_7_31
  distance: 362.03px  ← хорошее расстояние

[DEBUG] ch_7_31 in DOM:
  bbox: x=935.26, y=1325.52, w=0.03, h=0.00  ← неправильный path в SVG
```
**→ Исходный path в BODY-02-colored.svg неверный**

---

## ✅ Чеклист перед отправкой

- [ ] Hard Refresh выполнен
- [ ] Console открыта
- [ ] Дата введена (24.01.1922, 07:25, UTC+3)
- [ ] Логи видны в console
- [ ] Все логи скопированы (от `[DEBUG] === Channel...` до конца)
- [ ] Скриншот bodygraph (видны ли каналы визуально)
- [ ] Готово к отправке

---

**Время:** 5 минут
**Сложность:** ⭐ Очень просто
**Полный гайд:** смотрите [`GEOMETRY_DEBUG.md`](GEOMETRY_DEBUG.md)
