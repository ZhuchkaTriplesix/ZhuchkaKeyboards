# Локальный Docker-стек (корень монорепозитория)

Файлы в корне: **`docker-compose.yml`** (Postgres, Redis, MinIO, Traefik) и **`docker-compose.local.yml`** (оверлей: сервис **auth** за Traefik и прямой порт для отладки).

Запуск из корня:

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

## Hosts

Для маршрута Traefik к auth добавьте в `hosts` (Windows: `C:\Windows\System32\drivers\etc\hosts`):

```text
127.0.0.1 auth.localhost
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

Соответствующие labels в `docker-compose.local.yml` (сводка):

- `traefik.enable=true`
- `traefik.http.routers.auth.rule=Host(\`auth.localhost\`)`
- `traefik.http.routers.auth.entrypoints=web`
- `traefik.http.services.auth.loadbalancer.server.port=8000`

Проверка OIDC: `http://auth.localhost:8080/.well-known/openid-configuration`.

Остальные сервисы стека пока **не** публикуются через Traefik; при появлении новых сервисов с labels таблицу следует дополнить.

## Прямые порты (минуя Traefik)

Удобно для клиентов на хосте (IDE, CLI) и для отладки без Host-заголовка.

| Порт хоста | Сервис | Назначение |
|------------|--------|------------|
| `5432` | `postgres` | PostgreSQL |
| `6379` | `redis` | Redis |
| `9000` | `minio` | S3 API |
| `9001` | `minio` | веб-консоль MinIO |
| `8000` | `auth` | HTTP auth (оверлей; тот же сервис, что за Traefik) |

Из других контейнеров в той же сети Compose имена хостов: `postgres`, `redis`, `minio`, `auth` (см. `docker-compose.yml` / оверлей).

## MinIO

Бакеты для медиа по умолчанию: **`keyboards`**, **`parts`** (создаётся одноразовым контейнером `minio-init`). Учётные данные администратора задаются в `docker-compose.yml` (`MINIO_ROOT_*`).
