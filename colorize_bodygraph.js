// colorize_bodygraph.js
const fs = require('fs');

const conscious   = [1, 8, 57, 34];
const unconscious = [48, 16, 20, 10];

const channelMap = {
  'ch_34_20':  [34, 20],
  'ch_57_20':  [57, 20],
  'ch_1_8':    [1,  8],
  'ch_2_14':   [2,  14],
  'ch_7_31':   [7,  31],
  'ch_9_52':   [9,  52],
  'ch_10_20':  [10, 20],
  'ch_13_33':  [13, 33],
  'ch_15_5':   [15, 5],
  'ch_19_49':  [19, 49],
  'ch_22_12':  [22, 12],
  'ch_23_43':  [23, 43],
  'ch_25_51':  [25, 51],
  'ch_26_44':  [26, 44],
  'ch_27_50':  [27, 50],
  'ch_32_54':  [32, 54],
  'ch_35_36':  [35, 36],
  'ch_38_28':  [38, 28],
  'ch_40_37':  [40, 37],
  'ch_41_30':  [41, 30],
  'ch_42_53':  [42, 53],
  'ch_45_21':  [45, 21],
  'ch_46_29':  [46, 29],
  'ch_48_16':  [48, 16],
  'ch_55_39':  [55, 39],
  'ch_56_11':  [56, 11],
  'ch_57_10':  [57, 10],
  'ch_57_34':  [57, 34],
  'ch_58_18':  [58, 18],
  'ch_59_6':   [59, 6],
  'ch_60_3':   [60, 3],
  'ch_61_24':  [61, 24],
  'ch_62_17':  [62, 17],
  'ch_63_4':   [63, 4],
  'ch_64_47':  [64, 47],
};

const gateCoords = {
  1:  [1080.84, 1601.94],
  2:  [1082,    2019],
  3:  [1076.19, 2797.16],
  4:  [1298.93, 446.32],
  5:  [965.45,  2507.7],
  6:  [1666.26, 2566.03],
  7:  [935.26,  1687.55],
  8:  [1082,    1329],
  9:  [1188.61, 2799.87],
  10: [860.97,  1813.84],
  11: [1217.2,  640.16],
  12: [1303.51, 1165.93],
  13: [1203.71, 1677.1],
  14: [1095.93, 2514.74],
  15: [944.55,  1931.19],
  16: [887.42,  1034.97],
  17: [983.65,  637.84],
  18: [85.61,   2743.1],
  19: [1269.39, 3053.68],
  20: [891.68,  1186.74],
  21: [1614,    2074],
  22: [1980,    2471],
  23: [1087.81, 976.55],
  24: [1082,    444],
  25: [1315.48, 1820.32],
  26: [1375.32, 2187.74],
  27: [886.84,  2663.52],
  28: [228.52,  2681.26],
  29: [1216.1,  2519.65],
  30: [2105.35, 2733.68],
  31: [930.62,  1325.52],
  32: [397.42,  2613.29],
  33: [1200.22, 1334.81],
  34: [885.29,  2537.09],
  35: [1314.68, 1013.16],
  36: [2097,    2423],
  37: [1853,    2514],
  38: [933,     3172],
  39: [1276.35, 3159.84],
  40: [1563.58, 2295.81],
  41: [1246.16, 3263],
  42: [955,     2796.55],
  43: [1101.74, 769.03],
  44: [350.97,  2500.13],
  45: [1293.35, 1276],
  46: [1207.19, 1924.23],
  47: [891.13,  448.64],
  48: [73.43,   2392.1],
  49: [1786,    2604],
  50: [532.71,  2568.74],
  51: [1505,    2100],
  52: [1175,    3004],
  53: [972.44,  3013.43],
  54: [911.32,  3071.94],
  55: [1947.68, 2675.58],
  56: [1200.22, 985.68],
  57: [214.84,  2453.74],
  58: [935,     3265],
  59: [1272.71, 2657.71],
  60: [1082,    3004],
  61: [1081.23, 248],
  62: [981.7,   976.53],
  63: [1286.16, 248],
  64: [893.46,  248],
};

