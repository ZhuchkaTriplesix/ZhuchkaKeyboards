# OMS service (`services/oms`) — детальные требования

## 1. Назначение и границы

- Владелец **заказа продажи** (sales order): строки, цены **снимком**, статусы жизненного цикла для клиента и производства, связи с **оплатой**, **отгрузкой**, **кастомом**.
- **Единый** внешний номер заказа (human-readable + внутренний id).
- **Не владелец**: списанием со склада (Inventory), задачами WMS, трекингом перевозчика (Fulfillment) — только координация через API/события.

## 2. Владение данными

| Сущность | Описание |
|----------|----------|
| `SalesOrder` | Номер, customer_id, валюта, статус, created_at, канал продаж |
| `OrderLine` | variant_id, name_snapshot, qty, unit_price, tax, custom_line_ref? |
| `OrderPaymentLink` | payment_intent_id, статус оплаты агрегированный |
| `OrderStatusHistory` | from → to, actor (user/system), reason |
| `OrderHold` | Блокировка (fraud, возврат) |

Статусы (пример, уточнять под процесс):

`draft` → `pending_payment` → `paid` → `processing` → `fulfillment` → `shipped` → `delivered` / `cancelled` / `returned`.

## 3. API

Префикс `/api/v1`.

### Клиент (по токену владельца заказа)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/orders` | Список заказов текущего клиента |
| GET | `/orders/{id}` | Детали + строки + публичные статусы |
| POST | `/orders/{id}/cancel` | Отмена по правилам (до отгрузки) |

### Операционка

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/orders` | Фильтры: статус, дата, номер, customer_id |
| GET | `/orders/{id}` | Полная карточка |
| PATCH | `/orders/{id}/status` | Переход с reason (RBAC) |
| POST | `/orders` | Создание из Commerce (внутренний или с service token) |
| POST | `/orders/{id}/notes` | Внутренние заметки |

### Сервис-сервис

- `POST /internal/orders` — создание заказа от Commerce (mTLS или client_credentials).
- `PATCH /internal/orders/{id}/payment-state` — от Payments worker (или только через события — предпочтительно события).

## 4. События

### Исходящие

| Событие | Когда |
|---------|--------|
| `oms.order.created` | Заказ создан |
| `oms.order.paid` | Оплата подтверждена |
| `oms.order.cancelled` | Отмена |
| `oms.order.status_changed` | Любой переход |

### Входящие (подписка)

- `payments.capture.succeeded` → перевод в `paid`, триггер Fulfillment/Inventory.
- `commerce.order.submitted` — если используется двухфазная модель.

## 5. Согласованность

- Создание заказа и строк — **одна транзакция** в БД OMS.
- Связь с оплатой: **идемпотентная** обработка события оплаты (по `payment_intent_id` + `order_id`).

## 6. Критерии приёмки

- [ ] Снимок цен и названий на строках не перезаписывается при изменении каталога.
- [ ] История статусов полная для разбора инцидентов.
- [ ] Клиент видит только разрешённые поля; внутренние поля — только staff.
