# Локальный Docker-стек (корень монорепозитория)

Файлы в корне: **`docker-compose.yml`** (Postgres, Redis, MinIO, Traefik) и **`docker-compose.local.yml`** (оверлей: все основные Python API из `services/*` за Traefik и прямые порты для отладки).

Запуск из корня:

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

## Hosts

Для маршрута Traefik добавьте в `hosts` (Windows: `C:\Windows\System32\drivers\etc\hosts`):

```text
127.0.0.1 auth.localhost
127.0.0.1 catalog.localhost
127.0.0.1 commerce.localhost
127.0.0.1 payments.localhost
127.0.0.1 directory.localhost
127.0.0.1 oms.localhost
127.0.0.1 fulfillment.localhost
127.0.0.1 inventory.localhost
127.0.0.1 wms.localhost
127.0.0.1 production.localhost
127.0.0.1 custom.localhost
127.0.0.1 procurement.localhost
127.0.0.1 counterparties.localhost
127.0.0.1 notification.localhost
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
| `directory.localhost` | `directory` | `directory` | `8000` |
| `oms.localhost` | `oms` | `oms` | `8000` |
| `fulfillment.localhost` | `fulfillment` | `fulfillment` | `8000` |
| `inventory.localhost` | `inventory` | `inventory` | `8000` |
| `wms.localhost` | `wms` | `wms` | `8000` |
| `production.localhost` | `production` | `production` | `8000` |
| `custom.localhost` | `custom` | `custom` | `8000` |
| `procurement.localhost` | `procurement` | `procurement` | `8000` |
| `counterparties.localhost` | `counterparties` | `counterparties` | `8000` |
| `notification.localhost` | `notification` | `notification` | `8000` |

Соответствующие labels в `docker-compose.local.yml` (сводка): для каждого сервиса — `traefik.enable=true`, `Host(\`<имя>.localhost\`)`, `entrypoints=web`, `loadbalancer.server.port=8000`.

Проверка OIDC: `http://auth.localhost:8080/.well-known/openid-configuration`.

OpenAPI (пример): `http://catalog.localhost:8080/api/openapi.json` (аналогично для других сервисов по их хосту).

**Directory:** эндпоинты **`/api/v1/me`**, **`/api/v1/me/addresses`**, **`/api/v1/me/consents`** ожидают **Bearer** access token от Auth; операционные **`GET /api/v1/customers`**, **`GET/PATCH /api/v1/customers/{id}`**, **`POST /api/v1/customers/{id}/merge`** — тот же Bearer, но в JWT в **`scope`** должен быть **`admin`**. В `docker/directory/config.dev.ini` секция **`[AUTH]`** (JWKS, `ISSUER`, `AUDIENCE`) согласована с **`docker/auth/config.dev.ini`**.

### Базы данных PostgreSQL

При **первом** создании тома Postgres скрипты в `docker/postgres/docker-entrypoint-initdb.d/` создают отдельные БД для сервисов (владелец `zhuchka`): `zhuchka_auth` (из образа/базового init), `zhuchka_catalog`, `zhuchka_commerce`, `zhuchka_payments`, `zhuchka_directory`, `zhuchka_oms`, `zhuchka_fulfillment`, `zhuchka_inventory`, `zhuchka_wms`, `zhuchka_production`, `zhuchka_custom`, `zhuchka_procurement`, `zhuchka_counterparties`, `zhuchka_notification`.

Если том **`zhuchka_pgdata` уже существовал** без нужной базы, создайте её вручную (пример для одной БД):

```bash
docker compose -f docker-compose.yml exec postgres psql -U zhuchka -d zhuchka_auth -c "CREATE DATABASE zhuchka_catalog OWNER zhuchka;"
```

Повторите `CREATE DATABASE …` для остальных имён при необходимости.

## Прямые порты (минуя Traefik)

Удобно для клиентов на хосте (IDE, CLI) и для отладки без Host-заголовка.

| Порт хоста | Сервис | Назначение |
|------------|--------|------------|
| `5432` | `postgres` | PostgreSQL |
| `6379` | `redis` | Redis |
| `9000` | `minio` | S3 API |
| `9001` | `minio` | веб-консоль MinIO |
| `8000` | `auth` | HTTP auth (оверлей) |
| `8001` | `catalog` | HTTP catalog |
| `8002` | `commerce` | HTTP commerce |
| `8003` | `payments` | HTTP payments |
| `8004` | `directory` | HTTP directory |
| `8005` | `oms` | HTTP oms |
| `8006` | `fulfillment` | HTTP fulfillment |
| `8007` | `inventory` | HTTP inventory |
| `8008` | `wms` | HTTP wms |
| `8009` | `production` | HTTP production |
| `8010` | `custom` | HTTP custom |
| `8011` | `procurement` | HTTP procurement |
| `8012` | `counterparties` | HTTP counterparties |
| `8013` | `notification` | HTTP notification |

Из других контейнеров в той же сети Compose имена хостов: `postgres`, `redis`, `minio`, и имена сервисов из оверлея (`auth`, `catalog`, …, `notification`).

## MinIO

Бакеты для медиа по умолчанию: **`keyboards`**, **`parts`** (создаётся одноразовым контейнером `minio-init`). Учётные данные администратора задаются в `docker-compose.yml` (`MINIO_ROOT_*`).

## Пример переменных окружения

Файл с плейсхолдерами (без реальных ключей): **[`docker/local.example.env`](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards/blob/dev/docker/local.example.env)** (в репозитории, вне каталога `docs/`). Имена переменных с префиксом `ZCH_LOCAL_*` не подхватываются Compose автоматически — это ориентир для приложений и скриптов на хосте.
