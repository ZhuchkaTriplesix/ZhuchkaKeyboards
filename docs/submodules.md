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
