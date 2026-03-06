FROM python:3.12-slim

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    gnupg2 curl unzip fonts-liberation libnss3 libxss1 libasound2 \
    libatk-bridge2.0-0 libatk1.0-0 libcups2 libx11-xcb1 libxcomposite1 \
    libxcursor1 libxdamage1 libxrandr2 libgbm1 libpangocairo-1.0-0 \
    libpango-1.0-0 xdg-utils

# Добавляем репозиторий Google Chrome
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux-signing-key.gpg
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-key.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list

# Устанавливаем Chrome
RUN apt-get update && apt-get install -y google-chrome-stable

WORKDIR /app
COPY requirements.txt .
COPY .env .
RUN pip install --no-cache-dir -r requirements.txt
# Копируем исходный код
COPY . .
EXPOSE 8888
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]

