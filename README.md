# ViditaSystemsTestTask

## Тестовое задание ViditaSystems

### Установка и настройка

1. Склонируйте репозиторий при помощи команды `git clone https://github.com/meetinger/ViditaSystemsTestTask` 
и перейдите в директорию репозитория
2. Создайте нового бота в https://t.me/BotFather
3. Отредактируйте файлы .env_template и .env_docker_template и переименуйте их в .env и .env_docker соответственно
   1. `BOT_TOKEN`=ваш_токен_из_BotFather
   2. `WEBHOOK_PORT`=порт_для_вебхуков
   3. `WEBHOOK_URL`=url_для_вебхуков
4. Соберите образ контейнера с помощью команды `sudo docker build .`
5. Запустите контейнеры с помощью команды `sudo docker-compose up -d`
6. Проверяем работу бота

### Использование бота
1. `/start` для регистрации в боте
2. `/set_category <Имя категории>` создаёт категорию
3. 
