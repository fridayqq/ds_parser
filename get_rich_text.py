import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
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
    wait = WebDriverWait(driver, 10)
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

            # Ожидание загрузки элемента
            rich_text_element = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'Inner-Page__content'))
            )
            rich_text = rich_text_element.text

            # Удаление текста из элементов с классом 'alt_under_img'
            alt_text_elements = driver.find_elements(By.CLASS_NAME, 'alt_under_img')
            for element in alt_text_elements:
                alt_text = element.text
                rich_text = rich_text.replace(alt_text, '')

            # Добавление пустой строки после каждого абзаца
            paragraphs = rich_text.split('\n')
            rich_text_with_newlines = '\n\n'.join(paragraphs)

            update_parsed(link, rich_text_with_newlines)
            updated_count += 1
            logger.info(f"Новость по ссылке '{link}' обновлена с rich_text")

        except NoSuchElementException:
            logger.warning(f"Rich text отсутствует в новости по ссылке '{link}'")
            update_parsed(link, rich_text=None)
        except Exception as e:
            update_parsed(link, rich_text=None)
            logger.error(f"Ошибка при извлечении rich_text по ссылке '{link}': no_rich_text")

    if updated_count == 0:
        logger.info("Обновлять нечего, все новости уже обновлены.")
    else:
        logger.info(f"Обновлено новостей: {updated_count}")

    driver.quit()

if __name__ == "__main__":
    get_rich_text()
