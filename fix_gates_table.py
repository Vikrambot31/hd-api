#!/usr/bin/env python3
"""
ИСПРАВЛЕНИЕ ТАБЛИЦЫ ВОРОТ HUMAN DESIGN

Скрипт восстанавливает правильное распределение ворот на основе:
1. Известного порядка ворот в Human Design (I Ching sequence)
2. Контрольных точек (24.4° → 44, 11.5° → 45)
3. Логики распределения по зодиаку
"""

import json
import math

# ============================================================================
# ПРАВИЛЬНЫЙ ПОРЯДОК ВОРОТ В HUMAN DESIGN (I Ching + Астрология)
# ============================================================================
# Этот порядок определен системой Human Design
# Каждый знак зодиака (30°) содержит определенные ворота в определенном порядке

ZODIAC_GATES = {
    # Овен (0-30°): 51, 25, 17, 21, 42, 3, 27, 24, 2, 23
    # Телец (30-60°): 8, 20, 16, 35, 45, 12, 15, 10, 9, 52
    # И так далее...
    # Это упрощенное представление - полный порядок более сложный
}

def get_correct_gate_ranges():
    """
    Возвращает правильные диапазоны долгот для каждого Ворот.

    Источник: Система Human Design (основана на И Цзин)
    Каждый Ворота занимает примерно 5.625° (360° / 64)
    """

    # Основной принцип: каждый Ворота занимает один "дом" из 64
    # В Human Design это соответствует гексаграммам И Цзин

    # Правильное распределение (восстановлено на основе контрольных точек):
    # Gate 45 должен быть около 11.5°
    # Gate 44 должен быть около 24.4°

    # Из этого можно вычислить:
    # Если Gate 45 на 11.5° и занимает ~5.625°, то:
    # Gate 45: примерно 8.7° - 14.3°
    # Gate 44: примерно 22.1° - 27.7°

    # На основе анализа и известных данных о Human Design:
    gates_ranges = {}

    # Используем известный порядок ворот в соответствии с Human Design
    # Источник: Система Human Design Ra Uru Hu

    # Определяем примерный порядок на основе логики и известных точек
    gates_data_points = [
        # (ворота, примерный центр долготы)
        (44, 24.4),   # Контрольная точка
        (45, 11.5),   # Контрольная точка
        # Остальные восстанавливаем логически...
    ]

    return None  # Требует дополнительных данных

def create_fixed_table_from_excel_template():
    """
    Создает исправленную таблицу на основе шаблона Excel.

    ТРЕБУЕТ: файл !Рассчеты_upd_v.5.xlsx (лист FullHD)
    """

    print("📄 Попытка загрузки данных из Excel...")

    try:
        import openpyxl
    except ImportError:
        print("✗ openpyxl не установлен")
        print("  Установите: pip install openpyxl")
        return None

    excel_file = "!Рассчеты_upd_v.5.xlsx"

    try:
        wb = openpyxl.load_workbook(excel_file)
        ws = wb["FullHD"]

        print(f"✓ Найден файл: {excel_file}")
        print(f"✓ Лист: FullHD")

        # Читаем данные
        gates_data = {}
        for row in ws.iter_rows(values_only=True):
            if row[0] and isinstance(row[0], (int, float)):
                lon_start = row[0]
                gate = row[1]
                # Собираем данные
                if gate not in gates_data:
                    gates_data[gate] = []
                gates_data[gate].append(lon_start)

        return gates_data

    except FileNotFoundError:
        print(f"✗ Файл не найден: {excel_file}")
        return None
    except Exception as e:
        print(f"✗ Ошибка при чтении: {e}")
        return None

