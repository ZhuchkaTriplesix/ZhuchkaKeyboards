# Commerce service (`services/commerce`) — детальные требования

## 1. Назначение и границы

- Владелец **корзины**, **чекаут-расчёта**, **промо/купонов** (пока не вынесены), **создания черновика заказа** и передачи в **OMS** после успешной валидации и оплаты (последовательность согласовать: часто «создать заказ в OMS в статусе pending_payment» → Payments → OMS paid).
- **Не владелец**: долгосрочного жизненного цикла заказа (OMS), складских остатков (Inventory), платёжных транзакций (Payments).

## 2. Владение данными

| Сущность | Описание |
|----------|----------|
| `Cart` | anonymous_id и/или `customer_id`, валюта, ttl |
| `CartLine` | variant_id, quantity, unit_price_snapshot, custom_spec_id? |
| `Promotion` | Правила применения, период, стеки с другими промо |
| `Coupon` | Код, лимиты использования |
| `CheckoutSession` | Состояние чекаута, выбранный адрес, доставка, итоги |

## 3. API — корзина

Префикс `/api/v1`.

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/carts` | Создать (guest или пользователь) |
| GET | `/carts/{id}` | Состав |
| POST | `/carts/{id}/lines` | Добавить позицию (проверка цены/наличия — синхронный вызов Catalog/Inventory или кэш) |
| PATCH | `/carts/{id}/lines/{lineId}` | Количество |
| DELETE | `/carts/{id}/lines/{lineId}` | Удалить |
| POST | `/carts/{id}/merge` | Слияние guest → user при логине |

**Идемпотентность:** `POST` добавления строки — опционально по `Idempotency-Key` для защиты от двойного клика.

## 4. API — промо

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/carts/{id}/coupons` | Применить код |
| DELETE | `/carts/{id}/coupons/{code}` | Снять |

## 5. API — checkout

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/carts/{id}/checkout/preview` | Расчёт налогов/доставки/итого без побочных эффектов |
| POST | `/carts/{id}/checkout` | Создать **заказ** + платёжное намерение; **обязательно** `Idempotency-Key` |

Тело `checkout` типично включает:

- `shipping_address_id` или embedded address snapshot
- `billing_address_id`
- `delivery_option_id`
- `customer_note`
- ссылка на **custom specification** если есть

Ответ:

- `order_id` (OMS)
- `payment_intent_id` (Payments) или redirect URL
- суммы разбивкой

## 6. Интеграции (синхронные)

- **Catalog**: актуальные цены, публикация SKU, validate compatibility для кастомных сборок.
- **Inventory**: доступное количество (read); резерв может делаться Commerce или OMS — **одна политика** на платформу.
- **Directory**: адреса для `/me` checkout.
- **Custom**: валидация и snapshot BOM/цены для кастомной линии.
- **OMS**: создание заказа.
- **Payments**: создание PaymentIntent после создания заказа (порядок строго документировать).

## 7. События

| Событие | Когда |
|---------|--------|
| `commerce.checkout.started` | Начало checkout (аналитика) |
| `commerce.order.submitted` | Заказ создан в OMS |

## 8. Ошибки домена

| `code` | Смысл |
|--------|--------|
| `variant_unavailable` | Нет в наличии / снят с публикации |
| `coupon_not_applicable` | Промо не подходит |
| `compatibility_failed` | От Catalog validate |
| `checkout_idempotency_replay` | Повтор того же ключа — вернуть тот же результат |

## 9. Критерии приёмки

- [ ] Checkout идемпотентен; повтор не создаёт второй заказ.
- [ ] Цены в корзине снапшотятся на линии; изменение каталога не ломает уже открытую корзину без пересчёта.
- [ ] OpenAPI описывает полную цепочку preview → checkout.
