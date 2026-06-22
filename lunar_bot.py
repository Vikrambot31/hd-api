import math
import datetime
import urllib.request
import urllib.parse
import json
import os
import time
from zoneinfo import ZoneInfo

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_sent.txt")

# ── Config ──────────────────────────────────────────────
BOT_TOKEN  = os.getenv("BOT_TOKEN")
CHAT_ID    = os.getenv("CHAT_ID")
if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError("Missing BOT_TOKEN or CHAT_ID. Add them in GitHub repository Settings -> Secrets and variables -> Actions.")
KYIV_TZ = ZoneInfo("Europe/Kyiv")

# ── Lunar math ──────────────────────────────────────────
KNOWN_NEW_MOON = datetime.datetime(2000, 1, 6, 18, 14, 0,
                                   tzinfo=datetime.timezone.utc)
LUNAR_CYCLE = 29.53058867

def lunar_age(dt):
    diff = (dt - KNOWN_NEW_MOON).total_seconds() / 86400
    return math.fmod(diff, LUNAR_CYCLE) % LUNAR_CYCLE

def lunar_day(dt):
    return min(max(int(lunar_age(dt)) + 1, 1), 30)

def phase_info(age):
    p = age / LUNAR_CYCLE
    if p < 0.03 or p >= 0.97: return "🌑 Новолуние"
    if p < 0.22: return "🌒 Растущий серп"
    if p < 0.28: return "🌓 Первая четверть"
    if p < 0.47: return "🌔 Растущая луна"
    if p < 0.53: return "🌕 Полнолуние"
    if p < 0.72: return "🌖 Убывающая луна"
    if p < 0.78: return "🌗 Последняя четверть"
    return "🌘 Убывающий серп"

ZODIAC_NAMES = ["Овен","Телец","Близнецы","Рак","Лев","Дева",
                "Весы","Скорпион","Стрелец","Козерог","Водолей","Рыбы"]
ZODIAC_ICONS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]
ZODIAC_NAMES_UK = ["Овна","Тельця","Близнюків","Рака","Лева","Діви",
                   "Терезів","Скорпіона","Стрільця","Козерога","Водолія","Риб"]
ZODIAC_FILES = [
    "Luna-to-Aries.png","Luna-to-Taurus.png","Luna-to-Gemini.png",
    "Luna-to-Cancer.png","Luna-to-Leo.png","Luna-to-Virgo.png",
    "Luna-to-Libra.png","Luna-to-Scorpio.png","Luna-to-Sagittarius.png",
    "Luna-to-Capricorn.png","Luna-to-Aquarius.png","Luna-to-Pisces.png",
]

def _moon_zodiac_index(dt):
    jd = (dt - datetime.datetime(2000, 1, 1, 12, 0, 0,
          tzinfo=datetime.timezone.utc)).total_seconds() / 86400 + 2451545.0
    L   = math.fmod(218.316 + 13.176396 * (jd - 2451545.0), 360)
    M   = math.fmod(134.963 + 13.064993 * (jd - 2451545.0), 360)
    lon = math.fmod(L + 6.289 * math.sin(math.radians(M)), 360)
    return int(math.fmod(lon + 360, 360) / 30)

def zodiac_info(dt):
    idx = _moon_zodiac_index(dt)
    return f"{ZODIAC_ICONS[idx]} {ZODIAC_NAMES[idx]}"

