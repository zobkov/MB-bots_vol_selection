# 🚀 Деплой бота для отбора волонтеров

## 📋 Оглавление
- [Быстрый старт](#быстрый-старт)
- [Настройка окружения](#настройка-окружения)
- [Команды для управления](#команды-для-управления)
- [Мониторинг](#мониторинг)
- [Логирование](#логирование)
- [Резервное копирование](#резервное-копирование)
- [Устранение неполадок](#устранение-неполадок)

## 🚀 Быстрый старт

### 1. Подготовка сервера
```bash
# Установка Docker и Docker Compose (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Перелогинься или выполни:
newgrp docker

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Клонирование репозитория
```bash
git clone <your-repository-url>
cd vol_selection_MB_bot
```

### 3. Настройка конфигурации
```bash
# Копируем пример конфигурации
cp .env.example .env

# Редактируем конфигурацию
nano .env
```

### 4. Первый запуск
```bash
# Делаем скрипты исполняемыми
chmod +x deploy.sh monitor.sh update.sh

# Запускаем деплой
./deploy.sh
```

## ⚙️ Настройка окружения

### Обязательные переменные в .env:
```bash
# Токен бота от @BotFather
BOT_TOKEN=your_bot_token_here

# База данных PostgreSQL
DB_USER=postgres
DB_PASS=your_secure_password
DB_NAME=vol_bot
DB_HOST=postgres  # Для Docker
DB_PORT=5432

# Redis (пароль опционален)
REDIS_HOST=redis  # Для Docker
REDIS_PORT=6379
REDIS_PASSWORD=  # Можно оставить пустым

# Уровень логирования
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### Опциональные переменные (Google Sheets):
```bash
GOOGLE_CREDENTIALS_PATH=config/google_credentials.json
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
GOOGLE_ENABLE_DRIVE=false
```

## 🛠️ Команды для управления

### Makefile команды:
```bash
make help              # Показать все доступные команды
make dev-up            # Запустить только БД и Redis для разработки
make prod-up           # Запустить все сервисы в продакшн
make deploy            # Полный деплой с резервной копией
make logs              # Показать логи бота
make status            # Показать статус контейнеров
make backup            # Создать резервную копию БД
make restart           # Перезапустить бота
make clean             # Очистить неиспользуемые Docker ресурсы
```

### Прямые Docker Compose команды:
```bash
# Запуск в продакшн
docker-compose -f docker-compose.prod.yml up -d

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f bot

# Остановка
docker-compose -f docker-compose.prod.yml down

# Перезапуск конкретного сервиса
docker-compose -f docker-compose.prod.yml restart bot
```

## 📊 Мониторинг

### Веб-интерфейс логов
После запуска доступен по адресу: `http://your-server:8080`
- Показывает логи всех контейнеров в реальном времени
- Удобный поиск и фильтрация

### Скрипт мониторинга
```bash
./monitor.sh
```
Показывает:
- Статус контейнеров
- Использование ресурсов
- Размер логов
- Последние записи
- Статистику пользователей
- Состояние БД и Redis

### Healthcheck
Бот имеет встроенный healthcheck на порту 8000:
```bash
curl http://localhost:8000/health
```

## 📝 Логирование

### Структура логов:
```
logs/
├── bot.log           # Общие логи бота
├── errors.log        # Только ошибки
├── user_actions.log  # Действия пользователей
└── database.log      # Операции с БД
```

### Конфигурация логирования:
- Ротация файлов при достижении размера
- Сохранение нескольких архивных версий
- Разные уровни детализации
- Автоматическое логирование всех пользовательских действий

### Просмотр логов:
```bash
# Последние записи
tail -f logs/bot.log

# Поиск ошибок
grep -i error logs/bot.log

# Действия конкретного пользователя
grep "USER:123456" logs/user_actions.log
```

## 💾 Резервное копирование

### Автоматическое резервное копирование
При каждом деплое создается резервная копия БД в папке `backups/`

### Ручное создание резервной копии:
```bash
make backup
```

### Восстановление из резервной копии:
```bash
# Найди нужную резервную копию
ls -la backups/

# Восстанови данные
source .env
cat backups/backup_YYYYMMDD_HHMMSS.sql | docker exec -i vol_selection_postgres psql -U $DB_USER -d $DB_NAME
```

## 🔄 Автоматическое обновление

### Обновление из Git:
```bash
./update.sh
```
Скрипт:
- Проверяет наличие обновлений
- Создает резервную копию
- Обновляет код
- Перезапускает сервисы
- Проверяет корректность работы

### Настройка автоматических обновлений (cron):
```bash
# Редактируем crontab
crontab -e

# Добавляем строку для проверки обновлений каждый день в 3:00
0 3 * * * cd /path/to/vol_selection_MB_bot && ./update.sh >> logs/updates.log 2>&1
```

## 🚨 Устранение неполадок

### Проверка статуса сервисов:
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Общие проблемы:

#### 1. Бот не отвечает
```bash
# Проверяем логи
docker-compose -f docker-compose.prod.yml logs bot

# Проверяем healthcheck
curl http://localhost:8000/health

# Перезапускаем
docker-compose -f docker-compose.prod.yml restart bot
```

#### 2. Проблемы с базой данных
```bash
# Проверяем подключение
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# Проверяем логи БД
docker-compose -f docker-compose.prod.yml logs postgres
```

#### 3. Проблемы с Redis
```bash
# Проверяем подключение
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Очищаем кэш Redis (если нужно)
docker-compose -f docker-compose.prod.yml exec redis redis-cli flushall
```

#### 4. Нехватка места на диске
```bash
# Очистка старых логов Docker
docker system prune -f

# Очистка старых образов
docker image prune -a

# Очистка логов бота (осторожно!)
find logs/ -name "*.log" -mtime +30 -delete
```

### Полный перезапуск:
```bash
# Остановка всех сервисов
docker-compose -f docker-compose.prod.yml down

# Очистка
docker system prune -f

# Повторный деплой
./deploy.sh
```

## 🔐 Безопасность

### Рекомендации:
1. Используйте сильные пароли для БД
2. Ограничьте доступ к портам (только необходимые)
3. Регулярно обновляйте образы
4. Мониторьте логи на подозрительную активность
5. Настройте файрвол

### Настройка файрвола (UFW):
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8080/tcp  # Веб-интерфейс логов
sudo ufw enable
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `./monitor.sh`
2. Убедитесь, что все переменные окружения заданы
3. Проверьте статус сервисов
4. Создайте issue в репозитории с логами
