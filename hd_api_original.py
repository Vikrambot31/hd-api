#!/usr/bin/env python3
"""
Human Design Calculator API
Uses pyswisseph (Moshier ephemeris) for accurate planet positions.
Gate/line lookup uses the FullHD table from !Рассчеты_upd_v.5.xlsx
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe
import json
import os
import bisect

# ─── Load FullHD Gate-Line Lookup Table ───────────────────────────────────────
GL_LOOKUP = []  # [[lon_start, gate, line, color, tone], ...]

def load_lookup():
    global GL_LOOKUP
    path = os.path.join(os.path.dirname(__file__), 'fullhd_lookup.json')
    with open(path, 'r') as f:
        GL_LOOKUP = json.load(f)
    # GL_LOOKUP is sorted by lon_start
    print(f"Loaded {len(GL_LOOKUP)} gate-line-color-tone entries")

app = Flask(__name__)

@app.route("/")
def home():
    return "HD API работает"

CORS(app)

load_lookup()

# ─── Gate/Line/Color/Tone lookup ─────────────────────────────────────────────
def lookup_gate_data(lon):
    """
    Given ecliptic longitude (0-360°), return (gate, line, color, tone).
    Uses binary search on the pre-sorted FullHD table.
    """
    lon = lon % 360.0
    lons = [e[0] for e in GL_LOOKUP]
    idx = bisect.bisect_right(lons, lon) - 1
    if idx < 0:
        idx = len(GL_LOOKUP) - 1  # wrap-around (Gate 25 line 2 end)
    entry = GL_LOOKUP[idx]
    return entry[1], entry[2], entry[3], entry[4]  # gate, line, color, tone

# ─── Design Date Calculation ──────────────────────────────────────────────────
def calculate_design_jd(birth_jd):
    """
    Find the Julian Day when the Sun was exactly 88° before its birth position.
    Uses iterative Newton-Raphson on the Moshier ephemeris.
    """
    iflag = swe.FLG_MOSEPH | swe.FLG_SPEED
    
    # Get birth Sun longitude
    res, _ = swe.calc_ut(birth_jd, swe.SUN, iflag)
    birth_sun = res[0]
    
    # Target: Sun longitude at birth - 88°
    target_lon = (birth_sun - 88.0) % 360.0
    
    # Initial estimate: ~88 days before birth (Sun moves ~1°/day)
    jd = birth_jd - 88.0
    
    for _ in range(50):  # Newton-Raphson iterations
        res, _ = swe.calc_ut(jd, swe.SUN, iflag)
        current_lon = res[0]
        speed = res[3]  # degrees per day
        
        # Angular difference (handle wrap-around)
        diff = (target_lon - current_lon + 180) % 360 - 180
        
        if abs(diff) < 1e-8:
            break
        
        if speed < 0.01:
            speed = 0.9856  # fallback: average solar speed
        
        jd += diff / speed
    
    return jd

# ─── Planet List ──────────────────────────────────────────────────────────────
PLANETS = [
    (swe.SUN,       'Солнце',    'Sun',       '☀️'),
    (swe.MOON,      'Луна',      'Moon',      '🌙'),
    (swe.MERCURY,   'Меркурий',  'Mercury',   '☿'),
    (swe.VENUS,     'Венера',    'Venus',     '♀'),
    (swe.MARS,      'Марс',      'Mars',      '♂'),
    (swe.JUPITER,   'Юпитер',   'Jupiter',   '♃'),
    (swe.SATURN,    'Сатурн',   'Saturn',    '♄'),
    (swe.URANUS,    'Уран',      'Uranus',    '♅'),
    (swe.NEPTUNE,   'Нептун',   'Neptune',   '♆'),
    (swe.PLUTO,     'Плутон',   'Pluto',     '♇'),
    (swe.TRUE_NODE, 'Сев.Узел', 'N.Node',    '☊'),
    (swe.CHIRON,    'Хирон',    'Chiron',    '⚷'),
]

def planet_id_from_idx(idx):
    return PLANETS[idx][0]

# ─── Human Design Channels & Centers ─────────────────────────────────────────
CHANNELS = [
    (64, 47), (61, 24), (63, 4),   # Head-Ajna
    (17, 62), (43, 23), (11, 56),  # Ajna-Throat
    (16, 48), (20, 57), (10, 20),  # Throat-Spleen / Throat-G
    (34, 20), (34, 57), (34, 10),  # Sacral-Throat / Sacral-Spleen / Sacral-G
    (1, 8),   (13, 33), (7, 31),   # G-Throat
    (25, 51),                       # G-Heart
    (2, 14),  (5, 15),  (29, 46),  # Sacral-G
    (3, 60),  (9, 52),  (42, 53),  # Sacral-Root
    (27, 50), (59, 6),  (26, 44),  # Sacral-Spleen, SolarPlexus-Spleen, Heart-Spleen
    (19, 49), (37, 40), (6, 59),   # Root-SolarPlexus, SolarPlexus-Heart
    (30, 41), (55, 39), (22, 12),  # SolarPlexus-Root, SolarPlexus-Throat
    (36, 35), (21, 45), (40, 37),  # SolarPlexus-Throat, Heart-Throat
    (26, 44), (51, 25),             # Heart-Spleen, Heart-G
    (54, 32), (38, 28), (58, 18),  # Root-Spleen
    (53, 42), (60, 3),              # Root-Sacral
    (39, 55), (41, 30),            # Root-SolarPlexus
    (28, 38), (32, 54),            # Spleen-Root (duplicates handled)
    (50, 27), (57, 34),            # Spleen-Sacral
    (44, 26),                       # Spleen-Heart
    (48, 16),                       # Spleen-Throat
    (18, 58),                       # Spleen-Root
    (20, 10),                       # Throat-G (duplicate)
    (45, 21),                       # Throat-Heart
    (35, 36),                       # Throat-SolarPlexus (reverse)
    (12, 22),                       # Throat-SolarPlexus
    (33, 13),                       # Throat-G (reverse)
    (31, 7),                        # Throat-G (reverse)
    (8, 1),                         # Throat-G (reverse)
    (56, 11),                       # Throat-Ajna (reverse)
    (62, 17),                       # Throat-Ajna (reverse)
    (23, 43),                       # Throat-Ajna
    (24, 61),                       # Ajna-Head (reverse)
    (4, 63),                        # Ajna-Head (reverse)
    (47, 64),                       # Ajna-Head (reverse)
    (46, 29),                       # G-Sacral (reverse)
    (15, 5),                        # G-Sacral (reverse)
    (14, 2),                        # Sacral-G (reverse)
    (49, 19),                       # SolarPlexus-Root (reverse)
    (41, 30),                       # Root-SolarPlexus (dup)
    (10, 34),                       # G-Sacral (reverse)
    (57, 20),                       # Spleen-Throat (reverse)
    (10, 57),                       # G-Spleen
]

# Canonical channel pairs (gate_a, gate_b) both sorted
CANONICAL_CHANNELS = set()
for a, b in CHANNELS:
    pair = (min(a,b), max(a,b))
    CANONICAL_CHANNELS.add(pair)

# Centers and their associated gates
CENTERS = {
    'Head':         [64, 61, 63],
    'Ajna':         [47, 24, 4, 17, 11, 43],
    'Throat':       [62, 23, 56, 16, 35, 12, 20, 45, 31, 8, 33],
    'G-Center':     [1, 13, 7, 25, 15, 46, 10, 2],
    'Heart':        [51, 21, 26, 40],
    'Sacral':       [5, 14, 29, 34, 59, 27, 3, 42, 9],
    'Solar Plexus': [36, 22, 37, 6, 49, 55, 30],
    'Spleen':       [48, 57, 44, 50, 32, 18, 28],
    'Root':         [53, 60, 52, 54, 19, 38, 39, 58, 41],
}

CENTER_NAMES_RU = {
    'Head':         'Теменной',
    'Ajna':         'Аджна',
    'Throat':       'Горло',
    'G-Center':     'Г-центр',
    'Heart':        'Эго',
    'Sacral':       'Сакральный',
    'Solar Plexus': 'Солнечное сплетение',
    'Spleen':       'Селезёнка',
    'Root':         'Корень',
}

def get_center_for_gate(gate):
    for center, gates in CENTERS.items():
        if gate in gates:
            return center
    return None

def find_defined_channels(all_gates_set):
    """Find channels where both gates are defined (in any set)."""
    defined = []
    for a, b in CANONICAL_CHANNELS:
        if a in all_gates_set and b in all_gates_set:
            pair = (min(a,b), max(a,b))
            if pair not in [tuple(sorted(d)) for d in defined]:
                defined.append([a, b])
    return defined

def find_defined_centers(defined_channels):
    """Find centers connected by defined channels (BFS)."""
    # Build a graph of center connections
    defined_center_pairs = set()
    for a, b in defined_channels:
        ca = get_center_for_gate(a)
        cb = get_center_for_gate(b)
        if ca and cb and ca != cb:
            defined_center_pairs.add((ca, cb))
            defined_center_pairs.add((cb, ca))
    
    # A center is defined if it has at least one defined gate (part of a channel)
    defined_gate_set = set()
    for a, b in defined_channels:
        defined_gate_set.add(a)
        defined_gate_set.add(b)
    
    defined_centers = set()
    for center, gates in CENTERS.items():
        if any(g in defined_gate_set for g in gates):
            defined_centers.add(center)
    
    return defined_centers

def get_type(defined_channels, defined_centers, personality_gates, design_gates):
    """Determine Human Design type."""
    if len(defined_channels) == 0:
        return 'Рефлектор'
    
    throat_defined = 'Throat' in defined_centers
    sacral_defined = 'Sacral' in defined_centers
    
    # Motor centers
    motors = {'Heart', 'Sacral', 'Solar Plexus', 'Root'}
    
    # Check if any motor is connected to Throat
    motor_to_throat = False
    
    # Build adjacency from defined channels
    center_connections = {}
    defined_gate_set = set()
    for a, b in defined_channels:
        defined_gate_set.add(a)
        defined_gate_set.add(b)
        ca = get_center_for_gate(a)
        cb = get_center_for_gate(b)
        if ca and cb:
            center_connections.setdefault(ca, set()).add(cb)
            center_connections.setdefault(cb, set()).add(ca)
    
    # BFS from each motor to Throat
    for motor in motors:
        if motor not in defined_centers:
            continue
        # BFS
        visited = {motor}
        queue = [motor]
        while queue:
            current = queue.pop(0)
            if current == 'Throat':
                motor_to_throat = True
                break
            for neighbor in center_connections.get(current, []):
                if neighbor not in visited and neighbor in defined_centers:
                    visited.add(neighbor)
                    queue.append(neighbor)
        if motor_to_throat:
            break
    
    if sacral_defined and motor_to_throat:
        return 'Манифестирующий Генератор'
    elif sacral_defined:
        return 'Генератор'
    elif motor_to_throat:
        return 'Манифестор'
    else:
        return 'Проектор'

def get_authority(defined_centers, hd_type):
    """Determine authority based on defined centers."""
    if hd_type == 'Рефлектор':
        return 'Лунный'
    if 'Solar Plexus' in defined_centers:
        return 'Эмоциональный'
    if 'Sacral' in defined_centers:
        return 'Сакральный'
    if 'Spleen' in defined_centers:
        return 'Селезёночный'
    if 'Heart' in defined_centers:
        return 'Эго'
    if 'G-Center' in defined_centers:
        return 'Самость'
    return 'Ментальный'

def get_profile(pers_sun_line, design_sun_line):
    """Profile = Personality Sun Line / Design Sun Line."""
    return f"{pers_sun_line}/{design_sun_line}"

def get_definition(defined_channels, defined_centers):
    """Determine definition type."""
    if not defined_channels:
        return 'Нет определения'
    
    # Build connected components among defined centers
    defined_gate_set = set()
    for a, b in defined_channels:
        defined_gate_set.add(a)
        defined_gate_set.add(b)
    
    adjacency = {}
    for a, b in defined_channels:
        ca = get_center_for_gate(a)
        cb = get_center_for_gate(b)
        if ca and cb and ca != cb:
            adjacency.setdefault(ca, set()).add(cb)
            adjacency.setdefault(cb, set()).add(ca)
    
    # Find connected components of defined centers
    visited = set()
    components = []
    for center in defined_centers:
        if center not in visited:
            component = set()
            queue = [center]
            while queue:
                c = queue.pop(0)
                if c in visited:
                    continue
                visited.add(c)
                component.add(c)
                for neighbor in adjacency.get(c, []):
                    if neighbor not in visited and neighbor in defined_centers:
                        queue.append(neighbor)
            components.append(component)
    
    n = len(components)
    if n == 1:
        return 'Одинарное'
    elif n == 2:
        return 'Двойное разделённое'
    elif n == 3:
        return 'Тройное разделённое'
    else:
        return f'{n}-кратное разделённое'

def jd_to_datestr(jd):
    y, m, d, h = swe.revjul(jd)
    hour = int(h)
    minute = int((h - hour) * 60)
    second = int(((h - hour) * 60 - minute) * 60)
    return f"{int(d):02d}.{int(m):02d}.{int(y)} {hour:02d}:{minute:02d}:{second:02d} UTC"

# ─── Main Calculation Endpoint ────────────────────────────────────────────────
@app.route("/api/calc", methods=["POST"])
@app.route("/api/calculate", methods=["POST"])
def api_calc():
    try:
        data = request.json
        year  = int(data['year'])
        month = int(data['month'])
        day   = int(data['day'])
        hour  = int(data['hour'])
        minute = int(data['minute'])
        second = int(data.get('second', 0))
        tz_offset = float(data.get('tz_offset', 0))

        ut_hours = hour + minute/60 + second/3600 - tz_offset
        birth_jd = swe.julday(year, month, day, ut_hours)
        design_jd = calculate_design_jd(birth_jd)

        iflag = swe.FLG_MOSEPH | swe.FLG_SPEED

        personality_data = []
        design_data = []
        personality_gates = set()
        design_gates = set()

        for pid, name_ru, name_en, symbol in PLANETS:
            try:
                res_p, _ = swe.calc_ut(birth_jd, pid, iflag)
                lon_p = res_p[0]
                gate_p, line_p, color_p, tone_p = lookup_gate_data(lon_p)
                personality_gates.add(gate_p)

                res_d, _ = swe.calc_ut(design_jd, pid, iflag)
                lon_d = res_d[0]
                gate_d, line_d, color_d, tone_d = lookup_gate_data(lon_d)
                design_gates.add(gate_d)

                personality_data.append({
                    'planet': name_ru, 'symbol': symbol,
                    'longitude': round(lon_p, 6),
                    'gate': gate_p, 'line': line_p, 'color': color_p, 'tone': tone_p,
                    'gate_line': f"{gate_p}.{line_p}",
                })
                design_data.append({
                    'planet': name_ru, 'symbol': symbol,
                    'longitude': round(lon_d, 6),
                    'gate': gate_d, 'line': line_d, 'color': color_d, 'tone': tone_d,
                    'gate_line': f"{gate_d}.{line_d}",
                })
            except:
                continue

        # Earth
        earth_lon_p = (personality_data[0]['longitude'] + 180) % 360
        earth_lon_d = (design_data[0]['longitude'] + 180) % 360
        eg_p, el_p, ec_p, et_p = lookup_gate_data(earth_lon_p)
        eg_d, el_d, ec_d, et_d = lookup_gate_data(earth_lon_d)
        personality_gates.add(eg_p)
        design_gates.add(eg_d)
        personality_data.insert(1, {'planet':'Земля','symbol':'⊕','longitude':round(earth_lon_p,6),'gate':eg_p,'line':el_p,'color':ec_p,'tone':et_p,'gate_line':f"{eg_p}.{el_p}"})
        design_data.insert(1, {'planet':'Земля','symbol':'⊕','longitude':round(earth_lon_d,6),'gate':eg_d,'line':el_d,'color':ec_d,'tone':et_d,'gate_line':f"{eg_d}.{el_d}"})

        all_gates = personality_gates | design_gates
        defined_channels = find_defined_channels(all_gates)
        defined_centers = find_defined_centers(defined_channels)

        pers_sun_line = personality_data[0]['line']
        design_sun_line = design_data[0]['line']
        profile = get_profile(pers_sun_line, design_sun_line)
        hd_type = get_type(defined_channels, defined_centers, personality_gates, design_gates)
        authority = get_authority(defined_centers, hd_type)
        definition = get_definition(defined_channels, defined_centers)

        centers_info = {}
        for center_en, name_ru in CENTER_NAMES_RU.items():
            gates_in_center = CENTERS[center_en]
            centers_info[center_en] = {
                'name_ru': name_ru,
                'defined': center_en in defined_centers,
                'personality_gates': [g for g in gates_in_center if g in personality_gates],
                'design_gates': [g for g in gates_in_center if g in design_gates],
            }

        return jsonify({
            'success': True,
            'birth_date_utc': jd_to_datestr(birth_jd),
            'design_date_utc': jd_to_datestr(design_jd),
            'birth_jd': round(birth_jd, 6),
            'design_jd': round(design_jd, 6),
            'type': hd_type,
            'profile': profile,
            'authority': authority,
            'definition': definition,
            'personality_planets': personality_data,
            'design_planets': design_data,
            'personality_gates': sorted(personality_gates),
            'design_gates': sorted(design_gates),
            'all_gates': sorted(all_gates),
            'defined_channels': [[min(a,b), max(a,b)] for a,b in defined_channels],
            'defined_centers': list(defined_centers),
            'centers': centers_info,
        })

    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()}), 400

if __name__ == '__main__':
    print("Human Design API starting on port 10000...")
    app.run(host='0.0.0.0', port=10000, debug=False)