# ── Data ────────────────────────────────────────────────
DAYS = {
    1:  {"name":"Лампада",          "rating":"neutral", "tips":["Планируй, не действуй","Пост и медитация","Прислушайся к интуиции","Не подписывай договоры","Помирись с близкими"]},
    2:  {"name":"Рог изобилия",     "rating":"good",    "tips":["Говори честно и ярко","Торговля идёт отлично","Проси о повышении смело","Внимание к зубам и рту","Не участвуй в авантюрах"]},
    3:  {"name":"Барс",             "rating":"good",    "tips":["Иди в спортзал сегодня","Баня — лучший выбор","Принимай смелые решения","Работай с металлом","Не будь пассивным"]},
    4:  {"name":"Древо Познания",   "rating":"good",    "tips":["Учись и читай активно","Физический труд в почёте","Будь честен с собой","Умеренность в еде","Стройте планы с партнёром"]},
    5:  {"name":"Единорог",         "rating":"good",    "tips":["Один из лучших дней","Интуиция не подведёт","Инвестируй смело","Детокс и лёгкая еда","Романтика и волшебство"]},
    6:  {"name":"Журавль",          "rating":"good",    "tips":["Деловые знакомства — кстати","Пой и дыши глубже","Доверяй снам этой ночи","Прогулка на природе","Говори искренне"]},
    7:  {"name":"Петух",            "rating":"good",    "tips":["Вставай рано — энергия есть","Завершай начатые дела","Вечером будь осторожен","Семейный завтрак — отлично","Будь организован"]},
    8:  {"name":"Феникс",           "rating":"neutral", "tips":["День трансформации — не бойся","Следи за сердцем","Неожиданные встречи вероятны","Умеренность во всём","Медитируй для стабильности"]},
    9:  {"name":"Летучая мышь",     "rating":"bad",     "tips":["Не подписывай документы","Молчи и наблюдай","Пей больше воды","Избегай тёмных мест","Медитация защитит"]},
    10: {"name":"Фонтан",           "rating":"good",    "tips":["Деньги текут свободно","Ванна и плавание — отлично","Делись щедро — вернётся","Говори о чувствах открыто","Романтика у воды"]},
    11: {"name":"Огненный меч",     "rating":"good",    "tips":["Победный день для бизнеса","Спорт и активность — максимум","Берегись ожогов и порезов","Возьми лидерство в руки","Романтический сюрприз — кстати"]},
    12: {"name":"Чаша Грааля",      "rating":"neutral", "tips":["День любви и сострадания","Помогай другим сегодня","Прощение очищает душу","Береги сердце — зона риска","Искренность растопит лёд"]},
    13: {"name":"Колесо",           "rating":"good",    "tips":["Лови момент перемен","Путешествие приносит доход","В транспорте будь осторожен","Гибкость мышления — ключ","Старые темы вернутся — решай"]},
    14: {"name":"Труба",            "rating":"good",    "tips":["Публичность работает на тебя","Слушай — не только говори","Проверяй источники новостей","Музыка лечит сегодня","Слова имеют огромную силу"]},
    15: {"name":"Змей",             "rating":"bad",     "tips":["Не доверяй выгодным предложениям","Береги нервную систему","Сдерживай низменные желания","Медитация держит контроль","Не проводи магических ритуалов"]},
    16: {"name":"Голубь",           "rating":"good",    "tips":["День мира и стабильности","Долгосрочные вложения — отлично","Природа и чистый воздух лечат","Идеально для примирения","Делай предложение — день благоволит"]},
    17: {"name":"Виноград",         "rating":"good",    "tips":["Пожинай плоды своих трудов","Фрукты и соки очень полезны","Отмечай успехи и радуйся","Умеренность в алкоголе","Береги репутацию от завистников"]},
    18: {"name":"Зеркало",          "rating":"bad",     "tips":["Честность с собой — главное","Не смотрись долго в зеркало","Баня и лёгкое голодание","Не принимай важных решений","Анализируй — не обвиняй других"]},
    19: {"name":"Краб",             "rating":"neutral", "tips":["День ухода в себя — нормально","Работай с подсознанием","Желудок — зона внимания","Домашний уют важнее тусовок","Доверяй снам этой ночи"]},
    20: {"name":"Орёл",             "rating":"good",    "tips":["Смотри на ситуацию сверху","Дыши глубоко — лёгкие важны","Принимай стратегические решения","Свобода духа восстановлена","Говори честно с партнёром"]},
    21: {"name":"Конь",             "rating":"good",    "tips":["Скорость и движение — твои козыри","Берегись в дороге","Начни то, что давно откладывал","Импульсивные признания — кстати","Не ставь на азарт"]},
    22: {"name":"Слон",             "rating":"good",    "tips":["Мудрые решения принесут плоды","Учись — инвестиции окупятся","Совет старших очень ценен","Семья на первом месте","Терпение — твоя сила сегодня"]},
    23: {"name":"Крокодил",         "rating":"bad",     "tips":["Скрытые опасности — будь бдителен","Не хвастайся деньгами","Только рутинная работа","Молчание мудрее слов","Не провоцируй ревность"]},
    24: {"name":"Медведь",          "rating":"neutral", "tips":["Накапливай — не трать резервы","День отдыха и восстановления","Работай с недвижимостью","Домашний вечер с партнёром","Не давите друг на друга"]},
    25: {"name":"Черепаха",         "rating":"good",    "tips":["Медленно но верно к цели","Йога и тай-чи — идеально","Долгосрочные вложения выгодны","Терпение с партнёром — ключ","Не спеши — черепаха побеждает"]},
    26: {"name":"Жаба",             "rating":"bad",     "tips":["Береги кошелёк — риск кражи","Говори важное вслух","Детокс и очищение — полезно","Не заключай договоров","Молчи в конфликтах — выгоднее"]},
    27: {"name":"Корабль",          "rating":"good",    "tips":["Путешествия приносят доход","Музыка и вода целят","Маяк интуиции укажет путь","Романтика у воды — идеально","Не засыпай надолго"]},
    28: {"name":"Лотос",            "rating":"good",    "tips":["День красоты и благодати","Уход за собой — SPA и массаж","Творчество расцветает","Хорошо для помолвок и свадеб","Красивый жест говорит громче слов"]},
    29: {"name":"Спрут",            "rating":"bad",     "tips":["Жги свечи — очищает ауру","Пеки хлеб — исцеляет","Избегай тёмных мест и скандалов","Молитва защищает от тьмы","Самоизоляция лучше конфликта"]},
    30: {"name":"Золотой лебедь",   "rating":"good",    "tips":["Отдай все долги сегодня","Подведи итоги месяца","Прощай — это освобождает","Генеральная уборка — отлично","Дари подарки — вернётся вдвойне"]},
}

