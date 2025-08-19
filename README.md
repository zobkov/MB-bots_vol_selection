# Telegram Bot для отбора волонтеров МБ 2025

Бот для проведения отбора волонтеров с использованием aiogram 3.x и aiogram-dialog.

## Технологический стек

- **aiogram 3.x** - основной фреймворк для Telegram бота
- **aiogram-dialog** - система диалогов для удобного построения интерфейса
- **PostgreSQL** - основная база данных
- **Redis** - хранилище состояний FSM
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - система миграций

## Структура проекта

```
vol_selection_MB_bot/
├── config/
│   ├── config.py              # Конфигурация приложения
│   ├── selection_config.json  # Настройки этапов отбора
│   └── google_credentials.json.example
├── bot/
│   ├── dialogs/              # Диалоги бота
│   │   ├── start.py         # Стартовый диалог
│   │   ├── menu.py          # Главное меню
│   │   ├── application.py   # Анкета
│   │   └── departments.py   # Выбор отделов
│   ├── states/              # Состояния FSM
│   └── handlers.py          # Обработчики команд
├── database/
│   ├── models.py            # Модели базы данных
│   ├── db.py               # Подключение к БД
│   └── repositories.py     # Репозитории для работы с данными
├── alembic/                # Миграции
├── main.py                 # Точка входа
└── requirements.txt
```

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd vol_selection_MB_bot
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Заполните переменные в `.env`:

```env
# Bot Token (получить у @BotFather)
BOT_TOKEN=your_bot_token_here

# Database PostgreSQL
DB_USER=postgres
DB_PASS=your_password
DB_NAME=vol_bot
DB_HOST=localhost
DB_PORT=5432

# Redis (password опционален - можно оставить пустым)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Google (опционально, для будущего экспорта в Google Sheets)
GOOGLE_CREDENTIALS_PATH=config/google_credentials.json
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
GOOGLE_ENABLE_DRIVE=false
```

### 4. Настройка базы данных

Создайте базу данных PostgreSQL:

```sql
CREATE DATABASE vol_bot;
```

Примените миграции:

```bash
alembic upgrade head
```

### 5. Настройка Redis

Установите и запустите Redis:

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server
```

### 6. Запуск бота

```bash
python main.py
```

## Функциональность

### Команды бота

- `/start` - запуск бота, переход к стартовому диалогу
- `/menu` - переход в главное меню

### Диалоги

1. **Стартовый диалог** - приветствие с изображением и кнопкой перехода в меню
2. **Главное меню** - информация о текущем этапе, статус заявки, кнопки для заполнения анкеты и поддержки
3. **Анкета (1-й этап)** - пошаговое заполнение анкеты:
   - ФИО
   - Курс обучения (1-4 бакалавриат, 1-2 магистратура)
   - Проживание в общежитии
   - Корпоративная почта (@spbu.ru)
   - Контактный телефон
   - Личные качества
   - Оценка интереса к отделам (1-5)
   - Мотивация
   - Обзор и подтверждение

### Структура базы данных

#### Таблица `users`
- `telegram_id` - ID пользователя в Telegram
- `telegram_username` - username в Telegram
- `is_alive` - активность пользователя
- `is_blocked` - заблокирован ли пользователь
- `stage1_submitted` - статус подачи заявки ('submitted'/'not_submitted')

#### Таблица `applications` 
- Данные анкеты пользователя
- Оценки интереса к отделам (1-5)
- Связь с пользователем через `user_id`

## Конфигурация этапов

Настройки этапов отбора находятся в `config/selection_config.json`:

```json
{
  "selection_stages": {
    "stage1": {
      "name": "Первый этап - Анкета",
      "deadline": "21.09.2025 23:59",
      "results_date": "22.09.2025 12:00"
    },
    "stage2": {
      "name": "Второй этап - Тестовое задание", 
      "start_date": "22.09.2025 12:00"
    }
  },
  "departments": {
    "logistics": "Логистика",
    "marketing": "Маркетинг", 
    "pr": "PR",
    "program": "Программа",
    "partners": "Партнеры"
  },
  "support_contacts": {
    "main": "@support_user1",
    "technical": "@support_user2"
  }
}
```

## Логирование

Бот использует стандартное логирование Python. Уровень логирования можно настроить в `main.py`.

## Разработка

### Создание новых миграций

```bash
alembic revision --autogenerate -m "описание изменений"
alembic upgrade head
```

### Работа с диалогами

Диалоги построены на основе aiogram-dialog. Каждый диалог состоит из:
- Состояний (states) - определяют окна диалога
- Окон (windows) - содержат интерфейс и логику
- Геттеров (getters) - предоставляют данные для отображения
- Обработчиков (handlers) - обрабатывают действия пользователя

### Добавление новых функций

1. Определите новые состояния в `bot/states/`
2. Создайте диалог в `bot/dialogs/`
3. Зарегистрируйте диалог в `main.py`
4. При необходимости обновите модели БД и создайте миграцию

## Поддержка

При возникновении вопросов обращайтесь к документации:
- [aiogram](https://docs.aiogram.dev/)
- [aiogram-dialog](https://aiogram-dialog.readthedocs.io/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
