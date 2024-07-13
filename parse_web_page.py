import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
from loguru import logger
from database import create_table, link_exists, insert_news

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройки базы данных
NEWS_SITE_URL = os.getenv('NEWS_SITE_URL')

# Проверьте, загружается ли переменная окружения
if not NEWS_SITE_URL:
    raise EnvironmentError("Переменная окружения NEWS_SITE_URL не установлена.")

# Настройка опций браузера
chrome_options = Options()
chrome_options.add_argument('--headless')  # Запуск в режиме без графического интерфейса
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Инициализация драйвера Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def fetch_news():
    logger.info(f"Начало парсинга сайта: {NEWS_SITE_URL}")
    driver.set_page_load_timeout(60)
    driver.get(NEWS_SITE_URL)
    time.sleep(10)

    new_news_count = 0

    sections = driver.find_elements(By.CLASS_NAME, 'Main-Infonoise')
    for section in sections:
        ul_elements = section.find_elements(By.CLASS_NAME, 'Main-Infonoise-Item__posts-list')
        for ul in ul_elements:
            li_elements = ul.find_elements(By.CLASS_NAME, 'Main-Infonoise-Item__post-item')
            for li in li_elements:
                try:
                    article = li.find_element(By.CLASS_NAME, 'Post-News')
                    link = article.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    title = article.find_element(By.CLASS_NAME, 'Post-News__title').text
                    images = article.find_elements(By.CLASS_NAME, 'Post-News__image')
                    image_urls = ', '.join([img.get_attribute('src') for img in images])

                    # Проверка наличия новости в базе данных
                    if not link_exists(link):
                        insert_news(link, title, image_urls)
                        new_news_count += 1
                        logger.info(f"Новость '{title}' добавлена в базу данных")
                except Exception as e:
                    logger.error(f"Ошибка при обработке новости: {e}")

    if new_news_count == 0:
        logger.info("База данных актуальна, новых новостей нет.")

    driver.quit()

if __name__ == "__main__":
    create_table()
    fetch_news()
