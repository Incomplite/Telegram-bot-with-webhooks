# Маникюрный Бот

Данный проект представляет собой демо-бота для мастера маникюра с использованием **FastAPI** для поднятия веб-сервера и обработки запросов, а также с реализацией Telegram MiniApp для приема заявок.
Бот работает через вебхуки и взаимодействует с базой данных **SQLite** с использованием **SQLAlchemy**. Веб-приложение поддерживает статические страницы и функционал для работы администратора и клиентов.

![Static Badge](https://img.shields.io/badge/Incomplite-Telegram--bot--with--webhooks-blue)
![GitHub top language](https://img.shields.io/github/languages/top/Incomplite/Telegram-bot-with-webhooks)

## Стек:
- **Backend**: FastAPI
- **Telegram API**: Aiogram + Webhooks
- **ORM**: SQLAlchemy
- **База данных**: SQLite
- **Миграции**: Alembic

## Установка

1. Клонирование репозитория

```bash
git clone https://github.com/Incomplite/Telegram-bot-with-webhooks.git
```

2. Переход в директорию бота

```bash
cd Telegram-bot-with-webhooks
```

3. Создание виртуального окружения

```bash
python3 -m venv venv
```

4. Активация виртуального окружения

```bash
venv/Scripts/activate
```

5. Установка зависимостей

```bash
pip3 install -r requirements.txt
```

6. Выполнение миграций Alembic

```bash
alembic upgrade head
```

7. Запуск бота.

```bash
uvicorn src.main:app
```

## Поддержка
Если у вас возникли сложности или вопросы по использованию, создайте 
[обсуждение](https://github.com/Incomplite/Telegram-bot-with-webhooks/issues/new/choose) в данном репозитории или напишите на электронную почту <blocktapok@gmail.com>.
