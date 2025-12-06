import requests
from config import GROQ_API_KEY, AUTHOR_PROFILE
import logging

logger = logging.getLogger(__name__)


class ContentGenerator:
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        if self.api_key:
            logger.info("✅ Groq API configured")
        else:
            logger.error("❌ No GROQ_API_KEY!")
    
    def _build_prompt(self, news_digest: str, custom_topic: str = None, is_urgent: bool = False) -> str:
        urgency = "⚠️ СРОЧНАЯ новость! Будь эмоциональным.\n" if is_urgent else ""
        
        prompt = f"""{AUTHOR_PROFILE}

{urgency}
Напиши пост для Telegram-канала.

Правила:
- Пиши на русском
- 3-8 абзацев  
- 1-3 эмодзи в конце
- Без хештегов
- Не начинай с "Друзья"
- Дай свою оценку
- Отвечай ТОЛЬКО текстом поста
"""
        
        if custom_topic:
            prompt += f"\nТема: {custom_topic}"
        elif news_digest.strip():
            prompt += f"\nНовости:\n{news_digest}\n\nВыбери одну и напиши пост."
        else:
            prompt += "\nПоделись размышлениями о жизни в Израиле."
        
        return prompt
    
    async def generate_post(self, news_digest: str, custom_topic: str = None, is_urgent: bool = False) -> str:
        if not self.api_key:
            return None
            
        prompt = self._build_prompt(news_digest, custom_topic, is_urgent)
        
        try:
            logger.info("Groq: starting...")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama-3.1-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
                "temperature": 0.8
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            post = result["choices"][0]["message"]["content"].strip()
            
            if len(post) < 50:
                logger.warning(f"Too short: {len(post)}")
                return None
            
            if len(post) > 4000:
                post = post[:3900] + "..."
            
            logger.info(f"Groq OK: {len(post)} chars")
            return post
            
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return None


generator = ContentGenerator()
