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
   4. `UPDATE_METHOD`=метод_обновления(webhook или pooling), в случае pooling 4-ый пункт можно пропустить
4. Создайте ключ шифрование и SSL сертификат с помощью команды: 
`openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 3650 -out cert.pem`
На шаге `Common Name (e.g. server FQDN or YOUR name) []` 
введите IP-адрес или домен сервера на который будут приходить вебхуки
5. Соберите образ контейнера с помощью команды `sudo docker build .`
6. Запустите контейнеры с помощью команды `sudo docker-compose up -d`
7. Проверяем работу бота

### Использование бота
1. `/start` для регистрации в боте
2. `/set_category <Имя категории>` создаёт категорию
3. `/`
