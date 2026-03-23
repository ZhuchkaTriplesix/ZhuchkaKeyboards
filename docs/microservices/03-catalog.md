# Catalog service (`services/catalog`) — детальные требования

## 1. Назначение и границы

- Владелец **каталога и PIM**: продукты, **варианты (SKU)**, атрибуты, категории, медиа (метаданные + URL), SEO-поля, **правила совместимости** (клавиатуры: layout, форм-фактор, PCB, стабы и т.д.).
- **Поиск** в контуре этого сервиса до выделения отдельного search-service: query API с фильтрами/facets.
- **Не владелец**: остатков, цен с наценкой в корзине (частично commerce), заказов.

## 2. Владение данными

| Сущность | Описание |
|----------|----------|
| `Product` | Логический товар, бренд, описание, статус (draft/published/archived) |
| `Variant` | SKU, атрибуты, штрихкод, вес/габариты для доставки |
| `AttributeDefinition` | Имя, тип (enum/number/string), единицы, локализация |
| `Category` | Дерево, slug, SEO |
| `MediaAsset` | Тип (image/video), url, alt, порядок, привязка к product/variant |
| `CompatibilityRule` | Условия вида «variant A совместим с B если …»; исполняемое представление (JSON/DSL) |
| `PriceList` / `BasePrice` (опционально) | Базовая публичная цена; промо — в Commerce |

Уточнение: если **цены только в Commerce**, Catalog отдаёт **list_price** как справочно или не отдаёт — единая политика.

## 3. API — чтение (витрина)

Префикс: `/api/v1` (или `/public/v1` за отдельным middleware).

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/products` | Список: фильтры category, brand, attributes, cursor |
| GET | `/products/{slugOrId}` | Детали + варианты |
| GET | `/variants/{id}` | Карточка SKU |
| GET | `/categories` | Дерево или плоский список с path |
| POST | `/compatibility/validate` | Тело: выбранные variant_id / атрибуты → допустимость + сообщения |
| GET | `/search` | q, facets, sort, cursor |

Кэширование: **ETag** / `Cache-Control` для GET; инвалидация при публикации.

## 4. API — запись (операционка)

| Метод | Путь | Описание |
|-------|------|----------|
| POST/PATCH/DELETE | `/products`, `/variants`, `/categories` | CRUD с ролями `catalog.editor` |
| POST | `/products/{id}/publish` | Переход в published + событие |
| POST | `/media` | Регистрация файла (presigned upload в object storage — отдельный flow) |
| CRUD | `/compatibility/rules` | Правила; тестовый прогон на наборах |

## 5. Совместимость (домен клавиатур)

- Отдельный **движок проверки**: вход — набор выбранных сущностей (варианты компонентов), выход — `ok | violations[]` с кодами (`incompatible_switch_plate`, `pcb_mount_mismatch`, …).
- Версионирование правил: при изменении — `rule_set_version` в ответе validate для привязки к черновику заказа.

## 6. События

| Событие | Когда |
|---------|--------|
| `catalog.product.published` | Публикация |
| `catalog.product.updated` | Любое изменение, влияющее на витрину |
| `catalog.compatibility.updated` | Изменение правил |

## 7. Зависимости

- **Object storage** (S3): бинарники изображений; Catalog хранит только URL и метаданные.
- Опционально **полнотекстовый индекс** (PostgreSQL FTS / OpenSearch) внутри сервиса.

## 8. Нефункциональные требования

- Чтение каталога — **высокий RPS**; горизонтальное масштабирование stateless.
- Запись — ниже RPS, строгий аудит «кто изменил карточку».

## 9. Критерии приёмки

- [ ] OpenAPI покрывает публичное чтение и админ-запись.
- [ ] `POST /compatibility/validate` документирован с примерами нарушений.
- [ ] События публикации для инвалидации кэша фронта/CDN.
