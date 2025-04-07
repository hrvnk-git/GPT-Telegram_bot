# GPT-Telegram_bot

Telegram бот с интеграцией OpenAI GPT API.

## Описание

Этот бот позволяет пользователям общаться с ChatGPT прямо в Telegram. Он поддерживает обработку текстовых сообщений, голосовых сообщений и изображений.

## Возможности

- Обработка текстовых сообщений через GPT
- Анализ изображений с описанием содержимого
- Транскрибация голосовых сообщений в текст
- Управление доступом пользователей
- Сохранение контекста диалога
- История сообщений

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/hrvnk-git/GPT-Telegram_bot.git
cd GPT-Telegram_bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе `.env example` и заполните необходимые переменные:
```
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
AUTHORIZED_USER_ID=your_telegram_id
```

4. Запустите бота:
```bash
python main.py
```

## Docker

Для запуска в Docker:

```bash
docker compose up -d
```

## Команды бота

- `/start` - Начать диалог с ботом
- `/reset` - Сбросить контекст диалога
- `/id` - Узнать свой ID в Telegram

## Технологии

- Python 3.12+
- aiogram 3.19.0
- OpenAI API
- SQLite (для хранения данных)
- Docker

## Структура проекта

```
GPT-Telegram_bot/
├── database/         # Модули для работы с БД
├── handlers/         # Обработчики команд и сообщений
├── keyboards/        # Клавиатуры бота
├── middlewares/      # Промежуточные обработчики
├── utils/           # Вспомогательные функции
├── main.py          # Точка входа
└── config.py        # Конфигурация
```

## Лицензия

MIT