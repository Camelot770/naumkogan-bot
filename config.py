import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@naumkogan")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

CHECK_INTERVAL_MINUTES = 5
MIN_POST_INTERVAL_MINUTES = 30
MAX_POSTS_PER_DAY = 15

NEWS_SOURCES = [
    # Английские - актуальные
    {"name": "Times of Israel", "url": "https://www.timesofisrael.com/feed/", "type": "rss", "language": "en"},
    {"name": "Times of Israel Israel", "url": "https://www.timesofisrael.com/israel-the-region/feed/", "type": "rss", "language": "en"},
    {"name": "Haaretz", "url": "https://www.haaretz.com/srv/haaretz-latest-headlines", "type": "rss", "language": "en"},
    {"name": "i24 News", "url": "https://www.i24news.tv/en/rss/israel", "type": "rss", "language": "en"},
    # Ивритские - актуальные  
    {"name": "Ynet Breaking", "url": "https://www.ynet.co.il/Integration/StoryRss1854.xml", "type": "rss", "language": "he"},
    {"name": "Ynet News", "url": "https://www.ynet.co.il/Integration/StoryRss2.xml", "type": "rss", "language": "he"},
    {"name": "Walla News", "url": "https://rss.walla.co.il/feed/1", "type": "rss", "language": "he"},
    {"name": "Maariv", "url": "https://www.maariv.co.il/Rss/RssFeedsMivzakChadashot", "type": "rss", "language": "he"},
]

IMPORTANT_KEYWORDS = [
    "hostage", "заложник", "חטוף", "ceasefire", "перемирие", "הפסקת אש",
    "hamas", "хамас", "חמאס", "hezbollah", "хезболла", "חיזבאללה",
    "iran", "иран", "איראן", "rocket", "ракет", "רקט",
    "netanyahu", "нетаньяху", "נתניהו", "knesset", "кнессет", "כנסת",
    "breaking", "срочно", "מבזק", "killed", "погиб", "נהרג",
    "attack", "атак", "פיגוע", "terror", "теракт", "טרור",
]

URGENT_KEYWORDS = [
    "breaking", "מבזק", "срочно", "hostage released", "שוחרר",
    "rocket alert", "אזעקה", "terror attack", "פיגוע", "теракт",
]

AUTHOR_PROFILE = """
Ты — новостной редактор Telegram-канала об Израиле.

ЗАДАЧА: Перескажи новость интересно и понятно для русскоязычной аудитории.

МОЖНО:
- Пересказывать своими словами
- Объяснять кто есть кто (если имя есть в новости)
- Писать 3-5 абзацев
- Добавить своё мнение в конце
- Использовать 1-2 эмодзи

НЕЛЬЗЯ (строго!):
- Выдумывать даты (никаких "7 октября", "в прошлом месяце" если этого нет в новости)
- Выдумывать числа жертв, раненых, заложников
- Добавлять имена людей которых нет в новости
- Придумывать детали событий
- Писать про события которых нет в новости

Если хочешь дать контекст — пиши "напомним" или "ранее сообщалось" только если это ТОЧНО правда.

Пиши на русском языке.
"""
