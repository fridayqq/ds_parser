import time
import random
import subprocess
from loguru import logger
from dotenv import load_dotenv
import sys

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка логирования
logger.remove()  # Удаление стандартного логгера
logger.add("scheduler.log", rotation="10 MB", retention="10 days", level="DEBUG")  # Логирование в файл
logger.add(sys.stderr, level="INFO")  # Оставляем логи уровня INFO и выше в консоли

def run_script(script_name):
    try:
        logger.info(f"Запуск {script_name}")
        subprocess.run(["python", script_name], check=True)
        logger.info(f"{script_name} успешно выполнен")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при выполнении {script_name}: {e}")

def main():
    scripts = ["parse_web_page.py", "get_rich_text.py", "telegram_poster.py"]
    
    while True:
        for script in scripts:
            run_script(script)
            sleep_time = random.randint(30, 60)  # Случайное время от 5 до 10 минут
            logger.info(f"Пауза {sleep_time // 60} минут между выполнением скриптов")
            time.sleep(sleep_time)

if __name__ == "__main__":
    main()
