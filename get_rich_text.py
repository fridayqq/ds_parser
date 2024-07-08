import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
from loguru import logger
from database import fetch_unparsed_links, update_parsed, mark_as_parsed_and_posted

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка опций браузера
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')

# Инициализация драйвера Chrome
service = Service(ChromeDriverManager().install())

def get_rich_text():
    driver = webdriver.Chrome(service=service, options=chrome_options)
    rows = fetch_unparsed_links()

    updated_count = 0

    for row in rows:
        link, title = row
        driver.get(link)
        time.sleep(5)

        try:
            if 'подкаст' in title.lower():
                mark_as_parsed_and_posted(link)
                logger.info(f"Новость по ссылке '{link}' содержит подкаст и обновлена.")
                continue

            rich_text_element = driver.find_element(By.CLASS_NAME, 'Inner-Page__content')
            rich_text = rich_text_element.text

            update_parsed(link, rich_text)
            updated_count += 1
            logger.info(f"Новость по ссылке '{link}' обновлена с rich_text")

        except Exception as e:
            update_parsed(link)
            logger.error(f"Ошибка при извлечении rich_text по ссылке '{link}': {e}")

    if updated_count == 0:
        logger.info("Обновлять нечего, все новости уже обновлены.")
    else:
        logger.info(f"Обновлено новостей: {updated_count}")

    driver.quit()

if __name__ == "__main__":
    get_rich_text()
