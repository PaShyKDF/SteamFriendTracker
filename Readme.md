# Steam Friend Tracker
Steam Friend Tracker - Telegram бот, работающий на основе Steam Web API. Бот предназначен для получения своевременного уведомления о том, что твой друг решил поиграть в игру. Представим ситуацию, что ты гуляешь, а твой друг или компания друзей идут играть. Увидев сообщение, можно попросить их подождать тебя 10 минут, пока ты дойдешь домой.
Или родитель удаленно получает сообщение о том, что его ребенок вместо домашней работы сел играть в игры😉.

Бот построен на асинхронной библиотеке Telebot, использует в качестве базы данных PostgreSQL и PGAdmin для управления ей. Все приложения упакованы в Docker контейнеры и запускаются через Docker-Compose. Также проект обновляется и поддерживается через технологию CI/CD и GitHub Actions.

Ссылка на сайт: https://t.me/Steam_Friend_Tracker_Bot

### Стек технологий:
<img src="https://img.shields.io/badge/Python-3776ab?style=for-the-badge&logo=python&logoColor=yellow"/> <img src="https://img.shields.io/badge/PostgreSQL-50b0f0?style=for-the-badge&logo=postgresql&logoColor=white"/> <img src="https://img.shields.io/badge/PGAdmin-326690?style=for-the-badge&logo=postgresql&logoColor=white"/> <img src="https://img.shields.io/badge/CI&CD-B8860B?style=for-the-badge"/> <img src="https://img.shields.io/badge/github actions-4B0082?style=for-the-badge&logo=githubactions&logoColor=2088FF"/> <img src="https://img.shields.io/badge/docker-1d63ed?style=for-the-badge&logo=docker&logoColor=white"/> <img src="https://img.shields.io/badge/nginx-006400?style=for-the-badge&logo=nginx&logoColor=32CD32"/> <img src="https://img.shields.io/badge/json-000000?style=for-the-badge&logo=json&logoColor=white"/> <img src="https://img.shields.io/badge/yaml-FF0000?style=for-the-badge&logo=yaml&logoColor=white"/>

# Инструкция по запуску проекта
### Чтобы запустить проект, нужно установить на локальную машину docker. Все ниже перечисленные действия будут для ОС Ubuntu Linux.

1. Скачайте и установите curl — консольную утилиту, которая умеет скачивать файлы по команде пользователя:
```bash
sudo apt update
sudo apt install curl
```
2. С помощью утилиты curl скачайте скрипт для установки докера с официального сайта. Этот скрипт хорош тем, что сам определит и настроит вашу операционную систему.
```bash
curl -fSL https://get.docker.com -o get-docker.sh
```
Параметр -o get-docker.sh просит сохранить ответ сервера в файл get-docker.sh.
3. Запустите сохранённый скрипт с правами суперпользователя:
```bash
sudo sh ./get-docker.sh
```
4. Дополнительно к Docker установите утилиту Docker Compose:
```bash
sudo apt install docker-compose-plugin
```
Проверьте, что Docker работает:
```bash
sudo systemctl status docker
```
### После установки Docker и Docker-compose можно запускать проект:
1. В корневой директории создайте файл .env и укажите параметры для Базы Данных, PGAdmin и токен телеграм бота. Пример:
```
TELEGRAM_TOKEN=693918****:AAE8OkE1d6mY********
POSTGRES_USER=Имя пользователя
POSTGRES_PASSWORD=Пароль
POSTGRES_DB=Имя базы даннх
DB_HOST=Название контейнера с базой данных
DB_PORT=5432
PGADMIN_DEFAULT_EMAIL=Почту для входа в PGAdmin
PGADMIN_DEFAULT_PASSWORD=Пароль от PGAdmin
```
2. В корневой директории запустите docker-compose командой:
```bash
sudo docker compose up -d --build
```
3. Далее нужно создать в Базе Данных таблицы командой:
```bash
sudo docker compose exec tg_bot python migrations.py
```
4. Чтобы остановить бот:
```bash
sudo docker compose stop
```
### Инструкция по входу в PGAdmin:
1. Откройте в браузере ссылку:
```
http://127.0.0.1:5005
```
2. Введите почту и пароль, которую указывали в файле .env
3. Далее во вкладке Сервер нужно добавить Сервер: 
Во вкладке Соединение указать адрес сервера как имя контейнера БД и порт как 5432. Также указать пароль, имя БД и имя пользователя из. Env файла.