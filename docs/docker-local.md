# Локальный Docker-стек (корень монорепозитория)

Файлы в корне: **`docker-compose.yml`** (Postgres, Redis, MinIO, Traefik) и **`docker-compose.local.yml`** (оверлей: **auth**, **catalog**, **commerce**, **payments** за Traefik и прямые порты для отладки).

Запуск из корня:

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

## Hosts

Для маршрута Traefik к auth добавьте в `hosts` (Windows: `C:\Windows\System32\drivers\etc\hosts`):

```text
127.0.0.1 auth.localhost
127.0.0.1 catalog.localhost
127.0.0.1 commerce.localhost
127.0.0.1 payments.localhost
```

## Traefik

- Образ и провайдер Docker заданы в `docker-compose.yml`.
- Точка входа HTTP **`web`**: контейнер слушает **`:80`**, на хосте опубликовано **`8080`** (запросы идут на `http://<host>:8080`).
- **`providers.docker.exposedbydefault=false`** — в маршруты попадают только сервисы с `traefik.enable=true`.
- Панель / API Traefik (режим `api.insecure`, только для разработки): хост **`8081`** → контейнер **`:8080`**.

### Маршруты HTTP (через Traefik)

| Хост (на порту хоста `8080`) | Router (имя в labels) | Сервис Compose | Порт контейнера бэкенда |
|------------------------------|------------------------|----------------|-------------------------|
| `auth.localhost` | `auth` | `auth` | `8000` |
| `catalog.localhost` | `catalog` | `catalog` | `8000` |
| `commerce.localhost` | `commerce` | `commerce` | `8000` |
| `payments.localhost` | `payments` | `payments` | `8000` |

Соответствующие labels в `docker-compose.local.yml` (сводка): для каждого сервиса — `traefik.enable=true`, `Host(\`<имя>.localhost\`)`, `entrypoints=web`, `loadbalancer.server.port=8000`.

Проверка OIDC: `http://auth.localhost:8080/.well-known/openid-configuration`.

OpenAPI (примеры): `http://catalog.localhost:8080/api/openapi.json`, `http://commerce.localhost:8080/api/openapi.json`, `http://payments.localhost:8080/api/openapi.json`.

### База `zhuchka_catalog`

При **первом** создании тома Postgres скрипт `docker/postgres/docker-entrypoint-initdb.d/02-zhuchka-catalog.sql` создаёт БД `zhuchka_catalog`. Если том **`zhuchka_pgdata` уже существовал** без этой базы, выполните один раз:

```bash
docker compose -f docker-compose.yml exec postgres psql -U zhuchka -d zhuchka_auth -c "CREATE DATABASE zhuchka_catalog OWNER zhuchka;"
```

### База `zhuchka_commerce`

Аналогично: при первом init тома выполняется `03-zhuchka-commerce.sql`. Если базы не было:

```bash
docker compose -f docker-compose.yml exec postgres psql -U zhuchka -d zhuchka_auth -c "CREATE DATABASE zhuchka_commerce OWNER zhuchka;"
```

### База `zhuchka_payments`

При первом init тома выполняется `04-zhuchka-payments.sql`. Если базы не было:

```bash
docker compose -f docker-compose.yml exec postgres psql -U zhuchka -d zhuchka_auth -c "CREATE DATABASE zhuchka_payments OWNER zhuchka;"
```

## Прямые порты (минуя Traefik)

Удобно для клиентов на хосте (IDE, CLI) и для отладки без Host-заголовка.

| Порт хоста | Сервис | Назначение |
|------------|--------|------------|
| `5432` | `postgres` | PostgreSQL |
| `6379` | `redis` | Redis |
| `9000` | `minio` | S3 API |
| `9001` | `minio` | веб-консоль MinIO |
| `8000` | `auth` | HTTP auth (оверлей; тот же сервис, что за Traefik) |
| `8001` | `catalog` | HTTP catalog (оверлей) |
| `8002` | `commerce` | HTTP commerce (оверлей) |
| `8003` | `payments` | HTTP payments (оверлей) |

Из других контейнеров в той же сети Compose имена хостов: `postgres`, `redis`, `minio`, `auth`, `catalog`, `commerce`, `payments` (см. `docker-compose.yml` / оверлей).

## MinIO

Бакеты для медиа по умолчанию: **`keyboards`**, **`parts`** (создаётся одноразовым контейнером `minio-init`). Учётные данные администратора задаются в `docker-compose.yml` (`MINIO_ROOT_*`).

## Пример переменных окружения

Файл с плейсхолдерами (без реальных ключей): **[`docker/local.example.env`](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards/blob/dev/docker/local.example.env)** (в репозитории, вне каталога `docs/`). Имена переменных с префиксом `ZCH_LOCAL_*` не подхватываются Compose автоматически — это ориентир для приложений и скриптов на хосте.
