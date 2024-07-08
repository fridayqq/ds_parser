FROM ubuntu:20.04

# Установите зависимости
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    software-properties-common

# Установите Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm ./google-chrome-stable_current_amd64.deb

# Установите ChromeDriver
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Установите Python и необходимые пакеты
RUN apt-get install -y python3 python3-pip
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

# Копируйте ваше приложение в контейнер
COPY . /app
WORKDIR /app

# Запустите ваше приложение
CMD ["python3", "scheduler.py"]
