#!/bin/bash

# Скрипт для автоматического обновления бота из Git репозитория
set -e

echo "🔄 Начинаем обновление бота..."

# Проверяем, что мы в Git репозитории
if [ ! -d ".git" ]; then
    echo "❌ Это не Git репозиторий!"
    exit 1
fi

# Проверяем, есть ли изменения в удаленном репозитории
echo "🔍 Проверяем обновления в репозитории..."
git fetch origin

# Получаем текущий коммит и последний коммит в origin/main
CURRENT_COMMIT=$(git rev-parse HEAD)
LATEST_COMMIT=$(git rev-parse origin/main)

if [ "$CURRENT_COMMIT" = "$LATEST_COMMIT" ]; then
    echo "✅ Бот уже обновлен до последней версии"
    exit 0
fi

echo "📥 Найдены новые изменения, начинаем обновление..."

# Создаем резервную копию перед обновлением
echo "💾 Создаем резервную копию..."
./deploy.sh

# Сохраняем изменения (если есть)
if ! git diff-index --quiet HEAD --; then
    echo "⚠️ Обнаружены локальные изменения, сохраняем их..."
    git stash push -m "Auto-stash before update $(date)"
fi

# Обновляем код
echo "📋 Получаем изменения..."
git pull origin main

# Проверяем изменения в зависимостях
if git diff --name-only $CURRENT_COMMIT $LATEST_COMMIT | grep -q "requirements.txt"; then
    echo "📦 Обнаружены изменения в зависимостях, пересобираем образ..."
    docker-compose -f docker-compose.prod.yml build --no-cache bot
fi

# Перезапускаем сервисы
echo "🔄 Перезапускаем сервисы..."
docker-compose -f docker-compose.prod.yml up -d

# Проверяем статус
echo "🔍 Проверяем статус после обновления..."
sleep 15
docker-compose -f docker-compose.prod.yml ps

# Проверяем логи на наличие ошибок
echo "📋 Проверяем логи на ошибки..."
if docker-compose -f docker-compose.prod.yml logs --tail=50 bot | grep -i error; then
    echo "⚠️ Обнаружены ошибки в логах, проверьте состояние бота"
else
    echo "✅ Ошибок в логах не найдено"
fi

echo "🎉 Обновление завершено успешно!"
echo "📊 Логи: docker-compose -f docker-compose.prod.yml logs -f bot"
