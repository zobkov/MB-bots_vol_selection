.PHONY: help dev-up dev-down prod-up prod-down deploy logs build clean backup

help: ## Показать помощь
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev-up: ## Запустить сервисы для разработки (только БД и Redis)
	docker-compose -f docker-compose.dev.yml up -d

dev-down: ## Остановить сервисы разработки
	docker-compose -f docker-compose.dev.yml down

prod-up: ## Запустить все сервисы в продакшн режиме
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## Остановить продакшн сервисы
	docker-compose -f docker-compose.prod.yml down

deploy: ## Полный деплой с резервной копией
	./deploy.sh

build: ## Пересобрать Docker образы
	docker-compose -f docker-compose.prod.yml build --no-cache

logs: ## Показать логи бота
	docker-compose -f docker-compose.prod.yml logs -f bot

logs-all: ## Показать логи всех сервисов
	docker-compose -f docker-compose.prod.yml logs -f

status: ## Показать статус контейнеров
	docker-compose -f docker-compose.prod.yml ps

backup: ## Создать резервную копию БД
	@if [ -f .env ]; then \
		source .env && \
		mkdir -p backups && \
		BACKUP_FILE="backups/manual_backup_$$(date +%Y%m%d_%H%M%S).sql" && \
		docker exec vol_selection_postgres pg_dump -U $$DB_USER $$DB_NAME > $$BACKUP_FILE && \
		echo "Резервная копия создана: $$BACKUP_FILE"; \
	else \
		echo "Файл .env не найден!"; \
		exit 1; \
	fi

clean: ## Очистить неиспользуемые Docker ресурсы
	docker system prune -f

clean-all: ## Полная очистка (ОСТОРОЖНО: удалит все данные!)
	docker-compose -f docker-compose.prod.yml down -v
	docker system prune -af

restart: ## Перезапустить бота
	docker-compose -f docker-compose.prod.yml restart bot

shell: ## Зайти в контейнер бота
	docker-compose -f docker-compose.prod.yml exec bot bash

install: ## Установить зависимости локально
	pip install -r requirements.txt

run-local: ## Запустить бота локально (нужны dev сервисы)
	python3 main.py

test-syntax: ## Проверить синтаксис всех Python файлов
	find . -name "*.py" -not -path "./.venv/*" -exec python3 -m py_compile {} \;

test-imports: ## Проверить импорты
	python3 -c "from config.config import load_config; from database.models import User, Application; from utils.logging_config import setup_logging; print('✅ Все импорты успешны')"

docker-build: ## Собрать Docker образ
	docker build -t vol_selection_bot:latest .

docker-test: ## Протестировать Docker образ
	docker run --rm vol_selection_bot:latest python3 -c "print('✅ Docker образ работает')"
