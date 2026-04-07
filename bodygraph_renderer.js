// bodygraph_renderer.js

const gateCoords = {
  1:  [1080.84, 1601.94], 2:  [1082, 2019],      3:  [1076.19, 2797.16],
  4:  [1298.93, 446.32],  5:  [965.45, 2507.7],   6:  [1666.26, 2566.03],
  7:  [935.26, 1687.55],  8:  [1082, 1329],        9:  [1188.61, 2799.87],
  10: [860.97, 1813.84],  11: [1217.2, 640.16],   12: [1303.51, 1165.93],
  13: [1203.71, 1677.1],  14: [1095.93, 2514.74], 15: [944.55, 1931.19],
  16: [887.42, 1034.97],  17: [983.65, 637.84],   18: [85.61, 2743.1],
  19: [1269.39, 3053.68], 20: [891.68, 1186.74],  21: [1614, 2074],
  22: [1980, 2471],       23: [1087.81, 976.55],  24: [1082, 444],
  25: [1315.48, 1820.32], 26: [1375.32, 2187.74], 27: [886.84, 2663.52],
  28: [228.52, 2681.26],  29: [1216.1, 2519.65],  30: [2105.35, 2733.68],
  31: [930.62, 1325.52],  32: [397.42, 2613.29],  33: [1200.22, 1334.81],
  34: [885.29, 2537.09],  35: [1314.68, 1013.16], 36: [2097, 2423],
  37: [1853, 2514],       38: [933, 3172],         39: [1276.35, 3159.84],
  40: [1563.58, 2295.81], 41: [1246.16, 3263],     42: [955, 2796.55],
  43: [1101.74, 769.03],  44: [350.97, 2500.13],  45: [1293.35, 1276],
  46: [1207.19, 1924.23], 47: [891.13, 448.64],   48: [73.43, 2392.1],
  49: [1786, 2604],       50: [532.71, 2568.74],  51: [1505, 2100],
  52: [1175, 3004],       53: [972.44, 3013.43],  54: [911.32, 3071.94],
  55: [1947.68, 2675.58], 56: [1200.22, 985.68],  57: [214.84, 2453.74],
  58: [935, 3265],        59: [1272.71, 2657.71], 60: [1082, 3004],
  61: [1081.23, 248],     62: [981.7, 976.53],    63: [1286.16, 248],
  64: [893.46, 248],
};

const channelMap = {
  'ch_34_20': [34,20], 'ch_57_20': [57,20], 'ch_1_8':   [1,8],
  'ch_2_14':  [2,14],  'ch_7_31':  [7,31],  'ch_9_52':  [9,52],
  'ch_10_20': [10,20], 'ch_10_34': [10,34], 'ch_13_33': [13,33], 'ch_15_5':  [15,5],
  'ch_19_49': [19,49], 'ch_22_12': [22,12], 'ch_23_43': [23,43],
  'ch_25_51': [25,51], 'ch_26_44': [26,44], 'ch_27_50': [27,50],
  'ch_32_54': [32,54], 'ch_35_36': [35,36], 'ch_38_28': [38,28],
  'ch_40_37': [40,37], 'ch_41_30': [41,30], 'ch_42_53': [42,53],
  'ch_45_21': [45,21], 'ch_46_29': [46,29], 'ch_48_16': [48,16],
  'ch_55_39': [55,39], 'ch_56_11': [56,11], 'ch_57_10': [57,10],
  'ch_57_34': [57,34], 'ch_58_18': [58,18], 'ch_59_6':  [59,6],
  'ch_60_3':  [60,3],  'ch_61_24': [61,24], 'ch_62_17': [62,17],
  'ch_63_4':  [63,4],  'ch_64_47': [64,47],
};

