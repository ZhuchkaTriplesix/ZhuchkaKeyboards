# Git submodules

Корень монорепозитория подключает сервисы и фронты как **submodules** (URL — SSH `git@github.com:ZhuchkaTriplesix/...`).

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
