import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@naumkogan")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

CHECK_INTERVAL_MINUTES = 10
MIN_POST_INTERVAL_MINUTES = 60
MAX_POSTS_PER_DAY = 8

NEWS_SOURCES = [
    {"name": "Times of Israel", "url": "https://www.timesofisrael.com/feed/", "type": "rss", "language": "en"},
    {"name": "Jerusalem Post", "url": "https://www.jpost.com/rss/rssfeedsfrontpage.aspx", "type": "rss", "language": "en"},
    {"name": "Ynet News", "url": "https://www.ynetnews.com/RSS/", "type": "rss", "language": "en"},
    {"name": "Channel 12 (Mako)", "url": "https://www.mako.co.il/rss/news.xml", "type": "rss", "language": "he"},
    {"name": "Walla News", "url": "https://rss.walla.co.il/feed/1", "type": "rss", "language": "he"},
    {"name": "Ynet Hebrew", "url": "https://www.ynet.co.il/Integration/StoryRss2.xml", "type": "rss", "language": "he"},
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
Ты — Наум Коган, автор Telegram-канала об Израиле. Живёшь в Израиле, репатриант из России.

ПОЗИЦИЯ:
- Произраильская, но критикуешь и Нетаньяху, и оппозицию
- ХАМАС виноват в гибели мирных палестинцев, но сочувствуешь детям
- Против ультраортодоксов и их привилегий
- За диалог между левыми и правыми

СТИЛЬ:
- Честный, прямой, личный
- Пишешь от первого лица
- Самоирония
- Риторические вопросы
"""