const HEX = { black: '#111111', red: '#cc2200', grey: '#888888' };
const BODYGRAPH_SVG_PATH = 'BODY-02-colored.svg';
const CHANNEL_STROKE_WIDTH = '34';
const CHANNEL_BASE_STROKE = '#7f89ad';
const OUTLINE_STROKE = '#111111';
const CHANNEL_GLOW_FILTER_ID = 'definedChannelGlow';
const CENTER_GLOW_FILTER_ID = 'definedCenterGlow';
const FORCE_EXACT_PATH_CHANNELS = new Set(['ch_1_8', 'ch_7_31', 'ch_46_29']);
const PRIORITY_GATES = new Set([10, 20, 34, 57]);
const PRIORITY_GATE_ALLOWED_HANGING_CHANNEL = new Map([
  [10, 'ch_57_10'],
  [20, 'ch_10_20'],
  [34, 'ch_10_34'],
  [57, 'ch_57_10'],
]);

function canonicalChannelKey(a, b) {
  return `${Math.min(a, b)}-${Math.max(a, b)}`;
}

function normalizeGateArray(gates) {
  if (!Array.isArray(gates)) return [];
  return gates
    .map(g => Number(g))
    .filter(g => Number.isFinite(g));
}

function gateColorFromSets(id, conscious, unconscious) {
  if (conscious.has(id))   return 'black';
  if (unconscious.has(id)) return 'red';
  return null;
}

function findCircleByCoords(svgDoc, cx, cy) {
  const circles = svgDoc.querySelectorAll('circle');
  for (const c of circles) {
    if (Math.abs(parseFloat(c.getAttribute('cx')) - cx) < 0.5 &&
        Math.abs(parseFloat(c.getAttribute('cy')) - cy) < 0.5) {
      return c;
    }
  }
  return null;
}

function upsertGlowFilter(svgDoc, defs, filterId, markup) {
  const existing = defs.querySelector(`#${filterId}`);
  if (existing) existing.remove();

  const filter = svgDoc.createElementNS('http://www.w3.org/2000/svg', 'filter');
  filter.setAttribute('id', filterId);
  filter.setAttribute('filterUnits', 'userSpaceOnUse');
  filter.setAttribute('x', '-500');
  filter.setAttribute('y', '-500');
  filter.setAttribute('width', '3200');
  filter.setAttribute('height', '4600');
  filter.innerHTML = markup;
  defs.appendChild(filter);
}

function findTextAfterCircle(circle) {
  // следующий <g> после circle содержит <text>
  let el = circle.nextElementSibling;
  while (el) {
    const t = el.querySelector('text') || (el.tagName === 'text' ? el : null);
    if (t) return t;
    el = el.nextElementSibling;
  }
  return null;
}

function showBodygraphMessage(container, message, isError = false) {
  container.innerHTML = `<div class="bodygraph-status${isError ? ' error' : ''}">${message}</div>`;
  container.classList.toggle('is-error', isError);
}

const CENTER_TOOLTIP_CONTENT = {
  'Head': {
    title: 'Теменной центр',
    lines: [
      'Почему у меня нет идей?',
      'Как найти правильную мысль?',
      'Что мне нужно обдумывать сейчас?',
      'Почему у других есть вдохновение, а у меня нет?'
    ]
  },
  'Ajna': {
    title: 'Аджна центр',
    lines: [
      'Какая точка зрения правильная?',
      'Как мне быть уверенным в своем мнении?',
      'Почему я постоянно сомневаюсь?',
      'Как мне все разложить по полочкам?'
    ]
  },
  'Throat': {
    title: 'Центр горла',
    lines: [
      'Что мне сказать, чтобы меня заметили?',
      'Как говорить правильно?',
      'Почему меня не слушают?',
      'Как привлечь внимание словами?'
    ]
  },
  'G-Center': {
    title: 'Джи центр',
    lines: [
      'Кто я на самом деле?',
      'Куда мне идти?',
      'В чем смысл моей жизни?',
      'Почему у меня нет направления?'
    ]
  },
  'Heart': {
    title: 'Эго центр',
    lines: [
      'Чего я стою?',
      'Как доказать свою ценность?',
      'Почему я недостаточно хорош?',
      'Как добиться признания?'
    ]
  },
  'Solar Plexus': {
    title: 'Центр солнечного сплетения',
    lines: [
      'Что я должен чувствовать?',
      'Почему мои эмоции нестабильны?',
      'Как стать эмоционально правильным?',
      'Почему я не чувствую, как другие?'
    ]
  },
  'Sacral': {
    title: 'Сакральный центр',
    lines: [
      'Где взять энергию?',
      'Почему у меня нет сил?',
      'Как понять, когда действовать?',
      'Почему я не могу работать постоянно?'
    ]
  },
  'Spleen': {
    title: 'Центр селезенки',
    lines: [
      'Чего мне бояться?',
      'Как избежать опасности?',
      'Почему я тревожусь?',
      'Как почувствовать безопасность?'
    ]
  },
  'Root': {
    title: 'Корневой центр',
    lines: [
      'Когда мне нужно действовать?',
      'Почему я все время спешу?',
      'Как избавиться от давления?',
      'Когда это напряжение закончится?'
    ]
  }
};