function gateColor(id) {
  if (conscious.includes(id))   return 'black';
  if (unconscious.includes(id)) return 'red';
  return null;
}

const HEX = {
  black: '#111111',
  red:   '#cc2200',
  grey:  '#888888',
};

function findPathTag(svg, svgId) {
  const idStr = `id="${svgId}"`;
  const idPos = svg.indexOf(idStr);
  if (idPos === -1) return null;
  const tagStart = svg.lastIndexOf('<path', idPos);
  if (tagStart === -1) return null;
  const tagEnd = svg.indexOf('/>', idPos);
  if (tagEnd === -1) return null;
  return {
    full:  svg.slice(tagStart, tagEnd + 2),
    start: tagStart,
    end:   tagEnd + 2,
  };
}

let svg = fs.readFileSync('BODY-02-colored.svg', 'utf8');

let gradientDefs = '';

// 1) Перекраска каналов
for (const [svgId, [a, b]] of Object.entries(channelMap)) {
  const ca = gateColor(a);
  const cb = gateColor(b);
  if (!ca && !cb) continue;

  const found = findPathTag(svg, svgId);
  if (!found) {
    console.log(`⚠  НЕ НАЙДЕН: ${svgId}`);
    continue;
  }

  const { full: fullTag, start: tagStart, end: tagEnd } = found;
  const [x1, y1] = gateCoords[a];
  const [x2, y2] = gateCoords[b];

  let newStroke;

  if (ca && cb && ca === cb) {
    newStroke = HEX[ca];
  } else {
    const gradId = `grad_${svgId}`;
    const c1 = HEX[ca || 'grey'];
    const c2 = HEX[cb || 'grey'];
    gradientDefs +=
      `<linearGradient id="${gradId}" ` +
      `x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" ` +
      `gradientUnits="userSpaceOnUse">` +
      `<stop offset="0%"   stop-color="${c1}"/>` +
      `<stop offset="50%"  stop-color="${c1}"/>` +
      `<stop offset="50%"  stop-color="${c2}"/>` +
      `<stop offset="100%" stop-color="${c2}"/>` +
      `</linearGradient>`;
    newStroke = `url(#${gradId})`;
  }

  const newTag = fullTag.replace(/stroke="[^"]*"/, `stroke="${newStroke}"`);
  svg = svg.slice(0, tagStart) + newTag + svg.slice(tagEnd);
}

// 2) Вставляем градиенты
if (gradientDefs) {
  svg = svg.replace('</svg>', `<defs>${gradientDefs}</defs>\n</svg>`);
}

// 3) Перекраска кружков ворот
for (const [gateIdStr, [cx, cy]] of Object.entries(gateCoords)) {
  const gateId = Number(gateIdStr);
  const color = gateColor(gateId);
  if (!color) continue;

  const fillColor = color === 'black' ? '#111111' : '#cc2200';
  const textColor = color === 'black' ? '#ffffff'  : '#111111';

  // Перекрашиваем circle
  svg = svg.replace(
    new RegExp(`(<circle cx="${cx}" cy="${cy}"[^>]*?)fill="[^"]*"`, 'g'),
    `$1fill="${fillColor}"`
  );

  // Перекрашиваем текст цифры внутри следующего <text> после circle
  const circlePos = svg.indexOf(`cx="${cx}" cy="${cy}"`);
  if (circlePos === -1) continue;
  const textPos = svg.indexOf('<text', circlePos);
  if (textPos === -1) continue;
  const textEnd = svg.indexOf('</text>', textPos) + 7;
  let textBlock = svg.slice(textPos, textEnd);
  textBlock = textBlock.replace(/fill="[^"]*"/, `fill="${textColor}"`);
  svg = svg.slice(0, textPos) + textBlock + svg.slice(textEnd);
}

fs.writeFileSync('BODY-02-colored.svg', svg);
console.log('✓ Готово → BODY-02-colored.svg');