RATING_LABEL = {
    "good":    "✅ Благоприятный",
    "neutral": "⚪️ Нейтральный",
    "bad":     "⛔️ Неблагоприятный",
}

# ── Build message ────────────────────────────────────────
def kyiv_now():
    return datetime.datetime.now(KYIV_TZ)

def already_sent_today():
    """Return True if posts were already sent today (Kyiv date)."""
    today = kyiv_now().strftime("%Y-%m-%d")
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return f.read().strip() == today
    return False

def mark_sent_today():
    """Write today's Kyiv date to the state file."""
    today = kyiv_now().strftime("%Y-%m-%d")
    with open(STATE_FILE, "w") as f:
        f.write(today)

def should_send_now():
    # Always send — GitHub Actions delay is unpredictable, no hour filtering
    return True

def build_message():
    local = kyiv_now()
    utc_offset = int(local.utcoffset().total_seconds() // 3600)
    # Use local noon for calculations
    noon_utc = datetime.datetime(
        local.year, local.month, local.day,
        12 - utc_offset, 0, 0,
        tzinfo=datetime.timezone.utc
    )

    age   = lunar_age(noon_utc)
    ld    = lunar_day(noon_utc)
    phase = phase_info(age)
    zodiac = zodiac_info(noon_utc)
    data  = DAYS[ld]
    rating = RATING_LABEL[data["rating"]]

    # Weekday in Russian
    weekdays = ["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресенье"]
    months   = ["января","февраля","марта","апреля","мая","июня",
                "июля","августа","сентября","октября","ноября","декабря"]
    wday  = weekdays[local.weekday()]
    mname = months[local.month - 1]
    date_str = f"{wday}, {local.day} {mname}"

    tips = data["tips"][:3]
    tips_text = "\n".join(f"  • {t}" for t in tips)

    msg = (
        f"🌙 *Лунный день — {date_str}*\n\n"
        f"*{ld}-й лунный день* — {data['name']}\n"
        f"{phase}   {zodiac}\n"
        f"{rating}\n\n"
        f"*Советы дня:*\n{tips_text}\n\n"
        f"🔮 [Полный календарь](https://vikramhd2027.netlify.app/lunar)"
    )
    return msg

# ── Send to Telegram ─────────────────────────────────────
def send_message(text, retries=3):
    url  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = json.dumps({
        "chat_id":    CHAT_ID,
        "text":       text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read())
                if not result.get("ok"):
                    raise RuntimeError(f"Telegram error: {result}")
                print(f"✅ Sent to {CHAT_ID}, message_id={result['result']['message_id']}")
                return
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)

# ── Zodiac sign change detection & photo post ────────────
def _dt_to_jd(dt):
    return (dt - datetime.datetime(2000, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)).total_seconds() / 86400 + 2451545.0

def _jd_to_dt(jd):
    return datetime.datetime(2000, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc) + datetime.timedelta(days=jd - 2451545.0)

def _moon_lon_sweph(jd):
    try:
        import swisseph as swe
        swe.set_ephe_path(None)
        result, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_NONUT)
        return result[0]
    except Exception:
        return None