const GATE_TOOLTIP_CONTENT = {
  title: 'Важно!',
  lines: [
    'Каждые ворота нужно читать с Центром, Профилем, Линией, см. Полярности и т. д.'
  ]
};

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function ensureBodygraphTooltip(container) {
  let tooltip = container.querySelector('.bodygraph-tooltip');
  if (tooltip) return tooltip;

  tooltip = document.createElement('div');
  tooltip.className = 'bodygraph-tooltip';
  container.appendChild(tooltip);
  return tooltip;
}

function setBodygraphTooltipContent(tooltip, content) {
  const itemsHtml = content.lines
    .map(line => `<li>${escapeHtml(line)}</li>`)
    .join('');

  tooltip.innerHTML = `
    <div class="bodygraph-tooltip-title">${escapeHtml(content.title)}</div>
    <ul class="bodygraph-tooltip-list">${itemsHtml}</ul>`;
}

function updateTooltipPosition(container, tooltip, clientX, clientY) {
  const containerRect = container.getBoundingClientRect();
  const tooltipRect = tooltip.getBoundingClientRect();
  const offset = 18;

  let left = clientX - containerRect.left + offset;
  let top = clientY - containerRect.top + offset;

  const maxLeft = Math.max(12, container.clientWidth - tooltipRect.width - 12);
  const maxTop = Math.max(12, container.clientHeight - tooltipRect.height - 12);

  left = Math.min(Math.max(12, left), maxLeft);
  top = Math.min(Math.max(12, top), maxTop);

  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${top}px`;
}

function attachCenterTooltips(svgEl, container, centerIdMap, definedCentersSet) {
  const tooltip = ensureBodygraphTooltip(container);

  const showTooltip = (centerKey, event) => {
    const content = CENTER_TOOLTIP_CONTENT[centerKey];
    if (!content) return;

    setBodygraphTooltipContent(tooltip, content);
    tooltip.classList.add('visible');
    updateTooltipPosition(container, tooltip, event.clientX, event.clientY);
  };

  const hideTooltip = () => {
    tooltip.classList.remove('visible');
  };

  for (const [centerKey, svgId] of Object.entries(centerIdMap)) {
    const el = svgEl.querySelector(`[id="${svgId}"]`);
    if (!el) continue;

    if (definedCentersSet.has(centerKey)) {
      el.style.cursor = 'default';
      el.removeAttribute('tabindex');
      continue;
    }

    el.style.cursor = 'help';
    el.setAttribute('tabindex', '0');

    el.addEventListener('mouseenter', event => showTooltip(centerKey, event));
    el.addEventListener('mousemove', event => updateTooltipPosition(container, tooltip, event.clientX, event.clientY));
    el.addEventListener('mouseleave', hideTooltip);
    el.addEventListener('focus', () => {
      const rect = el.getBoundingClientRect();
      showTooltip(centerKey, { clientX: rect.left + rect.width / 2, clientY: rect.top + rect.height / 2 });
    });
    el.addEventListener('blur', hideTooltip);
  }
}

function attachGateTooltips(svgEl, container) {
  const tooltip = ensureBodygraphTooltip(container);

  const showTooltip = event => {
    setBodygraphTooltipContent(tooltip, GATE_TOOLTIP_CONTENT);
    tooltip.classList.add('visible');
    updateTooltipPosition(container, tooltip, event.clientX, event.clientY);
  };

  const hideTooltip = () => {
    tooltip.classList.remove('visible');
  };

  for (const [gateId, [cx, cy]] of Object.entries(gateCoords)) {
    const circle = findCircleByCoords(svgEl, cx, cy);
    const text = circle ? findTextAfterCircle(circle) : null;
    const hoverTargets = [circle, text].filter(Boolean);

    for (const target of hoverTargets) {
      target.style.cursor = 'help';
      target.setAttribute('data-gate-id', String(gateId));
      target.addEventListener('mouseenter', showTooltip);
      target.addEventListener('mousemove', event => updateTooltipPosition(container, tooltip, event.clientX, event.clientY));
      target.addEventListener('mouseleave', hideTooltip);
    }
  }
}

async function renderBodygraph(conscious, unconscious, containerId, definedCenters = [], definedChannels = []) {
  // conscious, unconscious — массивы номеров ворот
  const container = document.getElementById(containerId);
  if (!container) {
    throw new Error(`Container not found: ${containerId}`);
  }

  container.classList.remove('is-error');

  if (window.location.protocol === 'file:') {
    throw new Error('BODYGRAPH не может загрузиться из файла напрямую. Откройте calculator_web.html через локальный HTTP-сервер.');
  }

  const consciousGates = normalizeGateArray(conscious);
  const unconsciousGates = normalizeGateArray(unconscious);
  console.log('PERS:', consciousGates);
  console.log('DES:', unconsciousGates);
  const persSet = new Set(consciousGates);
  const desSet  = new Set(unconsciousGates);

  const response = await fetch(new URL(BODYGRAPH_SVG_PATH, window.location.href));
  if (!response.ok) {
    throw new Error(`Не удалось загрузить ${BODYGRAPH_SVG_PATH}: HTTP ${response.status}`);
  }
  const svgText  = await response.text();
  const parser   = new DOMParser();
  const svgDoc   = parser.parseFromString(svgText, 'image/svg+xml');
  const parseError = svgDoc.querySelector('parsererror');
  if (parseError) {
    throw new Error(`SVG ${BODYGRAPH_SVG_PATH} поврежден или содержит ошибки XML.`);
  }
  const svgEl    = svgDoc.querySelector('svg');
  if (!svgEl) {
    throw new Error(`В файле ${BODYGRAPH_SVG_PATH} не найден корневой тег <svg>.`);
  }

  // Добавляем фильтр glow в defs
  let defs = svgEl.querySelector('defs');
  if (!defs) {
    defs = svgDoc.createElementNS('http://www.w3.org/2000/svg','defs');
    svgEl.prepend(defs);
  }
  // Важно: objectBoundingBox клиппит узкие вертикальные каналы (например 1-8, 7-31)
  // и визуально делает их тонкими. Используем userSpaceOnUse с большим регионом.
  upsertGlowFilter(svgDoc, defs, CHANNEL_GLOW_FILTER_ID, `
    <feDropShadow dx="0" dy="0" stdDeviation="7" flood-color="#ffffff" flood-opacity="0.28"/>
    <feDropShadow dx="0" dy="0" stdDeviation="3.4" flood-color="#ffd889" flood-opacity="0.38"/>
    <feDropShadow dx="0" dy="0" stdDeviation="1.4" flood-color="#fff6db" flood-opacity="0.72"/>`);
  upsertGlowFilter(svgDoc, defs, CENTER_GLOW_FILTER_ID, `
    <feDropShadow dx="0" dy="0" stdDeviation="18" flood-color="#fff0b8" flood-opacity="0.22"/>
    <feDropShadow dx="0" dy="0" stdDeviation="9" flood-color="#ffd36a" flood-opacity="0.30"/>
    <feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="#fff8e6" flood-opacity="0.42"/>`);

  // DEBUG: список всех каналов - проверяем, какие нашлись в SVG
  console.log('[DEBUG] === Channel elements check in SVG ===');
  const foundChannels = [];
  const missingChannels = [];
  for (const [chId, [a, b]] of Object.entries(channelMap)) {
    let pathEl = svgEl.querySelector(`[id="${chId}"]`);
    const origFound = !!pathEl;
    if (!pathEl) {
      const revEl = svgEl.querySelector(`[id="ch_${b}_${a}"]`);
      if (revEl) {
        revEl.setAttribute('id', chId);
        pathEl = revEl;
      }
    }
    if (pathEl) {
      foundChannels.push(chId);
    } else {
      missingChannels.push(chId);
    }
  }
  console.log(`[DEBUG] Found in SVG: ${foundChannels.length}/36`);
  if (missingChannels.length > 0) {
    console.log(`[DEBUG] ⚠️  MISSING: ${missingChannels.join(', ')}`);
  }

  // Единый базовый стиль всех каналов
  for (const [chId, [a, b]] of Object.entries(channelMap)) {
    let pathEl = svgEl.querySelector(`[id="${chId}"]`);
    if (!pathEl) {
      const revEl = svgEl.querySelector(`[id="ch_${b}_${a}"]`);
      if (revEl) {
        revEl.setAttribute('id', chId);
        pathEl = revEl;
      }
    }
    if (pathEl) {
      const origD = pathEl.getAttribute('d');
      if (FORCE_EXACT_PATH_CHANNELS.has(chId)) {
        const [x1, y1] = gateCoords[a];
        const [x2, y2] = gateCoords[b];
        pathEl.setAttribute('d', `M${x1},${y1} L${x2},${y2}`);
        console.log(`[DEBUG] FORCE: ${chId} - forced exact path`);
      }

      pathEl.setAttribute('fill', 'none');
      pathEl.setAttribute('stroke', CHANNEL_BASE_STROKE);
      pathEl.setAttribute('stroke-opacity', '1');
      pathEl.setAttribute('stroke-width', CHANNEL_STROKE_WIDTH);
      pathEl.setAttribute('stroke-linecap', 'butt');
      pathEl.setAttribute('stroke-linejoin', 'round');
      pathEl.setAttribute('shape-rendering', 'geometricPrecision');
      pathEl.removeAttribute('vector-effect');
      pathEl.removeAttribute('filter');

      // DEBUG: логируем параметры базового стиля для проблемных каналов
      if (FORCE_EXACT_PATH_CHANNELS.has(chId)) {
        const [x1, y1] = gateCoords[a];
        const [x2, y2] = gateCoords[b];
        const pathLen = Math.sqrt((x2-x1)**2 + (y2-y1)**2);
        console.log(`[DEBUG] BASE STYLE: ${chId}`);
        console.log(`  gate ${a} coords: (${x1}, ${y1})`);
        console.log(`  gate ${b} coords: (${x2}, ${y2})`);
        console.log(`  distance: ${pathLen.toFixed(2)}px`);
        console.log(`  stroke-width: ${CHANNEL_STROKE_WIDTH}`);
      }
    }
  }
  console.log('[DEBUG] === End channel check ===');

  // 1b) Перекраска активных каналов
  // Правило приоритета для специальных ворот:
  // если по воротам уже есть полностью определенный канал,
  // половинки от этих ворот на других каналах не рисуем.
  const fullChannelByGate = new Map();
  for (const gate of PRIORITY_GATES) {
    fullChannelByGate.set(gate, false);
  }
  for (const [ga, gb] of Object.values(channelMap)) {
    const cga = gateColorFromSets(ga, persSet, desSet);
    const cgb = gateColorFromSets(gb, persSet, desSet);
    if (!cga || !cgb) continue;
    if (PRIORITY_GATES.has(ga)) fullChannelByGate.set(ga, true);
    if (PRIORITY_GATES.has(gb)) fullChannelByGate.set(gb, true);
  }

  const activeChannelIds = new Set();

  for (const [chId, [a, b]] of Object.entries(channelMap)) {
    const ca = gateColorFromSets(a, persSet, desSet);
    const cb = gateColorFromSets(b, persSet, desSet);

    // DEBUG: логируем три проблемных канала
    const isDebugChannel = FORCE_EXACT_PATH_CHANNELS.has(chId);
    if (isDebugChannel) {
      console.log(`[DEBUG] ${chId}: ca=${ca}, cb=${cb}`);
    }

    // Если обе ворота не активны, канал остается базовым.
    if (!ca && !cb) continue;

    // Правило главного висячего канала:
    // для специальных ворот разрешаем только один half-channel по умолчанию.
    if (a !== b) {
      const halfFromA = PRIORITY_GATES.has(a) && ca && !cb;
      const halfFromB = PRIORITY_GATES.has(b) && cb && !ca;
      if (halfFromA) {
        const allowed = PRIORITY_GATE_ALLOWED_HANGING_CHANNEL.get(a);
        if (allowed && chId !== allowed) {
          continue;
        }
      }
      if (halfFromB) {
        const allowed = PRIORITY_GATE_ALLOWED_HANGING_CHANNEL.get(b);
        if (allowed && chId !== allowed) {
          continue;
        }
      }
    }

    // Общая версия правила: если по воротам уже есть полный канал,
    // "половинку" от этих ворот на других каналах не рисуем.
    if (a !== b) {
      const halfFromA = PRIORITY_GATES.has(a) && ca && !cb;
      const halfFromB = PRIORITY_GATES.has(b) && cb && !ca;
      const suppressA = halfFromA && fullChannelByGate.get(a);
      const suppressB = halfFromB && fullChannelByGate.get(b);
      if (suppressA || suppressB) {
        continue;
      }
    }


    const pathEl = svgEl.querySelector(`[id="${chId}"]`);
    if (!pathEl) {
      if (isDebugChannel) console.log(`[DEBUG] ${chId}: pathEl not found!`);
      continue;
    }

    // оба одного цвета
    if (ca === cb) {
      const stroke = HEX[ca];
      pathEl.setAttribute('stroke', stroke);
      pathEl.setAttribute('stroke-width', CHANNEL_STROKE_WIDTH);
      pathEl.setAttribute('filter', `url(#${CHANNEL_GLOW_FILTER_ID})`);
      activeChannelIds.add(chId);
      if (isDebugChannel) {
        console.log(`[DEBUG] ${chId}: same color mode`);
        console.log(`  stroke: ${stroke}`);
        console.log(`  stroke-width: ${CHANNEL_STROKE_WIDTH}`);
        console.log(`  filter: url(#${CHANNEL_GLOW_FILTER_ID})`);
        console.log(`  d: ${pathEl.getAttribute('d')}`);
      }
      continue;
    }

    // оба есть но разных цветов или один — градиент
    const c1 = HEX[ca || 'grey'];
    const c2 = HEX[cb || 'grey'];
    // Если один из них не активен, используем цвет базового канала вместо grey
    const color1 = ca ? HEX[ca] : CHANNEL_BASE_STROKE;
    const color2 = cb ? HEX[cb] : CHANNEL_BASE_STROKE;
    const [x1, y1] = gateCoords[a];
    const [x2, y2] = gateCoords[b];
    const gradId = `grad_${chId}`;
    const defs = svgEl.querySelector('defs') || svgEl.insertBefore(
      svgDoc.createElementNS('http://www.w3.org/2000/svg', 'defs'), svgEl.firstChild
    );
    const grad = svgDoc.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
    grad.setAttribute('id', gradId);
    grad.setAttribute('x1', x1); grad.setAttribute('y1', y1);
    grad.setAttribute('x2', x2); grad.setAttribute('y2', y2);
    grad.setAttribute('gradientUnits', 'userSpaceOnUse');
    grad.innerHTML =
      `<stop offset="0%"   stop-color="${color1}"/>`+
      `<stop offset="50%"  stop-color="${color1}"/>`+
      `<stop offset="50%"  stop-color="${color2}"/>`+
      `<stop offset="100%" stop-color="${color2}"/>`;
    defs.appendChild(grad);
    const strokeUrl = `url(#${gradId})`;
    pathEl.setAttribute('stroke', strokeUrl);
    pathEl.setAttribute('stroke-width', CHANNEL_STROKE_WIDTH);
    pathEl.setAttribute('filter', `url(#${CHANNEL_GLOW_FILTER_ID})`);
    activeChannelIds.add(chId);

    if (isDebugChannel) {
      console.log(`[DEBUG] ${chId}: gradient mode`);
      console.log(`  color1: ${color1} (gate ${a})`);
      console.log(`  color2: ${color2} (gate ${b})`);
      console.log(`  stroke: ${strokeUrl}`);
      console.log(`  stroke-width: ${CHANNEL_STROKE_WIDTH}`);
      console.log(`  filter: url(#${CHANNEL_GLOW_FILTER_ID})`);
      console.log(`  gradient from (${x1},${y1}) to (${x2},${y2})`);
      console.log(`  d: ${pathEl.getAttribute('d')}`);
    }
  }

  // Сброс всех кружков в белый (неопределенные ворота)
  for (const [gateIdStr, [cx, cy]] of Object.entries(gateCoords)) {
    const circle = findCircleByCoords(svgDoc, cx, cy);
    if (circle) {
      circle.setAttribute('fill', '#ffffff');
      circle.setAttribute('stroke', OUTLINE_STROKE);
      circle.setAttribute('stroke-width', '8');
    }
    const text = circle ? findTextAfterCircle(circle) : null;
    if (text) {
      text.setAttribute('fill', '#111111');
      text.querySelectorAll('tspan').forEach(ts => ts.setAttribute('fill', '#111111'));
    }
  }

  // 2) Перекраска кружков
  for (const [gateIdStr, [cx, cy]] of Object.entries(gateCoords)) {
    const gateId = Number(gateIdStr);
    const color  = gateColorFromSets(gateId, persSet, desSet);
    if (!color) continue;

    const fillColor = color === 'black' ? '#111111' : '#cc2200';
    const textColor = '#ffffff';

    const circle = findCircleByCoords(svgDoc, cx, cy);
    if (circle) {
      circle.setAttribute('fill', fillColor);
      circle.setAttribute('stroke', OUTLINE_STROKE);
    }

    const text = circle ? findTextAfterCircle(circle) : null;
    if (text) {
      text.setAttribute('fill', textColor);
      // также tspan внутри
      text.querySelectorAll('tspan').forEach(ts => ts.setAttribute('fill', textColor));
    }
  }

  // 3) Перекраска центров
  const centerIdMap = {
    'Head':         '_Центр_Темени',
    'Ajna':         '_Центр_Аджна',
    'Throat':       '_Центр_Горла',
    'G-Center':     '_Центр_Джи',
    'Heart':        '_Центр_Эго',
    'Sacral':       '_Центр_Сакрал',
    'Solar Plexus': '_Центр_Эмоций',
    'Spleen':       '_Центр_Селезенка',
    'Root':         '_Центр_Корень',
  };

  const definedCentersSet = new Set(definedCenters);

  for (const [centerKey, svgId] of Object.entries(centerIdMap)) {
    const el = svgEl.querySelector(`[id="${svgId}"]`);
    if (!el) continue;
    if (definedCentersSet.has(centerKey)) {
      // определён — оставить как есть и добавить мягкую подсветку.
      el.setAttribute('fill-opacity', '0.8');
      el.setAttribute('stroke', OUTLINE_STROKE);
      el.setAttribute('filter', `url(#${CENTER_GLOW_FILTER_ID})`);
    } else {
      // открыт — прозрачный, но тоже с мягкой подсветкой.
      el.setAttribute('fill', '#ffffff');
      el.setAttribute('fill-opacity', '1');
      el.setAttribute('stroke', OUTLINE_STROKE);
      el.setAttribute('stroke-width', '4');
      el.setAttribute('filter', `url(#${CENTER_GLOW_FILTER_ID})`);
    }
  }

  // Держим каналы поверх центров, но ниже кружков ворот и текста.
  const firstGateCircle = svgEl.querySelector('circle');
  if (firstGateCircle) {
    const baseLayer = svgDoc.createElementNS('http://www.w3.org/2000/svg', 'g');
    baseLayer.setAttribute('id', 'channel-base-layer');
    const activeLayer = svgDoc.createElementNS('http://www.w3.org/2000/svg', 'g');
    activeLayer.setAttribute('id', 'channel-active-layer');

    svgEl.insertBefore(baseLayer, firstGateCircle);
    svgEl.insertBefore(activeLayer, firstGateCircle);

    const inactiveChannelIds = [];
    const highlightedChannelIds = [];

    for (const chId of Object.keys(channelMap)) {
      if (activeChannelIds.has(chId)) {
        highlightedChannelIds.push(chId);
      } else {
        inactiveChannelIds.push(chId);
      }
    }

    for (const chId of inactiveChannelIds) {
      const pathEl = svgEl.querySelector(`[id="${chId}"]`);
      if (pathEl) {
        baseLayer.appendChild(pathEl);
      }
    }

    for (const chId of highlightedChannelIds) {
      const pathEl = svgEl.querySelector(`[id="${chId}"]`);
      if (pathEl) {
        activeLayer.appendChild(pathEl);
      }
    }
  }

  // 3) Вставляем SVG в контейнер
  container.innerHTML = '';
  svgEl.style.width  = '100%';
  svgEl.style.height = 'auto';
  container.style.position = 'relative';
  container.appendChild(svgEl);
  attachCenterTooltips(svgEl, container, centerIdMap, definedCentersSet);
  attachGateTooltips(svgEl, container);

  // DEBUG: проверяем, что данные реально в DOM после вставки
  console.log('[DEBUG] === DOM verification after SVG insertion ===');
  for (const chId of Array.from(FORCE_EXACT_PATH_CHANNELS)) {
    const pathEl = svgEl.querySelector(`[id="${chId}"]`);
    if (pathEl) {
      const stroke = pathEl.getAttribute('stroke');
      const strokeWidth = pathEl.getAttribute('stroke-width');
      const filter = pathEl.getAttribute('filter');
      const d = pathEl.getAttribute('d');
      const computedStyle = window.getComputedStyle(pathEl);
      const computedStroke = computedStyle.stroke;
      const computedStrokeWidth = computedStyle.strokeWidth;
      const computedOpacity = computedStyle.opacity;
      const computedDisplay = computedStyle.display;
      const computedVisibility = computedStyle.visibility;

      console.log(`[DEBUG] ${chId} in DOM:`);
      console.log(`  attr stroke: ${stroke}`);
      console.log(`  attr stroke-width: ${strokeWidth}`);
      console.log(`  attr filter: ${filter}`);
      console.log(`  attr d: ${d}`);
      console.log(`  computed stroke: ${computedStroke}`);
      console.log(`  computed stroke-width: ${computedStrokeWidth}`);
      console.log(`  computed opacity: ${computedOpacity}`);
      console.log(`  computed display: ${computedDisplay}`);
      console.log(`  computed visibility: ${computedVisibility}`);

      // Проверяем dimensions и bbox
      try {
        const bbox = pathEl.getBBox();
        console.log(`  bbox: x=${bbox.x.toFixed(2)}, y=${bbox.y.toFixed(2)}, w=${bbox.width.toFixed(2)}, h=${bbox.height.toFixed(2)}`);
      } catch(e) {
        console.log(`  bbox: error - ${e.message}`);
      }
    }
  }
  console.log('[DEBUG] === End DOM verification ===');
}

function renderBodygraphError(containerId, error) {
  const container = document.getElementById(containerId);
  if (!container) {
    return;
  }

  const message = error instanceof Error ? error.message : String(error || 'Неизвестная ошибка рендера BODYGRAPH.');
  showBodygraphMessage(container, message, true);
}
