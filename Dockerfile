FROM python:3.9-slim

# Установка зависимостей
RUN apt update && apt install -y \
    wget \
    bzip2 \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libasound2 \
    libx11-xcb1 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    libxcb-shm0 \
    libxcb-dri3-0 \
    libxshmfence1 \
    libxinerama1 \
    libxkbcommon0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libdrm2 \
    fonts-liberation \
    libgl1 \
    libgbm1 \
    libpango-1.0-0 \
    && apt clean

# Установка Firefox 124.0.2
RUN wget https://ftp.mozilla.org/pub/firefox/releases/124.0.2/linux-x86_64/en-US/firefox-124.0.2.tar.bz2 && \
    tar -xjf firefox-124.0.2.tar.bz2 && \
    mv firefox /opt/firefox124 && \
    ln -sf /opt/firefox124/firefox /usr/bin/firefox

# Установка geckodriver 0.36.0
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz && \
    tar -xvzf geckodriver-v0.36.0-linux64.tar.gz && \
    mv geckodriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/geckodriver

# Установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Старт
CMD ["python", "main.py"]
