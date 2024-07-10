import sqlite3
import telebot
from dotenv import load_dotenv
import os
import sys
import html
import time
from loguru import logger

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройки Telegram
TOKEN = os.getenv('TELEGRAMBOT_API_KEY')
CHANNEL_ID = os.getenv('CHAT_ID')
CHAT_THREAD_ID = int(os.getenv('CHAT_THREAD_ID', 0))  # Используем переменную окружения для ID потока
FOOTER_TEXT = os.getenv('FOOTER_TEXT')
POST_DELAY = int(os.getenv('POST_DELAY', 5))  # Задержка между постами в секундах (по умолчанию 5 секунд)

bot = telebot.TeleBot(TOKEN)

# Ограничения Telegram
MESSAGE_LIMIT = 4096
IMAGE_MESSAGE_LIMIT = 1024

def fetch_unposted_news():
    conn = sqlite3.connect('news_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT link, title, images, rich_text FROM news WHERE posted = 0')
    rows = cursor.fetchall()
    conn.close()
    return rows

def mark_as_posted(link):
    conn = sqlite3.connect('news_data.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE news SET parsed = 1, posted = 1 WHERE link = ?', (link,))
    conn.commit()
    conn.close()

def split_message(message, limit):
    """Функция для разделения длинных сообщений на несколько частей"""
    parts = []
    while len(message) > limit:
        split_index = message.rfind('\n', 0, limit)
        if split_index == -1:
            split_index = limit
        parts.append(message[:split_index])
        message = message[split_index:]
    parts.append(message)
    return parts

def post_news_to_telegram():
    news_items = fetch_unposted_news()

    logger.info(f"Найдено {len(news_items)} новостей для постинга")

    for item in news_items:
        link, title, images, rich_text = item
        escaped_title = html.escape(title)
        escaped_rich_text = html.escape(rich_text or '')
        base_message = (
            f" \U0001F6CE <b>{escaped_title}</b>\n\n{escaped_rich_text}\n\n"
            f"{FOOTER_TEXT}"
        )

        try:
            if images:
                image_urls = images.split(', ')
                first_message = True
                for image_url in image_urls:
                    if first_message:
                        parts = split_message(base_message, IMAGE_MESSAGE_LIMIT)
                        for part in parts:
                            bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=part, parse_mode='HTML', reply_to_message_id=CHAT_THREAD_ID)
                            first_message = False
                    else:
                        bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption="", parse_mode='HTML', reply_to_message_id=CHAT_THREAD_ID)
            else:
                parts = split_message(base_message, MESSAGE_LIMIT)
                for part in parts:
                    bot.send_message(chat_id=CHANNEL_ID, text=part, parse_mode='HTML', reply_to_message_id=CHAT_THREAD_ID, disable_web_page_preview=True)

            mark_as_posted(link)
            logger.info(f"Новость '{title}' опубликована в Telegram")

        except Exception as e:
            mark_as_posted(link)  # Отмечаем новость как опубликованную даже в случае ошибки
            logger.error(f"Ошибка при отправке новости '{title}' в Telegram: {e}")

        # Пауза между постами
        time.sleep(POST_DELAY)

if __name__ == "__main__":
    try:
        post_news_to_telegram()
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        sys.exit(1)
