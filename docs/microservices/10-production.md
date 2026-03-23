# Production service (`services/production`) — детальные требования

## 1. Назначение и границы

- Владелец **производственных заказов** (work orders): маршруты, этапы, **BOM** на сборку, загрузка линии/ячеек, **ОТК**, брак, связь с **sales order** / **custom**.
- **Не владелец**: складскими количествами (Inventory списывает по событиям), **долгосрочным** OMS-статусом (кроме производственных подстатусов).

## 2. Владение данными

| Сущность | Описание |
|----------|----------|
| `WorkOrder` | id, `order_id` или `custom_spec_id`, приоритет, статус |
| `Routing` | Последовательность операций (сборка, луб, тест, упаковка) |
| `Operation` | Статус, исполнитель, started_at, completed_at |
| `ComponentConsumption` | sku_id, planned_qty, actual_qty |
| `ScrapRecord` | Причина, qty, rework? |
| `QualityCheck` | Результат теста, серийники |

## 3. API

Префикс `/api/v1`.

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/work-orders` | Создать из OMS/Custom |
| GET | `/work-orders` | Фильтры: статус, дата, order_id |
| GET | `/work-orders/{id}` | Детали + операции |
| PATCH | `/work-orders/{id}/status` | Переход (планирование → в работе → завершён) |
| POST | `/work-orders/{id}/operations/{opId}/start` | |
| POST | `/work-orders/{id}/operations/{opId}/complete` | С фактом списания компонентов |
| POST | `/work-orders/{id}/scrap` | Учёт брака |
| POST | `/work-orders/{id}/qc` | Запись ОТК |

## 4. Интеграции

- **Custom**: финальная BOM и допуски.
- **Inventory**: резерв/списание компонентов по этапам; возврат при браке — отдельные движения.
- **OMS**: обновление ETA (событие `production.milestone`).

## 5. События

| Событие | Когда |
|---------|--------|
| `production.work_order.released` | В работу |
| `production.operation.completed` | Этап |
| `production.scrap.recorded` | Брак |
| `production.completed` | Готовность к отгрузке |

## 6. Критерии приёмки

- [ ] Списание компонентов согласовано с Inventory (нет двойного списания).
- [ ] История этапов полная для гарантийных кейсов.
- [ ] Связь с заказом клиента не теряется при partial shipment.
