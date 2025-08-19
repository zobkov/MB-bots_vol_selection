# Запустить Postgres
docker run -d \
  --name vol_selection_postgres \
  -e POSTGRES_USER=vol_selection_user \
  -e POSTGRES_PASSWORD=vol_selection_pass \
  -e POSTGRES_DB=vol_selection_db \
  -p 5432:5432 \
  postgres:15

# Запустить Redis
docker run -d \
  --name vol_selection_redis \
  -p 6380:6379 \
  redis:7