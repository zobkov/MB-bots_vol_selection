#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 Запуск бота для отбора волонтеров МБ 2025${NC}"

# Проверка существования .env файла
if [ ! -f .env ]; then
    echo -e "${RED}❌ Файл .env не найден!${NC}"
    echo -e "${YELLOW}Скопируйте .env.example в .env и заполните необходимые переменные.${NC}"
    exit 1
fi

# Проверка установки зависимостей
echo -e "${BLUE}📦 Проверка зависимостей...${NC}"
pip install -r requirements.txt

# Проверка подключения к Redis
echo -e "${BLUE}🔧 Проверка Redis...${NC}"
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ Redis не запущен. Попытка запуска...${NC}"
    # Для macOS
    if command -v brew &> /dev/null; then
        brew services start redis
    # Для Linux
    elif command -v systemctl &> /dev/null; then
        sudo systemctl start redis-server
    else
        echo -e "${RED}❌ Не удалось запустить Redis автоматически. Запустите его вручную.${NC}"
        exit 1
    fi
fi

# Применение миграций
echo -e "${BLUE}🗄️ Применение миграций базы данных...${NC}"
alembic upgrade head

# Запуск бота
echo -e "${GREEN}🚀 Запуск бота...${NC}"
python main.py
