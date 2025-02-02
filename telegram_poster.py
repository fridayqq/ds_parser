import time
import telebot
from dotenv import load_dotenv
import os
import html
from loguru import logger
from database import fetch_unposted_news, mark_as_posted
import sys

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройки Telegram
TOKEN = os.getenv('TELEGRAMBOT_API_KEY')
CHANNEL_ID = os.getenv('CHAT_ID')
CHAT_THREAD_ID = int(os.getenv('CHAT_THREAD_ID', 0))  # Используем переменную окружения для ID потока
FOOTER_TEXT = os.getenv('FOOTER_TEXT')

# Настройки второго канала
CHANNEL_ID2 = os.getenv('CHAT_ID2')
FOOTER_TEXT2 = os.getenv('FOOTER_TEXT2')

POST_DELAY = int(os.getenv('POST_DELAY', 5))  # Задержка между постами в секундах (по умолчанию 5 секунд)

bot = telebot.TeleBot(TOKEN)

# Ограничения Telegram
MESSAGE_LIMIT = 4096
IMAGE_MESSAGE_LIMIT = 1024

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
        escaped_rich_text = html.escape(rich_text.strip()) if rich_text else ''  # Удаляем лишние пробелы если rich_text не пустой

        base_message = f" \U0001F6CE <b>{escaped_title}</b>\n\n"
        if escaped_rich_text:
            base_message += f"{escaped_rich_text}\n\n"
        base_message += f"{FOOTER_TEXT}"

        base_message2 = f" \U0001F6CE <b>{escaped_title}</b>\n\n"
        if escaped_rich_text:
            base_message2 += f"{escaped_rich_text}\n\n"
        base_message2 += f"{FOOTER_TEXT2}"

        # Сначала отметим новость как опубликованную
        mark_as_posted(link)

        try:
            # Публикация в первом канале
            post_message(CHANNEL_ID, CHAT_THREAD_ID, base_message, images)
            logger.info(f"Новость '{title}' опубликована в первом канале Telegram")
            
            # Пауза между постами
            time.sleep(POST_DELAY)

            # Публикация во втором канале через 1 минуту
            time.sleep(60)
            post_message(CHANNEL_ID2, None, base_message2, images)
            logger.info(f"Новость '{title}' опубликована во втором канале Telegram")

        except Exception as e:
            logger.error(f"Ошибка при отправке новости '{title}' в Telegram: {e}")

def post_message(channel_id, thread_id, message, images):
    if images:
        image_urls = images.split(', ')
        media_group = [telebot.types.InputMediaPhoto(image_url) for image_url in image_urls]

        parts = split_message(message, IMAGE_MESSAGE_LIMIT)
        for part in parts:
            if len(media_group) > 0:
                media_group[0].caption = part
                media_group[0].parse_mode = 'HTML'
                if thread_id:
                    bot.send_media_group(chat_id=channel_id, media=media_group, reply_to_message_id=thread_id)
                else:
                    bot.send_media_group(chat_id=channel_id, media=media_group)
                media_group = []  # очистить media_group после отправки
            else:
                if thread_id:
                    bot.send_message(chat_id=channel_id, text=part, parse_mode='HTML', reply_to_message_id=thread_id, disable_web_page_preview=True)
                else:
                    bot.send_message(chat_id=channel_id, text=part, parse_mode='HTML', disable_web_page_preview=True)
    else:
        parts = split_message(message, MESSAGE_LIMIT)
        for part in parts:
            if thread_id:
                bot.send_message(chat_id=channel_id, text=part, parse_mode='HTML', reply_to_message_id=thread_id, disable_web_page_preview=True)
            else:
                bot.send_message(chat_id=channel_id, text=part, parse_mode='HTML', disable_web_page_preview=True)

if __name__ == "__main__":
    try:
        post_news_to_telegram()
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        sys.exit(1)
