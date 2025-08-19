#!/bin/bash

# Скрипт мониторинга состояния бота
set -e

echo "🔍 Мониторинг состояния бота..."
echo "==============================="

# Проверка контейнеров
echo "📦 Статус контейнеров:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "💾 Использование ресурсов:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" $(docker-compose -f docker-compose.prod.yml ps -q)

echo ""
echo "🗂️ Размер логов:"
if [ -d "logs" ]; then
    du -sh logs/*
else
    echo "Директория logs не найдена"
fi

echo ""
echo "🚀 Последние 10 записей из лога бота:"
if [ -f "logs/bot.log" ]; then
    tail -n 10 logs/bot.log
else
    echo "Файл bot.log не найден"
fi

echo ""
echo "❌ Последние ошибки (если есть):"
if [ -f "logs/errors.log" ]; then
    if [ -s "logs/errors.log" ]; then
        tail -n 5 logs/errors.log
    else
        echo "Ошибок не найдено ✅"
    fi
else
    echo "Файл errors.log не найден"
fi

echo ""
echo "👥 Активность пользователей за последний час:"
if [ -f "logs/user_actions.log" ]; then
    if [ -s "logs/user_actions.log" ]; then
        # Показываем активность за последний час
        HOUR_AGO=$(date -d '1 hour ago' '+%Y-%m-%d %H')
        grep "$HOUR_AGO" logs/user_actions.log | wc -l | xargs echo "Действий:"
    else
        echo "Нет активности пользователей"
    fi
else
    echo "Файл user_actions.log не найден"
fi

echo ""
echo "🗄️ Подключение к базе данных:"
if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -q; then
    echo "✅ База данных доступна"
    # Показываем количество пользователей и заявок
    source .env
    USERS_COUNT=$(docker-compose -f docker-compose.prod.yml exec -T postgres psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM users;" | xargs)
    APPLICATIONS_COUNT=$(docker-compose -f docker-compose.prod.yml exec -T postgres psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM applications;" | xargs)
    echo "👤 Пользователей: $USERS_COUNT"
    echo "📋 Заявок: $APPLICATIONS_COUNT"
else
    echo "❌ База данных недоступна"
fi

echo ""
echo "📡 Подключение к Redis:"
if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis доступен"
    REDIS_KEYS=$(docker-compose -f docker-compose.prod.yml exec -T redis redis-cli dbsize | xargs)
    echo "🔑 Ключей в Redis: $REDIS_KEYS"
else
    echo "❌ Redis недоступен"
fi

echo ""
echo "==============================="
echo "✅ Мониторинг завершен"
