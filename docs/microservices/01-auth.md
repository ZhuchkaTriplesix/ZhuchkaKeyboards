# Auth service (`services/auth`) — детальные требования

## 1. Назначение и границы

- **Единственный** владелец: учётные записи, пароли (хэш), OAuth2/OIDC Authorization Server, клиенты (confidential/public), refresh-токены, сессии (если используются), **JWKS**, роли и permissions (RBAC), опционально MFA, **аудит входов**.
- **Не входит**: бизнес-профиль покупателя (это `directory`), каталог, заказы.

## 2. Две аудитории входа (витрина vs операционка)

Политика продукта **жёстко разделяет** способы входа для **посетителя сайта** и для **сотрудника**.

### 2.1 Покупатель / пользователь витрины (публичный фронт)

- Должен иметь возможность войти **через Google** (аккаунт Gmail / Google OAuth / OIDC Google) и **через Telegram** (стандартный сценарий: [Telegram Login Widget](https://core.telegram.org/widgets/login) с проверкой подписи на бэкенде; при необходимости — OAuth-бот / deep link по политике безопасности).
- Реализация в `auth-service`: отдельный **OAuth client** для витрины (public, PKCE), **федерация** с Google OIDC как внешним IdP; для Telegram — эндпоинт приёма данных виджета, проверка `hash` с `bot_token`, создание/связывание пользователя и выдача **своих** access/refresh токенов платформы (единый `sub` в JWT для связи с `directory`).
- Самообслуживание «логин/пароль только наш» для покупателя — **опционально** (по продукту); если включено — тот же тип учётки **customer**, но без смешения с сотрудниками.

### 2.2 Сотрудник (операционный фронт / staff)

- Входит **только** по **учётной записи, выданной организацией**: учёт создаётся администратором (или HR-процесс / синхронизация с корпоративным каталогом), пароль задаётся/сбрасывается по регламенту; опционально **MFA** и в перспективе **SSO** (SAML/OIDC) к корпоративному IdP — но **не** через публичные кнопки «Google» / «Telegram» как у витрины.
- Отдельный **OAuth client** для операционки (confidential или public+PKCE по политике); grant types и redirect URI **не** пересекаются с витринным клиентом; в политике сервиса — **запрет** привязки staff-ролей к входу через Telegram/Google (проверка по `client_id` + типу учётки / флагу `identity_kind`).

### 2.3 Модель данных (уточнение)

- Учётная запись должна иметь признак **типа**: например `customer` | `staff` (или отдельные таблицы связей), плюс **`external_identities`**: провайдер (`google`, `telegram`), subject у провайдера, связь с внутренним `user_id`.
- **Сотрудник**: `identity_kind=staff`, провайдеры входа только `local` и при внедрении — `corporate_sso`; **покупатель**: `identity_kind=customer`, допустимы `google`, `telegram`, при необходимости `password`.

## 3. Владение данными (логическая модель)

| Сущность | Описание |
|----------|----------|
| `User` | Уникальный субъект (`sub`), **тип** (`customer` / `staff`), email/логин, статус (active/locked), MFA flags |
| `ExternalIdentity` | Связь `user_id` ↔ внешний провайдер (`google`, `telegram`, …) и `subject` у провайдера; только для **customer**, если вход через федерацию |
| `Credential` | Пароль/OTP/WebAuthn — только здесь; алгоритмы и политика сложности; для **staff** — основной способ входа; для **customer** — опционально |
| `OAuthClient` | client_id, тип (public/confidential), redirect_uris, grant_types; **отдельные клиенты** для витрины и для операционки |
| `Role`, `Permission` | Именованные роли; мелкозернистые permissions при необходимости |
| `UserRoleAssignment` | Связь user ↔ role ↔ scope (организация/склад — если ABAC-lite) |
| `RefreshToken` / `Session` | Хранение с отзывом и ротацией |
| `LoginAudit` | timestamp, user_id?, client_id, ip, user_agent, result, reason, **метод входа** (local / google / telegram / sso) |

## 4. OAuth2 / OIDC — обязательные эндпоинты

| Метод | Путь | Назначение |
|-------|------|------------|
| GET | `/.well-known/openid-configuration` | OIDC discovery |
| GET | `/.well-known/jwks.json` | Публичные ключи JWT |
| GET/POST | `/oauth/authorize` (или по спеке AS) | Authorization code flow |
| POST | `/oauth/token` | token, refresh_token, client_credentials |
| POST | `/oauth/revoke` | Отзыв refresh / access (если поддерживается) |
| GET | `/oauth/userinfo` | Claims пользователя для OIDC (если включено) |

Требования:

- Поддержка **Authorization Code + PKCE** для публичных клиентов (браузер).
- **client_credentials** для сервис-сервис с ограниченным набором scopes.
- **Refresh token rotation** — по политике безопасности; старый refresh инвалидировать при выдаче нового (рекомендуется).
- Дополнительно для витрины: **authorization code** после редиректа с **Google** (стандартный OIDC) и обработка **Telegram Login** (отдельный ресурсный эндпоинт, не смешивать с staff-клиентом).

## 5. Административное и внутреннее API (`/api/v1/...`)

Все под **Bearer** с ролью администратора платформы или отдельным **service account** с mTLS (политика деплоя).

| Ресурс | Операции | Примечание |
|--------|----------|------------|
| `/users` | POST, GET, PATCH, DELETE (soft) | Создание **в т.ч. staff** (выданный аккаунт), тип `staff`; покупателей часто создаёт поток Google/Telegram — отдельная политика |
| `/users/{id}/roles` | PUT (replace), POST | Назначение ролей |
| `/users/{id}/mfa` | POST, DELETE | Включение/сброс MFA |
| `/clients` | CRUD OAuth clients | Секреты — только при создании/ротации, дальше маска |
| `/roles`, `/permissions` | CRUD при необходимости | Версионирование при изменении матрицы прав |

**Интроспекция** (опционально, если не только JWKS):

- `POST /oauth/introspect` — для resource servers, которые не валидируют JWT локально.

## 6. Scopes (пример конвенции)

- `openid`, `profile`, `email` — базовые OIDC.
- `customer` — доступ к своему профилю в directory через BFF.
- `staff` — операционный контур (узкий набор).
- `inventory:read`, `inventory:write` — пример доменных scopes (согласовать единый реестр).

Каждый доменный сервис документирует **минимальный** набор scopes для своих эндпоинтов; Auth только **выдаёт** токены с этими scope.

## 7. Безопасность

- Пароли: **Argon2id** или **bcrypt** с work factor по политике; соль per-user.
- Rate limit на `/oauth/token`, `/oauth/authorize`, `/users/*/password-reset` — на Traefik + при необходимости в сервисе.
- **Блокировка** после N неудачных попыток; отражение в `LoginAudit`.
- Секреты клиентов — только в Vault/secret manager; не логировать.

## 8. События (исходящие)

| Событие | Когда | Ключевые поля |
|---------|--------|----------------|
| `auth.user.created` | Создан пользователь | `user_id`, `email_hash?` |
| `auth.user.locked` | Блокировка | `user_id`, `reason` |
| `auth.login.succeeded` | Успешный вход | `user_id`, `client_id`, `ip_hash` |
| `auth.login.failed` | Неуспех | `identifier_hash`, `reason` |

Consumer’ы: SIEM, `notification-service` (опционально алерты), аналитика.

## 9. Наблюдаемость

- Метрики: число выданных токенов, failed logins, latency token endpoint, invalid_grant rate.
- Логи: без PII в открытом виде; корреляция по `request_id`.

## 10. Доменные коды ошибок (примеры)

| `code` | HTTP | Смысл |
|--------|------|--------|
| `invalid_grant` | 400 | Неверный refresh / code |
| `invalid_client` | 401 | Клиент не аутентифицирован |
| `access_denied` | 403 | Policy / disabled user |
| `mfa_required` | 403 | Нужен второй фактор |

## 11. Критерии приёмки

- [ ] Discovery + JWKS работают; доменный сервис может валидировать JWT без вызова Auth на каждый запрос.
- [ ] PKCE обязателен для публичных клиентов.
- [ ] Аудит входов пишется для success/failure.
- [ ] OpenAPI для админ-API и для OAuth эндпоинтов (где применимо) опубликованы.
- [ ] Витрина: вход через **Google** и **Telegram** реализован и не даёт staff-scopes.
- [ ] Операционка: вход только **выданная** учётка (и при необходимости корпоративный SSO); **нет** входа staff через Google/Telegram как у покупателя.