def create_logically_correct_table():
    """
    Создает логически правильную таблицу на основе математических принципов.

    Используется в случае если исходные данные недоступны.
    """

    print("📊 Генерирую логически правильное распределение ворот...\n")

    # В Human Design 64 гексаграммы (ворота) распределены по 360°
    # Каждый ворота занимает: 360° / 64 = 5.625°

    lookup_table = []
    gates_per_degree = 64 / 360  # ворот на градус
    step_per_entry = 360 / 13824  # градусов на запись (13824 = 64 * 216)

    for gate_num in range(1, 65):
        # Диапазон для этого Ворота
        gate_start = (gate_num - 1) * (360 / 64)
        gate_end = gate_num * (360 / 64)

        # Каждый ворота разделен на 6 линий × 6 тонов = 36 записей
        for i in range(216):  # 216 записей на ворота
            lon = gate_start + (i * (360 / 64) / 216)
            line = (i // 36) + 1  # 6 линий
            color = (i // 36) + 1  # Цвет совпадает с линией
            tone = (i % 36) // 6 + 1  # 6 тонов

            # [longitude, gate, line, color, tone]
            lookup_table.append([
                round(lon, 8),
                gate_num,
                line,
                color,
                tone
            ])

    # Сортируем по долготе (уже в правильном порядке)
    lookup_table.sort(key=lambda x: x[0])

    return lookup_table

def validate_table(table):
    """Проверяет корректность таблицы"""

    if not table or len(table) != 13824:
        return False, f"Неправильный размер: {len(table)} (ожидается 13824)"

    # Проверяем диапазоны долгот
    min_lon = min(row[0] for row in table)
    max_lon = max(row[0] for row in table)

    if min_lon < 0 or max_lon >= 360:
        return False, f"Диапазон долгот выходит за границы: {min_lon} - {max_lon}"

    # Проверяем покрытие
    lons = sorted(set(row[0] for row in table))
    expected_count = 13824
    if len(lons) < expected_count * 0.9:  # Хотя бы 90% уникальных долгот
        return False, "Недостаточное покрытие диапазона долгот"

    # Проверяем валидность ворот
    gates = set(row[1] for row in table)
    if len(gates) != 64:
        return False, f"Неправильное количество ворот: {len(gates)} (ожидается 64)"

    return True, "✓ Таблица валидна"

def test_specific_cases(table):
    """Тестирует конкретные известные случаи"""

    test_cases = [
        (24.4, 44, "Долгота 24.4° должна быть Gate 44"),
        (11.5, 45, "Долгота 11.5° должна быть Gate 45"),
    ]

    print("\n🧪 ТЕСТИРОВАНИЕ КОНТРОЛЬНЫХ ТОЧЕК:")
    all_passed = True

    for lon, expected_gate, description in test_cases:
        # Находим ворота для этой долготы
        actual_gate = None
        for row in table:
            if row[0] <= lon < row[0] + (360 / 64 / 216):
                actual_gate = row[1]
                break

        # Если не нашли, ищем ближайший
        if not actual_gate:
            idx = 0
            for i, row in enumerate(table):
                if row[0] <= lon:
                    idx = i
            actual_gate = table[idx][1]

        passed = (actual_gate == expected_gate)
        status = "✓ PASS" if passed else "✗ FAIL"
        all_passed = all_passed and passed

        print(f"  {status}: {description}")
        print(f"         Долгота {lon}° → Gate {actual_gate} (ожидается {expected_gate})")

    return all_passed

if __name__ == "__main__":
    print("=" * 70)
    print("ИСПРАВЛЕНИЕ ТАБЛИЦЫ ВОРОТ fullhd_lookup.json")
    print("=" * 70)

    # Шаг 1: Попробуем загрузить из Excel
    excel_data = create_fixed_table_from_excel_template()

    if excel_data:
        print("\n✓ Используются данные из Excel")
        # TODO: преобразовать excel_data в lookup_table
        lookup_table = None
    else:
        # Шаг 2: Создаем логически правильную таблицу
        print("\n⚠️  Excel не найден")
        print("Создаю логически правильное распределение...\n")
        lookup_table = create_logically_correct_table()

    # Шаг 3: Валидация
    if lookup_table:
        is_valid, message = validate_table(lookup_table)
        print(f"\n✓ Таблица создана: {len(lookup_table)} записей")
        print(f"  {message}")

        # Шаг 4: Тестирование
        test_passed = test_specific_cases(lookup_table)

        # Шаг 5: Сохраняем
        if test_passed:
            output_file = "fullhd_lookup_fixed.json"
            with open(output_file, 'w') as f:
                json.dump(lookup_table, f, separators=(',', ':'))
            print(f"\n✓ Сохранено: {output_file}")
            print(f"  Размер файла: {len(lookup_table)} записей")
        else:
            print("\n✗ Тесты не пройдены!")
            print("  Требуется источник правильных данных (Excel файл)")

    print("\n" + "=" * 70)

