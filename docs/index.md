# Документация ZhuchkaKeyboards

Монорепозиторий: субмодули сервисов, Docker Compose для локальной инфраструктуры, обзорные материалы в каталоге `docs/`.

## Быстрые ссылки

| Тема | Документ |
|------|----------|
| Ветки, PR, субмодули | [git-workflow.md](git-workflow.md) |
| Список субмодулей | [submodules.md](submodules.md) |
| Docker, Traefik, MinIO (локально) | [docker-local.md](docker-local.md) |
| OpenAPI и снимки API | [openapi-sync.md](openapi-sync.md) |
| Требования к HTTP/API | [microservices-api-requirements.md](microservices-api-requirements.md) |
| Описание микросервисов | [microservices/README.md](microservices/README.md) |

Полный список страниц — в навигации слева и через поиск (иконка в шапке).

## Сборка сайта

Из корня репозитория:

```bash
pip install -r requirements-docs.txt
mkdocs serve   # предпросмотр на http://127.0.0.1:8000
# mkdocs build  # статика в ./site (каталог в .gitignore)
```
