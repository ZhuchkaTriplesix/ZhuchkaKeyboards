# Git submodules

Корень монорепозитория подключает сервисы, фронты и вспомогательные репозитории (например Telegram-бот) как **submodules** (URL — SSH `git@github.com:ZhuchkaTriplesix/...`).

## Python-микросервисы (`services/*`)

Бэкенды в `services/` основаны на [Reei-dp/fastapi-template](https://github.com/Reei-dp/fastapi-template): структура `src/`, Docker, Makefile, Alembic, Redis, health. **Не копируются** каталог `daemon-service/` (systemd) и `.github/workflows/` (CI/CD); в README и `DEPLOYMENT.md` соответствующие разделы убраны или сокращены.

## Карта путей

| Путь в репо | Удалённый репозиторий |
|-------------|------------------------|
| `services/auth` | [ZhuchkaKeyboards_auth](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_auth) |
| `services/directory` | [ZhuchkaKeyboards_directory](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_directory) |
| `services/catalog` | [ZhuchkaKeyboards_catalog](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_catalog) |
| `services/commerce` | [ZhuchkaKeyboards_commerce](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_commerce) |
| `services/payments` | [ZhuchkaKeyboards_payments](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_payments) |
| `services/oms` | [ZhuchkaKeyboards_oms](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_oms) |
| `services/fulfillment` | [ZhuchkaKeyboards_fullfilment](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_fullfilment) (имя репо с опечаткой *fullfilment*) |
| `services/inventory` | [ZhuchkaKeyboards_inventory](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_inventory) |
| `services/wms` | [ZhuchkaKeyboards_wms](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_wms) |
| `services/production` | [ZhuchkaKeyboards_production](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_production) |
| `services/custom` | [ZhuchkaKeyboards_custom](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_custom) |
| `services/procurement` | [ZhuchkaKeyboards_procurement](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_procurement) |
| `services/counterparties` | [ZhuchkaKeyboards_counterparties](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_counterparties) |
| `services/notification` | [ZhuchkaKeyboards_notification](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_notification) |
| `frontend/market` | [ZhuchkaKeyboards_frontend_market](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_frontend_market) |
| `frontend/system` | [ZhuchkaKeyboards_frontend_system](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_frontend_system) |
| `bots/auth_bot` | [ZhuchkaKeyboards_auth_bot](https://github.com/ZhuchkaTriplesix/ZhuchkaKeyboards_auth_bot) (ветка в `.gitmodules`: `dev`; каркас бота — [Reei-dp/aiogram-template](https://github.com/Reei-dp/aiogram-template)) |

**Auth и auth_bot:** workflow issue → ветка → тесты → PR в `dev` субмодуля описан в [git-workflow.md](git-workflow.md) (раздел «`services/auth` и `bots/auth_bot`»).

## Локальная инфраструктура (Docker в корне)

Корневой `docker-compose.yml` и оверлей для auth: таблица портов, маршруты Traefik к сервисам, пример переменных — в [docker-local.md](docker-local.md).

## OpenAPI и снимки API

Спецификации в субмодулях обычно доступны как `GET /api/openapi.json` (у отдельных сервисов, например directory, маршрут может требовать auth — см. README субмодуля). Периодическое обновление снимков в корне и порядок работы — в [openapi-sync.md](openapi-sync.md).

## Клонирование

```bash
git clone --recurse-submodules <url-этого-репо>
```

Уже клонировали без субмодулей:

```bash
git submodule update --init --recursive
```

Обновить все указатели на удалённые `master`:

```bash
git submodule update --remote --merge
```

*(Осторожно: `--remote` тянет последний коммит из ветки, заданной в submodule; по умолчанию часто `master`.)*

## Субмодуль в detached HEAD

После `git submodule update` каталог субмодуля часто указывает на **конкретный коммит**; внутри субмодуля `git status` показывает **detached HEAD** — это ожидаемо. Чтобы вести разработку в ветке:

```bash
cd services/<name>   # или bots/auth_bot, frontend/market, …
git checkout dev
git pull origin dev
```

## CI в монорепозитории

В корне действует workflow **CI (dev)** (`.github/workflows/ci-dev.yml`): матрица по Python-сервисам в `services/*`, отдельные задания для **Flutter** (`frontend/market`, `frontend/system`) и для **`bots/auth_bot`**. Подробности — в `.github/workflows/` (reusable-файлы рядом).
