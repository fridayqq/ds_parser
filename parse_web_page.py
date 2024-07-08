import sqlite3
import time
import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from dotenv import load_dotenv
import os
from loguru import logger

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройки базы данных
DB_PATH = 'news_data.db'
NEWS_SITE_URL = os.getenv('NEWS_SITE_URL')

# Проверьте, загружается ли переменная окружения
if not NEWS_SITE_URL:
    raise EnvironmentError("Переменная окружения NEWS_SITE_URL не установлена.")

# Настройка опций браузера
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

capabilities = DesiredCapabilities.FIREFOX
capabilities['marionette'] = True


firefox_options = Options()
firefox_options.add_argument('--headless')  # Запуск в режиме без графического интерфейса, если нужно
firefox_options.add_argument('--no-sandbox')
firefox_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Firefox(options=firefox_options, executable_path='/usr/local/bin/geckodriver')


def fetch_news():
    logger.info(f"Начало парсинга сайта: {NEWS_SITE_URL}")
    driver = webdriver.Firefox(capabilities=capabilities,options=firefox_options)
    driver.set_page_load_timeout(60) 
    driver.get(NEWS_SITE_URL)
    time.sleep(10)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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
                    cursor.execute('SELECT COUNT(1) FROM news WHERE link = ?', (link,))
                    exists = cursor.fetchone()[0]

                    if not exists:
                        cursor.execute(
                            'INSERT INTO news (link, title, images) VALUES (?, ?, ?)',
                            (link, title, image_urls)
                        )
                        conn.commit()
                        new_news_count += 1
                        logger.info(f"Новость '{title}' добавлена в базу данных")
                except Exception as e:
                    logger.error(f"Ошибка при обработке новости: {e}")

    if new_news_count == 0:
        logger.info("База данных актуальна, новых новостей нет.")

    conn.close()
    driver.quit()

if __name__ == "__main__":
    from database import create_table
    create_table()
    fetch_news()
