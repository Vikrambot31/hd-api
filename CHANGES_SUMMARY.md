# Изменения для диагностики проблемы отрисовки каналов

## Дата внедрения
2026-04-06

## Что было изменено

### 1. **bodygraph_renderer.js** — добавлено debug-логирование
**Строки 182-186:** Логирование цветов ворот для трех проблемных каналов
```javascript
// DEBUG: логируем три проблемных канала
const isDebugChannel = FORCE_EXACT_PATH_CHANNELS.has(chId);
if (isDebugChannel) {
  console.log(`[DEBUG] ${chId}: ca=${ca}, cb=${cb}`);
}
```

**Строки 204-210:** Логирование параметров в режиме "solid color"
```javascript
if (isDebugChannel) {
  console.log(`[DEBUG] ${chId}: same color mode`);
  console.log(`  stroke: ${stroke}`);
  console.log(`  stroke-width: ${CHANNEL_STROKE_WIDTH}`);
  console.log(`  filter: url(#activeGlow)`);
  console.log(`  d: ${pathEl.getAttribute('d')}`);
}
```

**Строки 239-248:** Логирование параметров в режиме "gradient"
```javascript
if (isDebugChannel) {
  console.log(`[DEBUG] ${chId}: gradient mode`);
  console.log(`  c1: ${c1} (gate ${a})`);
  console.log(`  c2: ${c2} (gate ${b})`);
  console.log(`  stroke: ${strokeUrl}`);
  console.log(`  stroke-width: ${CHANNEL_STROKE_WIDTH}`);
  console.log(`  filter: url(#activeGlow)`);
  console.log(`  gradient from (${x1},${y1}) to (${x2},${y2})`);
  console.log(`  d: ${pathEl.getAttribute('d')}`);
}
```

**Строки 336-356:** DOM-верификация после вставки SVG в контейнер
```javascript
// DEBUG: проверяем, что данные реально в DOM после вставки
console.log('[DEBUG] === DOM verification after SVG insertion ===');
for (const chId of Array.from(FORCE_EXACT_PATH_CHANNELS)) {
  const pathEl = svgEl.querySelector(`[id="${chId}"]`);
  if (pathEl) {
    const stroke = pathEl.getAttribute('stroke');
    const strokeWidth = pathEl.getAttribute('stroke-width');
    const filter = pathEl.getAttribute('filter');
    const d = pathEl.getAttribute('d');
    const computedStroke = window.getComputedStyle(pathEl).stroke;
    const computedStrokeWidth = window.getComputedStyle(pathEl).strokeWidth;
    console.log(`[DEBUG] ${chId} in DOM:`);
    console.log(`  attr stroke: ${stroke}`);
    console.log(`  attr stroke-width: ${strokeWidth}`);
    console.log(`  attr filter: ${filter}`);
    console.log(`  attr d: ${d}`);
    console.log(`  computed stroke: ${computedStroke}`);
    console.log(`  computed stroke-width: ${computedStrokeWidth}`);
  }
}
console.log('[DEBUG] === End DOM verification ===');
```

### 2. **calculator_web.html** — обновлена версия скрипта
**Строка 455:** Версия изменена с `v=20260406-02` на `v=20260406-debug`
```html
<!-- ДО -->
<script src="bodygraph_renderer.js?v=20260406-02"></script>

<!-- ПОСЛЕ -->
<script src="bodygraph_renderer.js?v=20260406-debug"></script>
```
**Причина:** Обеспечить очистку кэша браузера при загрузке новой версии скрипта.

### 3. Созданы документы помощи
- `QUICK_START.txt` — быстрый старт (1 минута)
- `DEBUG_INSTRUCTIONS.md` — полная инструкция с объяснением
- `DIAGNOSTIC_CHECKLIST.md` — чеклист для проверки каждого блока
- `CHANGES_SUMMARY.md` — этот файл

---

## Логируемые каналы
Логирование включено **ТОЛЬКО** для трех каналов:
- ✓ `ch_1_8` (ворота 1 и 8)
- ✓ `ch_7_31` (ворота 7 и 31)
- ✓ `ch_46_29` (ворота 46 и 29)

Все остальные 33 канала не логируются (чтобы не засорить консоль).

---

## Как запустить тест

### Вариант 1: Быстро (5 минут)
```bash
1. Hard refresh: Ctrl+Shift+R (Windows/Linux) или Cmd+Shift+R (Mac)
2. Открыть DevTools: F12 → Console
3. Ввести дату: 24.01.1922, 07:25, UTC+3
4. Нажать "Рассчитать карту"
5. Скопировать логи из консоли
```

### Вариант 2: С инструкцией
- Смотрите файл `QUICK_START.txt`

### Вариант 3: С полной диагностикой
- Смотрите файл `DEBUG_INSTRUCTIONS.md`

---

## Ожидаемый вывод консоли

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
  computed stroke: rgb(204, 34, 0)  // или другое значение в зависимости от браузера
  computed stroke-width: 34px

[DEBUG] ch_7_31 in DOM:
  attr stroke: #111111
  attr stroke-width: 34
  attr filter: url(#activeGlow)
  attr d: M935.26,1687.55 L930.62,1325.52
  computed stroke: rgb(17, 17, 17)
  computed stroke-width: 34px

[DEBUG] ch_46_29 in DOM:
  attr stroke: url(#grad_ch_46_29)
  attr stroke-width: 34
  attr filter: url(#activeGlow)
  attr d: M1207.19,1924.23 L1216.1,2519.65
  computed stroke: rgb(204, 34, 0)
  computed stroke-width: 34px

[DEBUG] === End DOM verification ===
```

