import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def parse_dropscapital():
    url = 'https://dropscapital.com/'

    # Настройка опций браузера
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Запуск в фоновом режиме
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    # Запуск браузера
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # Явное ожидание для загрузки страницы
    time.sleep(10)

    # Счётчик для общего номера li
    li_counter = 1

    # Подключение к базе данных SQLite
    conn = sqlite3.connect('news_data.db')
    cursor = conn.cursor()

    # Создание таблицы, если она не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            link TEXT PRIMARY KEY,
            title TEXT,
            text TEXT,
            images TEXT
        )
    ''')

    # Поиск всех секций
    sections = driver.find_elements(By.CLASS_NAME, 'Main-Infonoise')
    print(f"Найдено секций: {len(sections)}")

    for index, section in enumerate(sections):
        print(f"\nСекция {index + 1}")

        # Поиск всех ul с классом Main-Infonoise-Item__posts-list в текущей секции
        ul_elements = section.find_elements(By.CLASS_NAME, 'Main-Infonoise-Item__posts-list')
        print(f"Найдено списков ul: {len(ul_elements)}")

        for ul_index, ul in enumerate(ul_elements):

            # Поиск всех li с классом Main-Infonoise-Item__post-item в текущем ul
            li_elements = ul.find_elements(By.CLASS_NAME, 'Main-Infonoise-Item__post-item')
            print(f"Найдено элементов li: {len(li_elements)}")

            for li_index, li in enumerate(li_elements):
                print(f"\nЭлемент li {li_counter}")

                # Извлечение информации из элемента li
                try:
                    article = li.find_element(By.CLASS_NAME, 'Post-News')
                    link = article.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    title = article.find_element(By.CLASS_NAME, 'Post-News__title').text
                    text = article.find_element(By.TAG_NAME, 'p').text

                    # Поиск всех изображений в статье
                    images = article.find_elements(By.CLASS_NAME, 'Post-News__image')
                    image_urls = [img.get_attribute('src') for img in images]
                    image_urls_str = ', '.join(image_urls)

                    print(f"Ссылка: {link}")
                    print(f"Заголовок: {title}")
                    print(f"Текст: {text}")
                    print(f"Картинки: {image_urls}")

                    # Вставка данных в таблицу с обработкой конфликта по link
                    cursor.execute('''
                        INSERT OR IGNORE INTO news (link, title, text, images)
                        VALUES (?, ?, ?, ?)
                    ''', (link, title, text, image_urls_str))
                    conn.commit()

                except Exception as e:
                    print(f"Ошибка при обработке элемента li {li_counter}: {e}")

                # Увеличиваем счётчик для общего номера li
                li_counter += 1

    # Закрытие соединения с базой данных и браузера
    conn.close()
    driver.quit()

# Вызов функции
parse_dropscapital()
