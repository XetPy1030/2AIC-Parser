# Берем нужный базовый образ
FROM python:3.10-buster
# Копируем все файлы из текущей директории в /app контейнера
COPY ./ /app
# Устанавливаем все зависимости
RUN apk update && pip install -r /app/requirements.txt --no-cache-dir
# Устанавливаем приложение (Подробнее смотри Distutils)
RUN pip install -e /app
# Говорим контейнеру какой порт слушай
#EXPOSE 8080
# Запуск нашего приложения при старте контейнера
CMD python /app/bot.py

# В качестве альтернативы distutils можно просто указать что выполнить
#CMD python /app/src/app.py