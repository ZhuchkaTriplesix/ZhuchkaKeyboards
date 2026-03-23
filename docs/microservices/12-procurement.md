# Procurement service (`services/procurement`) — детальные требования

## 1. Назначение и границы

- Владелец **закупочного цикла**: заявки (requisition), **заказы поставщику (PO)**, **ожидаемые поставки**, трекинг входящих отправок, **приёмка (GRN)** и согласование количеств с **Inventory**.
- **Не владелец**: справочником поставщика как юрлица (ссылка на **Counterparties**), финальной бухгалтерской проводкой (вне scope или интеграция ERP).

## 2. Владение данными

| Сущность | Описание |
|----------|----------|
| `Requisition` | Внутренний запрос на закупку, линии, обоснование |
| `PurchaseOrder` | Номер, counterparty_id (поставщик), условия, строки, статус |
| `InboundShipment` | Связь с PO, перевозчик, трек, ETA |
| `GoodsReceipt` | Факт приёма по строкам: qty принято, брак, расхождения |
| `InvoiceMatch` | (Опционально) сверка счёта поставщика с PO/GRN |

## 3. API

Префикс `/api/v1`.

| Метод | Путь | Описание |
|-------|------|----------|
| CRUD | `/requisitions` | Согласование внутри компании |
| POST | `/purchase-orders` | Создать PO из req или напрямую |
| GET | `/purchase-orders` | Список, фильтры |
| GET | `/purchase-orders/{id}` | Детали |
| PATCH | `/purchase-orders/{id}/send` | Отправка поставщику (EDI/email/API) |
| POST | `/inbound-shipments` | Ожидаемая поставка |
| PATCH | `/inbound-shipments/{id}/tracking` | Обновление трека |
| POST | `/goods-receipts` | Приёмка на склад; **Idempotency-Key** |
| GET | `/goods-receipts/{id}` | |

## 4. Интеграции

- **Counterparties**: валидация `counterparty_id` с ролью supplier.
- **WMS**: ожидаемое поступление для inbound задачи.
- **Inventory**: при подтверждении GRN — приход qty (событие или синхронный вызов с компенсацией при ошибке).

## 5. События

| Событие | Когда |
|---------|--------|
| `procurement.po.sent` | |
| `procurement.inbound.updated` | Трек/ETA |
| `procurement.goods.received` | Для Inventory и уведомлений |

## 6. Доменные ошибки

| `code` | Смысл |
|--------|--------|
| `po_not_modifiable` | После send |
| `grn_qty_exceeds_po` | Превышение по строке без override роли |
| `supplier_inactive` | |

## 7. Критерии приёмки

- [ ] Двойная приёмка одной строки исключена idempotency.
- [ ] PO версионируется или имеет audit trail изменений после send только через контролируемые действия.
- [ ] Связь PO → inbound → GRN прослеживается для аудита.