def _find_sign_entry_time(idx_today, search_end_utc):
    """Binary search: find exact UTC moment Moon entered idx_today sign (search 48h back)."""
    boundary_lon = idx_today * 30.0
    jd_end = _dt_to_jd(search_end_utc)
    jd_start = jd_end - 2.0  # 48 hours back

    def past_boundary(jd):
        lon = _moon_lon_sweph(jd)
        if lon is None:
            return False
        return ((lon - boundary_lon) % 360) < 180

    if not past_boundary(jd_end) or past_boundary(jd_start):
        return None

    lo, hi = jd_start, jd_end
    for _ in range(40):
        mid = (lo + hi) / 2
        if past_boundary(mid):
            hi = mid
        else:
            lo = mid
        if (hi - lo) * 86400 < 30:  # 30-second precision
            break

    return _jd_to_dt((lo + hi) / 2)

def check_sign_change():
    """Return (zodiac_index, entry_time_utc) if Moon changed sign today, else (None, None)."""
    local = kyiv_now()
    utc_offset = int(local.utcoffset().total_seconds() // 3600)
    noon_today = datetime.datetime(
        local.year, local.month, local.day,
        12 - utc_offset, 0, 0,
        tzinfo=datetime.timezone.utc
    )
    noon_yesterday = noon_today - datetime.timedelta(days=1)
    idx_today = _moon_zodiac_index(noon_today)
    idx_yesterday = _moon_zodiac_index(noon_yesterday)
    if idx_today != idx_yesterday:
        search_end = noon_today + datetime.timedelta(hours=12)
        entry_utc = _find_sign_entry_time(idx_today, search_end)
        return idx_today, entry_utc
    return None, None

def send_photo(photo_path, caption, retries=3):
    """Send a photo with caption to Telegram using multipart/form-data."""
    boundary = "----PythonBotBoundary"
    filename = os.path.basename(photo_path)

    with open(photo_path, "rb") as f:
        photo_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
        f"{CHAT_ID}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="caption"\r\n\r\n'
        f"{caption}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="parse_mode"\r\n\r\n'
        f"Markdown\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="photo"; filename="{filename}"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode("utf-8") + photo_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
                if not result.get("ok"):
                    raise RuntimeError(f"Telegram error: {result}")
                print(f"📸 Photo sent to {CHAT_ID}, message_id={result['result']['message_id']}")
                return
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)

def maybe_send_sign_change_photo():
    """If Moon changed zodiac sign today, send the corresponding image with entry time."""
    idx, entry_utc = check_sign_change()
    if idx is None:
        print("🔄 Знак Луны не менялся — фото не отправляем")
        return

    sign_uk = ZODIAC_NAMES_UK[idx]
    photo_file = ZODIAC_FILES[idx]
    photo_dir = os.path.join(os.path.dirname(__file__), "foto-for Lunar Bot")
    photo_path = os.path.join(photo_dir, photo_file)

    if not os.path.exists(photo_path):
        print(f"⚠️ Фото не найдено: {photo_path}")
        return

    # Convert entry time to Kyiv time (UTC+3 summer)
    if entry_utc is not None:
        entry_kyiv = entry_utc + datetime.timedelta(hours=3)
        time_str = entry_kyiv.strftime("%H:%M")
        time_line = f"\n⏰ Час входу в знак {sign_uk}: *{time_str}* (Київ)\n"
        print(f"🕐 Точный вход: {time_str} Киев (UTC: {entry_utc.strftime('%H:%M')})")
    else:
        time_line = "\n"

    caption = (
        f"{ZODIAC_ICONS[idx]} *Місяць перейшов у знак {sign_uk}*"
        f"{time_line}\n"
        f"Якщо не справляєтесь з емоціями — [пишіть Викраму](https://t.me/Vikram_2027) 💬"
    )
    print(f"📸 Смена знака! Луна → {ZODIAC_NAMES[idx]}. Отправляю фото...")
    send_photo(photo_path, caption)


if __name__ == "__main__":
    if already_sent_today():
        print(f"⏭️  Посты уже отправлены сегодня ({kyiv_now().strftime('%Y-%m-%d')}) — пропускаем")
        raise SystemExit(0)
    if not should_send_now():
        raise SystemExit(0)
    msg = build_message()
    print("── Message preview ──")
    print(msg)
    print("── Sending ──")
    send_message(msg)
    print("── Sign change check ──")
    maybe_send_sign_change_photo()
    mark_sent_today()
    print(f"✅ Дата отправки сохранена: {kyiv_now().strftime('%Y-%m-%d')}")

