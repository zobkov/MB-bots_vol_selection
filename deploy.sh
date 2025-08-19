#!/bin/bash

# Скрипт для автоматического деплоя бота
set -e

echo "🚀 Начинаем деплой бота..."

# Проверяем, что .env файл существует
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден! Скопируйте .env.example в .env и заполните настройки."
    exit 1
fi

# Загружаем переменные окружения
source .env

# Проверяем обязательные переменные
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN не задан в .env файле"
    exit 1
fi

if [ -z "$DB_USER" ] || [ -z "$DB_PASS" ] || [ -z "$DB_NAME" ]; then
    echo "❌ Настройки базы данных не заданы в .env файле"
    exit 1
fi

echo "✅ Конфигурация проверена"

# Останавливаем старые контейнеры
echo "🛑 Останавливаем старые контейнеры..."
docker-compose -f docker-compose.prod.yml down

# Создаем резервную копию БД (если есть запущенный контейнер)
echo "💾 Создаем резервную копию базы данных..."
mkdir -p backups
BACKUP_FILE="backups/backup_$(date +%Y%m%d_%H%M%S).sql"

if docker ps -q -f name=vol_selection_postgres &> /dev/null; then
    docker exec vol_selection_postgres pg_dump -U $DB_USER $DB_NAME > $BACKUP_FILE
    echo "✅ Резервная копия создана: $BACKUP_FILE"
else
    echo "ℹ️ База данных не запущена, резервная копия пропущена"
fi

# Собираем новые образы
echo "🔨 Собираем Docker образы..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Запускаем сервисы
echo "▶️ Запускаем сервисы..."
docker-compose -f docker-compose.prod.yml up -d

# Проверяем статус
echo "🔍 Проверяем статус сервисов..."
sleep 10
docker-compose -f docker-compose.prod.yml ps

# Проверяем логи бота
echo "📋 Последние логи бота:"
docker-compose -f docker-compose.prod.yml logs --tail=20 bot

echo "🎉 Деплой завершен!"
echo "📊 Просмотр логов: docker-compose -f docker-compose.prod.yml logs -f bot"
echo "🌐 Веб-интерфейс логов: http://localhost:8080"
echo "🛑 Остановка: docker-compose -f docker-compose.prod.yml down"
