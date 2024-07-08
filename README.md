# ds_parser

Этот проект предназначен для автоматического парсинга новостей с сайта, обработки текстового контента и публикации новостей в Telegram канал.

Выполняет по порядку следующие действия:
1) Парсит сайт с новостями в БД sqlite
2) Удаляет подкасты
3) Обогащает новости текстом, где возможно
4) Парсит БД на предмет незапощенных новостей
5) Постит новости в ТГ канал


## Структура проекта

- `parse_web_page.py` - скрипт для парсинга новостей с сайта и сохранения их в базу данных.
- `get_rich_text.py` - скрипт для обработки текста новостей и обновления базы данных.
- `telegram_poster.py` - скрипт для публикации новостей в Telegram канал.
- `scheduler.py` - скрипт для последовательного запуска вышеупомянутых скриптов с рандомными промежутками времени между запусками.
- `database.py` - вспомогательный скрипт с функциями для работы с БД

## Требования

- Python 3.6+
- Установленные библиотеки:
  - `selenium`
  - `loguru`
  - `python-dotenv`
  - `telebot`
  - `sqlite3` (входит в стандартную библиотеку Python)

## Установка

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/your-username/telegram-news-poster.git
   cd telegram-news-poster
   ```

2. Создайте и активируйте виртуальное окружение:
   ```sh
   python -m venv venv
   source venv/bin/activate  # Для Windows: venv\Scripts\activate
   ```

3. Установите зависимости:

    '''
    pip install -r requirements.txt
    '''

4. Создайте файл `.env` и добавьте необходимые переменные окружения


## Использование

### Запуск парсинга и публикации новостей

Для последовательного запуска всех скриптов используйте `scheduler.py`:

python scheduler.py

`scheduler.py` будет запускать `parse_web_page.py`, `get_rich_text.py` и `telegram_poster.py` по очереди с рандомными промежутками времени между 5 и 10 минут.

### Описание скриптов

- `parse_web_page.py`: Парсит новости с сайта и сохраняет их в базу данных SQLite (`news_data.db`).
- `get_rich_text.py`: Обрабатывает текст новостей и обновляет записи в базе данных.
- `telegram_poster.py`: Публикует новости из базы данных в Telegram канал.
- `scheduler.py`: Запускает вышеуказанные скрипты последовательно с паузами между запусками.

## Логирование

Логи каждого запуска скрипта сохраняются в файл с именем `scheduler_{time}.log` в формате `rotation="1 MB"` и `retention="10 days"`.

## Пример файла `.env`

'''
TELEGRAMBOT_API_KEY="your_telegram_bot_api_key"
MODE="production"
CHAT_ID="your_chat_id"
CHAT_THREAD_ID1=0
FOOTER_TEXT='your_footer_text'
POST_DELAY=5
NEWS_SITE_URL="https://secret_website.com/"
```
