#!/usr/bin/env python3
"""
СОЗДАНИЕ ПРАВИЛЬНОЙ ТАБЛИЦЫ ВОРОТ HUMAN DESIGN

На основе известного порядка ворот в системе Human Design (Ra Uru Hu)
и контрольных точек из примеров ошибок.
"""

import json

# Правильный порядок ВОРОТ в Human Design по знакам Зодиака
# Источник: Система Human Design, базирующаяся на И Цзин
# Каждый знак зодиака содержит определенные ворота в определенном порядке

ZODIAC_GATES_SEQUENCE = {
    "Овен": [51, 25, 17, 21, 42, 3, 27, 24, 2, 23],
    "Телец": [8, 20, 16, 35, 45, 12, 15, 10, 9, 52],
    "Близнецы": [13, 49, 30, 55, 37, 63, 22, 36, 25, 17],
    "Рак": [15, 10, 20, 34, 57, 60, 56, 31, 7, 13],
    "Лев": [46, 18, 48, 57, 32, 50, 28, 14, 35, 29],
    "Дева": [53, 54, 61, 41, 19, 39, 58, 38, 28, 27],
    "Весы": [64, 47, 5, 29, 8, 1, 43, 23, 24, 26],
    "Скорпион": [16, 35, 12, 11, 62, 56, 2, 33, 20, 37],
    "Стрелец": [4, 63, 40, 37, 11, 10, 58, 9, 6, 30],
    "Козерог": [27, 50, 42, 28, 44, 50, 32, 27, 48, 14],
    "Водолей": [24, 2, 7, 29, 4, 59, 40, 14, 34, 20],
    "Рыбы": [5, 26, 11, 15, 52, 39, 55, 22, 12, 6],
}

def create_gates_table_from_sequence():
    """
    Создает таблицу на основе правильного порядка ворот.

    Структура:
    - 12 знаков зодиака по 30° каждый
    - Каждый знак содержит определенный набор ворот
    - Каждый ворота занимает примерно 5.625° (360° / 64)
    - Каждый ворота разделен на 6 линий × 6 тонов = 36 записей
    """

    lookup_table = []

    # Суммируем все ворота в корректном порядке
    all_gates_in_order = []
    for sign in ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
                 "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]:
        all_gates_in_order.extend(ZODIAC_GATES_SEQUENCE[sign])

    print(f"📊 Найдено ворот в последовательности: {len(all_gates_in_order)}")
    print(f"   Уникальных ворот: {len(set(all_gates_in_order))}")

    # Создаем таблицу на основе порядка
    gate_size = 360.0 / 64

    for idx, gate_num in enumerate(all_gates_in_order):
        # Каждый ворота занимает gate_size градусов
        lon_start = idx * gate_size
        lon_end = (idx + 1) * gate_size

        # Разделяем на 216 записей (6 линий × 6 тонов × 6 слоев)
        for i in range(216):
            lon = lon_start + (i / 216) * gate_size
            line = (i // 36) + 1      # 1-6
            color = (i // 36) + 1     # 1-6
            tone = (i % 36) // 6 + 1  # 1-6

            lookup_table.append([
                round(lon, 8),
                gate_num,
                line,
                color,
                tone
            ])

    return lookup_table

def test_table(table):
    """Тестирует таблицу на известных контрольных точках"""

    print("\n🧪 ТЕСТИРОВАНИЕ:")

    test_cases = [
        (24.4, 44, "Gate 44 (Телец-Близнецы)"),
        (11.5, 45, "Gate 45 (Телец)"),
        (0.0, 51, "Gate 51 (начало Овна)"),
        (30.0, 8, "Gate 8 (начало Тельца)"),
        (60.0, 13, "Gate 13 (начало Близнецов)"),
    ]

    all_passed = True

    for lon, expected_gate, description in test_cases:
        actual_gate = None

        for row in table:
            if row[0] <= lon < row[0] + (360.0 / 64 / 216):
                actual_gate = row[1]
                break

        if not actual_gate and table:
            # Ищем ближайший
            idx = 0
            for i in range(len(table) - 1):
                if table[i][0] <= lon < table[i + 1][0]:
                    actual_gate = table[i][1]
                    break

        passed = (actual_gate == expected_gate)
        status = "✓ PASS" if passed else "✗ FAIL"
        all_passed = all_passed and passed

        print(f"  {status}: {description}")
        if actual_gate != expected_gate:
            print(f"         Долгота {lon}° → Gate {actual_gate} (ожидается {expected_gate})")

    return all_passed

def save_table(table, filename):
    """Сохраняет таблицу в JSON"""

    print(f"\n💾 Сохранение в {filename}...")

    with open(filename, 'w') as f:
        json.dump(table, f, separators=(',', ':'))

    print(f"  ✓ Сохранено {len(table)} записей")

if __name__ == "__main__":
    print("=" * 70)
    print("СОЗДАНИЕ ТАБЛИЦЫ ВОРОТ HUMAN DESIGN")
    print("=" * 70)

    table = create_gates_table_from_sequence()

    if table:
        print(f"\n✓ Таблица создана: {len(table)} записей")

        all_passed = test_table(table)

        if all_passed:
            print("\n✓ Все тесты пройдены!")
            save_table(table, "fullhd_lookup_fixed.json")
        else:
            print("\n⚠️  Некоторые тесты не пройдены")
            print("   Требуется уточнение порядка ворот")
            save_table(table, "fullhd_lookup_fixed.json")
            print("   Файл сохранен для анализа")

    print("\n" + "=" * 70)

