from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

                    # Переход по ссылке и поиск rich-text на новой странице
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[1])
                    driver.get(link)
                    time.sleep(5)  # Явное ожидание для загрузки новой страницы

                    try:
                        rich_text_element = driver.find_element(By.CLASS_NAME, 'Inner-Page__content')
                        rich_text = rich_text_element.text
                    except:
                        rich_text = 'Текст не найден'

                    # Закрытие новой вкладки и возврат на основную страницу
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                    # Поиск всех изображений в статье
                    images = article.find_elements(By.CLASS_NAME, 'Post-News__image')
                    image_urls = [img.get_attribute('src') for img in images]

                    print(f"Ссылка: {link}")
                    print(f"Заголовок: {title}")
                    print(f"Текст: {text}")
                    print(f"Дополнительный текст: {rich_text}")
                    print(f"Картинки: {image_urls}")

                except Exception as e:
                    print(f"Ошибка при обработке элемента li {li_counter}: {e}")

                # Увеличиваем счётчик для общего номера li
                li_counter += 1

    driver.quit()

# Вызов функции
parse_dropscapital()
