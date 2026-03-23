# Детальные требования к микросервисам

Здесь — **отдельный документ на каждый** из 14 бэкенд-сервисов: домен, данные, API, события, безопасность, наблюдаемость, приёмка.

**Сквозные правила** (HTTP, OAuth2, ошибки, пагинация, health, metrics) — в [`../microservices-api-requirements.md`](../microservices-api-requirements.md). Ниже — только дополнение к ним, не дублирование.

## Оглавление

| # | Сервис | Папка в репо | Документ |
|---|--------|----------------|----------|
| 1 | Auth | `services/auth` | [01-auth.md](01-auth.md) |
| 2 | Directory (customers) | `services/directory` | [02-directory.md](02-directory.md) |
| 3 | Catalog | `services/catalog` | [03-catalog.md](03-catalog.md) |
| 4 | Commerce | `services/commerce` | [04-commerce.md](04-commerce.md) |
| 5 | Payments | `services/payments` | [05-payments.md](05-payments.md) |
| 6 | OMS | `services/oms` | [06-oms.md](06-oms.md) |
| 7 | Fulfillment | `services/fulfillment` | [07-fulfillment.md](07-fulfillment.md) |
| 8 | Inventory | `services/inventory` | [08-inventory.md](08-inventory.md) |
| 9 | WMS | `services/wms` | [09-wms.md](09-wms.md) |
| 10 | Production | `services/production` | [10-production.md](10-production.md) |
| 11 | Custom | `services/custom` | [11-custom.md](11-custom.md) |
| 12 | Procurement | `services/procurement` | [12-procurement.md](12-procurement.md) |
| 13 | Counterparties | `services/counterparties` | [13-counterparties.md](13-counterparties.md) |
| 14 | Notification | `services/notification` | [14-notification.md](14-notification.md) |

## Локальные соглашения в этих документах

- **Префикс API** по умолчанию: `/api/v1` — в спеках сервиса может быть уточнён (например публичный read-only каталога без префикса за отдельным router-ом Traefik).
- **Идентификаторы**: UUID v7 или ULID для внешних ссылок; внутренние числовые id не экспонировать наружу без необходимости.
- **Etag / If-Match**: для `PATCH`/`PUT` на конкурентно редактируемых сущностях — при поддержке optimistic locking (где указано явно).
