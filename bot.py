import logging
from datetime import datetime, timedelta
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import json
import os

from config import (
    TELEGRAM_BOT_TOKEN, CHANNEL_ID, GROQ_API_KEY,
    CHECK_INTERVAL_MINUTES, MIN_POST_INTERVAL_MINUTES, MAX_POSTS_PER_DAY
)
from news_fetcher import check_for_news, format_news_for_generation
from generator import generator

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
STATE_FILE = "bot_state.json"


class BotState:
    def __init__(self):
        self.last_post_time = None
        self.posts_today = 0
        self.today_date = None
        self.is_paused = False
        self.load()
    
    def load(self):
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r") as f:
                    data = json.load(f)
                    self.last_post_time = datetime.fromisoformat(data["last_post_time"]) if data.get("last_post_time") else None
                    self.posts_today = data.get("posts_today", 0)
                    self.today_date = data.get("today_date")
                    self.is_paused = data.get("is_paused", False)
        except:
            pass
    
    def save(self):
        try:
            with open(STATE_FILE, "w") as f:
                json.dump({
                    "last_post_time": self.last_post_time.isoformat() if self.last_post_time else None,
                    "posts_today": self.posts_today,
                    "today_date": self.today_date,
                    "is_paused": self.is_paused,
                }, f)
        except:
            pass
    
    def can_post(self):
        if self.is_paused:
            return False, "Бот на паузе"
        
        today = datetime.now().strftime("%Y-%m-%d")
        if self.today_date != today:
            self.today_date = today
            self.posts_today = 0
            self.save()
        
        if self.posts_today >= MAX_POSTS_PER_DAY:
            return False, f"Лимит {MAX_POSTS_PER_DAY} постов"
        
        if self.last_post_time:
            elapsed = datetime.now() - self.last_post_time
            if elapsed < timedelta(minutes=MIN_POST_INTERVAL_MINUTES):
                remaining = MIN_POST_INTERVAL_MINUTES - (elapsed.seconds // 60)
                return False, f"Подожди {remaining} мин"
        
        return True, "OK"
    
    def record_post(self):
        self.last_post_time = datetime.now()
        self.posts_today += 1
        self.save()


state = BotState()


async def publish_post(post: str) -> bool:
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=post)
        logger.info(f"✅ Published: {len(post)} chars")
        return True
    except Exception as e:
        logger.error(f"❌ Publish error: {e}")
        return False


async def news_check_cycle():
    logger.info("🔍 Checking news...")
    
    can_post, reason = state.can_post()
    if not can_post:
        logger.info(f"⏸ Skip: {reason}")
        return
    
    try:
        urgent, important = await check_for_news()
        
        if urgent:
            logger.info(f"🚨 URGENT: {urgent['title']}")
            post = await generator.generate_post(f"СРОЧНО: {urgent['title']}", is_urgent=True)
            if post and await publish_post(post):
                state.record_post()
            return
        
        if len(important) >= 2:
            logger.info(f"📰 {len(important)} important news")
            news_digest = format_news_for_generation(important)
            post = await generator.generate_post(news_digest)
            if post and await publish_post(post):
                state.record_post()
        else:
            logger.info("😴 No significant news")
            
    except Exception as e:
        logger.error(f"Cycle error: {e}")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Бот @naumkogan\n\n"
        "/status - Статус\n"
        "/force - Опубликовать\n"
        "/preview - Превью\n"
        "/pause - Пауза\n"
        "/resume - Продолжить"
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    can_post, reason = state.can_post()
    pause_status = "🔴 ПАУЗА" if state.is_paused else "🟢 Активен"
    last_post = state.last_post_time.strftime("%H:%M") if state.last_post_time else "—"
    
    await update.message.reply_text(
        f"🤖 Статус\n\n"
        f"{pause_status}\n"
        f"📊 Постов: {state.posts_today}/{MAX_POSTS_PER_DAY}\n"
        f"🕐 Последний: {last_post}\n"
        f"🔑 AI: {'Groq ✅' if GROQ_API_KEY else '❌'}"
    )


async def cmd_force(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Генерирую...")
    
    try:
        urgent, important = await check_for_news()
        all_news = ([urgent] if urgent else []) + important
        news_digest = format_news_for_generation(all_news[:5]) if all_news else ""
        
        post = await generator.generate_post(news_digest)
        
        if post:
            if await publish_post(post):
                state.record_post()
                await update.message.reply_text("✅ Опубликовано!")
            else:
                await update.message.reply_text("❌ Ошибка публикации")
        else:
            await update.message.reply_text("❌ Ошибка генерации")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")


async def cmd_preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Генерирую...")
    
    try:
        urgent, important = await check_for_news()
        all_news = ([urgent] if urgent else []) + important
        news_digest = format_news_for_generation(all_news[:5]) if all_news else ""
        
        post = await generator.generate_post(news_digest)
        
        if post:
            await update.message.reply_text(f"📝 ПРЕВЬЮ:\n\n{post}")
        else:
            await update.message.reply_text("❌ Ошибка генерации")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")


async def cmd_pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.is_paused = True
    state.save()
    await update.message.reply_text("⏸ Пауза")


async def cmd_resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state.is_paused = False
    state.save()
    await update.message.reply_text("▶️ Работаю!")


def main():
    if not GROQ_API_KEY:
        logger.error("❌ GROQ_API_KEY not set!")
        return
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("force", cmd_force))
    app.add_handler(CommandHandler("preview", cmd_preview))
    app.add_handler(CommandHandler("pause", cmd_pause))
    app.add_handler(CommandHandler("resume", cmd_resume))
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(news_check_cycle, 'interval', minutes=CHECK_INTERVAL_MINUTES)
    scheduler.start()
    
    logger.info("=" * 50)
    logger.info("🤖 Bot started!")
    logger.info(f"📍 Channel: {CHANNEL_ID}")
    logger.info("=" * 50)
    
    app.run_polling()


if __name__ == "__main__":
    main()