---

## Что проверять в логах

| Что | Ожидаемое | Если другое | Вероятная причина |
|-----|-----------|-----------|-----------------|
| `ca=` для ch_1_8 | `black` | `null` / `red` | Gate 1 не в personality |
| `cb=` для ch_1_8 | `null` | `black` / `red` | Gate 8 активна (не должна быть) |
| stroke для ch_1_8 | `url(#grad_ch_1_8)` | `#...` или другой | Градиент не создан |
| stroke-width | `34` | другое число | CHANNEL_STROKE_WIDTH переписан |
| filter | `url(#activeGlow)` | `none` / отсутствует | Фильтр не применился |
| d (path) | `M1080.84,1601.94 L1082,1329` | `M...M...` или сложно | Путь неверный (зависит от FORCE_EXACT_PATH) |

---

## Если логи не видны

### Возможная причина 1: Кэш браузера
**Решение:**
```
Hard Refresh: Ctrl+Shift+R (Windows) или Cmd+Shift+R (Mac)
```

### Возможная причина 2: Консоль очищена
**Решение:**
```
- Перезагрузить страницу (F5)
- Запустить расчет заново
```

### Возможная причина 3: Скрипт не загрузился
**Решение:**
1. Откройте DevTools → Network
2. Найдите запрос `bodygraph_renderer.js?v=20260406-debug`
3. Проверьте статус (должен быть 200, не 304)
4. Если 304 → Hard Refresh еще раз

---

## Удаление debug-кода (после диагностики)

Когда проблема будет найдена и исправлена:

### Быстрое удаление (не трогая код)
Просто поменять версию в HTML обратно на финальную:
```html
<script src="bodygraph_renderer.js?v=20260406-final"></script>
```

### Полное удаление (очистка кода)
Удалить из `bodygraph_renderer.js`:
1. Все блоки `if (isDebugChannel) { console.log(...) }`
2. Весь блок DOM verification (строки 336-356)
3. Переменную `const isDebugChannel = ...`
4. Переменную `const strokeUrl = ...` (заменить обратно на прямой stroke)

---

## Контрольный список перед запуском

- [ ] Вы открыли файл через HTTP-сервер (не как `file://`)
- [ ] Вы нажали Hard Refresh (Ctrl+Shift+R)
- [ ] Вы открыли DevTools → Console
- [ ] Вы ввели тестовую дату: 24.01.1922, 07:25, UTC+3
- [ ] Вы нажали "Рассчитать карту"
- [ ] Вы видите логи в консоли (начинаются с `PERS:` и `DES:`)

---

## Если нужна дополнительная помощь

1. **Скопируйте весь блок логов** (от `PERS:` до `[DEBUG] === End DOM verification ===`)
2. **Сделайте скриншот** страницы (как выглядят каналы визуально)
3. **Откройте DevTools → Elements** и инспектируйте один из каналов:
   - Правая кнопка на линии канала → Inspect
   - Посмотрите, какие CSS-правила применены (Styles panel)
4. **Опишите проблему:**
   - Какие логи вы видели?
   - Что ожидали → что получили?
   - Как это выглядит визуально?

---

## История версий

| Версия | Дата | Изменение |
|--------|------|-----------|
| v=20260406-02 | - | Базовая версия с FORCE_EXACT_PATH_CHANNELS |
| v=20260406-debug | 2026-04-06 | **← ТЕКУЩАЯ** Добавлено debug-логирование |
| v=20260406-final | TBD | После диагностики и исправления |

---

## Документы в папке

```
web_calculator/
├── bodygraph_renderer.js       ← ОБНОВЛЕН (с логами)
├── calculator_web.html         ← ОБНОВЛЕН (версия +debug)
├── BODY-02-colored.svg         (не менялся)
├── fullhd_data.js              (не менялся)
├── hd_engine.js                (не менялся)
├── QUICK_START.txt             ← НОВЫЙ (этап 1)
├── DEBUG_INSTRUCTIONS.md       ← НОВЫЙ (этап 2)
├── DIAGNOSTIC_CHECKLIST.md     ← НОВЫЙ (этап 3)
└── CHANGES_SUMMARY.md          ← ЭТОТ ФАЙЛ
```

---

**Автор:** Claude (AI Assistant)
**Версия:** 1.0
**Статус:** Готово к тестированию
