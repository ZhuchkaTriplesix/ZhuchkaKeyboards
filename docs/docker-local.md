# Локальный Docker-стек (корень монорепозитория)

Файлы в корне: **`docker-compose.yml`** (Postgres, Redis, MinIO, Traefik) и **`docker-compose.local.yml`** (оверлей: Python API из `services/*`, Flutter web **market** / **system** за Traefik и прямые порты для отладки).

Запуск из корня:

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

Compose подхватывает **`TELEGRAM_BOT_TOKEN`** и опционально **`TELEGRAM_BOT_USERNAME`** из файла **`.env`** в корне (шаблон — **`.env.example`**; `.env` в git не коммитится). Токен уходит в контейнер **auth** как переменная окружения и переопределяет пустое значение в `docker/auth/config.dev.ini`. Для витрины **`TELEGRAM_BOT_USERNAME`** также передаётся в `build.args` образа **market_web** (дефолт в оверлее — `ZhuchkaKeyboards_bot`). Для [Telegram Login](https://core.telegram.org/widgets/login) см. блок ниже — **`*.localhost` в @BotFather не принимаются**.

Сервис **`auth_bot`** (`bots/auth_bot`, long polling) в **`docker-compose.local.yml`** поднимается вместе с оверлеем: тот же **`TELEGRAM_BOT_TOKEN`**, конфиг **`docker/auth_bot/config.dev.ini`** (можно дописать **`admin_ids`**). Отдельного порта нет — бот ходит наружу к Telegram API.

**Telegram Login (витрина):** @BotFather для **`/setdomain`** **не принимает** имена вида **`market.localhost`** (ответ вроде *«The message should contain one domain name»*). Нужно доменное имя, которое Telegram считает допустимым.

Рекомендация для локальной разработки без туннеля: **`market.localtest.me`** — зона **localtest.me** резолвится в **127.0.0.1** (запись в `hosts` не нужна). В BotFather отправьте одной строкой: **`market.localtest.me`** (без `http://`). В браузере откройте **`http://market.localtest.me`** (порт **80**) или **`http://market.localtest.me:8080`**. В оверлее для **market_web** задан второй маршрут Traefik на этот хост.

**Важно:** запросы витрины к auth (в т.ч. `POST /oauth/federated/telegram` после Login Widget) идут на **`AUTH_BASE_URL`**, вшитый при сборке образа. Для сценария с **localtest.me** в оверлее задан маршрут **`auth.localtest.me`** на тот же сервис **auth**, а дефолтный **`MARKET_AUTH_BASE_URL`** — **`http://auth.localtest.me`** (без зависимости от `auth.localhost` в `hosts`). Если у вас Traefik доступен только на **8080**, в корневом **`.env`** задайте **`MARKET_AUTH_BASE_URL=http://auth.localtest.me:8080`** (и **`SYSTEM_AUTH_BASE_URL`** при необходимости) и пересоберите **market_web** / **system_web**.

Альтернатива: **ngrok**, **Cloudflare Tunnel** и т.п. — в BotFather укажите hostname туннеля (тоже одно имя, без схемы).

Обычная витрина без Telegram по-прежнему: **`market.localhost`** в `hosts` и **`http://market.localhost:8080`** (или порт 80).

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
127.0.0.1 market.localhost
127.0.0.1 system.localhost
```

## Traefik

- Образ и провайдер Docker заданы в `docker-compose.yml`. Используется **`traefik:v3.6`**: у **Docker Engine 29+** минимальная версия API **1.44**, а старые образы Traefik (например v3.0) ходили в API **1.24** — провайдер Docker не поднимался (в логах пустое `Error response from daemon`, все маршруты давали 404).
- Точка входа HTTP **`web`**: контейнер слушает **`:80`**, на хосте опубликовано **`8080`** и в оверлее **`docker-compose.local.yml`** дополнительно **`80`** (удобно открывать сайты без `:8080` в URL, в т.ч. **`http://market.localtest.me`** для Telegram Login).
- **`providers.docker.exposedbydefault=false`** — в маршруты попадают только сервисы с `traefik.enable=true`.
- Панель / API Traefik (режим `api.insecure`, только для разработки): хост **`8081`** → контейнер **`:8080`**.

### Маршруты HTTP (через Traefik)

| Хост (на порту хоста **`80`** или **`8080`**) | Router (имя в labels) | Сервис Compose | Порт контейнера бэкенда |
|------------------------------|------------------------|----------------|-------------------------|
| `auth.localhost` | `auth` | `auth` | `8000` |
| `auth.localtest.me` | `auth-localtest` | `auth` | `8000` |
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
| `market.localhost` | `market-web` | `market_web` | `80` (nginx → Flutter web) |
| `system.localhost` | `system-web` | `system_web` | `80` (nginx → Flutter web) |

Соответствующие labels в `docker-compose.local.yml` (сводка): для API — `traefik.enable=true`, `Host(\`<имя>.localhost\`)`, `entrypoints=web`, `loadbalancer.server.port=8000`; для витрины и system UI — порт контейнера **`80`** (статика из `flutter build web`).

### Flutter web в Docker

- **Market:** `frontend/market/docker/Dockerfile` — сборка `flutter build web --release`, nginx с `try_files` для `go_router`. В **`docker-compose.local.yml`** для **market_web** в `build.args` задан **`AUTH_BASE_URL`** по умолчанию **`http://auth.localtest.me`** (переопределение **`MARKET_AUTH_BASE_URL`** в `.env`), плюс **`http://catalog.localhost:8080`**, **`http://commerce.localhost:8080`**, **`OAUTH_CLIENT_ID`**, **`TELEGRAM_BOT_USERNAME`**. Витрина за Traefik: **http://market.localhost:8080** или **http://market.localhost** (нужен `hosts`). Для **Telegram Login** откройте **http://market.localtest.me** или **:8080** — см. блок про BotFather выше.
- **System:** **`API_BASE_URL`** по умолчанию **`http://auth.localtest.me`** (**`SYSTEM_AUTH_BASE_URL`** в `.env`); UI — **http://system.localhost** или **http://system.localhost:8080**.

Значения `--dart-define` вшиваются на этапе **сборки** образа. Сборка вне Compose по умолчанию использует `127.0.0.1` и прямые порты API (см. `ARG` в Dockerfile); для Traefik меняйте `build.args` в оверлее или передавайте `--build-arg` при `docker build`.

Проверка OIDC: `http://auth.localhost:8080/.well-known/openid-configuration`.

OpenAPI (пример): `http://catalog.localhost:8080/api/openapi.json` (аналогично для других сервисов по их хосту; у **directory** этот URL и Swagger защищены HTTP Basic — см. `services/directory/src/main.py`).

**Directory:** эндпоинты **`/api/v1/me`**, **`/api/v1/me/addresses`**, **`/api/v1/me/consents`**, **`/api/v1/me/b2b-links`** ожидают **Bearer** access token от Auth; операционные **`GET /api/v1/customers`** (в т.ч. фильтр **`counterparty_id`**), **`GET/PATCH /api/v1/customers/{id}`**, **`POST /api/v1/customers/{id}/merge`** — тот же Bearer, но в JWT в **`scope`** должен быть **`admin`**. В `docker/directory/config.dev.ini` секция **`[AUTH]`** (JWKS, `ISSUER`, `AUDIENCE`) согласована с **`docker/auth/config.dev.ini`**.

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
