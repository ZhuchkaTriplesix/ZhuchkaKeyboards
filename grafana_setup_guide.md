# 📊 Инструкция по настройке Grafana для ZhuchkaKeyboards

## 🚀 Быстрый запуск

### 1. Откройте Grafana
- URL: http://localhost:3000
- Login: `admin`
- Password: `admin`

### 2. Проверьте Data Source
1. Перейдите в **Configuration** → **Data Sources**
2. Убедитесь, что Prometheus настроен:
   - Name: `Prometheus`
   - URL: `http://prometheus:9090`
   - Status: ✅ Green

### 3. Найдите наш дашборд
1. Перейдите в **Dashboards** → **Browse**
2. Найдите: **"ZhuchkaKeyboards Gateway Dashboard"**
3. Откройте дашборд

## 🔍 Альтернативный способ - ручное создание дашборда

Если автоматический дашборд не загрузился, создайте вручную:

### Шаг 1: Создать новый дашборд
1. **Dashboards** → **New** → **New Dashboard**
2. **Add visualization**

### Шаг 2: Добавить панели с правильными запросами

#### 📈 Panel 1: HTTP Request Rate
- **Query**: `rate(gateway_http_requests_total[5m])`
- **Legend**: `{{method}} {{endpoint}} ({{status_code}})`
- **Unit**: `reqps` (requests per second)

#### ⏱️ Panel 2: Response Time Percentiles  
- **Query A**: `histogram_quantile(0.95, rate(gateway_http_request_duration_seconds_bucket[5m]))`
- **Query B**: `histogram_quantile(0.50, rate(gateway_http_request_duration_seconds_bucket[5m]))`
- **Unit**: `s` (seconds)

#### 📊 Panel 3: Total Requests (Stat)
- **Query**: `sum(gateway_http_requests_total)`
- **Visualization**: Stat

#### 🥧 Panel 4: Requests by Endpoint (Pie Chart)
- **Query**: `sum by (endpoint) (gateway_http_requests_total)`
- **Visualization**: Pie chart

#### 📋 Panel 5: Status Codes
- **Query**: `sum by (status_code) (rate(gateway_http_requests_total[5m]))`
- **Legend**: `Status {{status_code}}`

## 🔧 Важные метрики для мониторинга

### Наши кастомные метрики middleware:
```promql
# Количество запросов
gateway_http_requests_total

# Время отклика (histogram)
gateway_http_request_duration_seconds_bucket
gateway_http_request_duration_seconds_count
gateway_http_request_duration_seconds_sum

# Rate запросов (RPS)
rate(gateway_http_requests_total[5m])

# Средний response time
rate(gateway_http_request_duration_seconds_sum[5m]) / rate(gateway_http_request_duration_seconds_count[5m])

# 95-й процентиль времени отклика
histogram_quantile(0.95, rate(gateway_http_request_duration_seconds_bucket[5m]))
```

### Системные метрики (от exporters):
```promql
# CPU использование
rate(node_cpu_seconds_total[5m])

# Память
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes

# PostgreSQL соединения
pg_stat_activity_count

# Redis memory
redis_memory_used_bytes
```

## 🎯 Рекомендованные алерты

### Создайте алерты для:
1. **High Response Time**: `avg(rate(gateway_http_request_duration_seconds_sum[5m])) > 0.5`
2. **High Error Rate**: `rate(gateway_http_requests_total{status_code=~"5.."}[5m]) > 0.1`
3. **Low Request Rate**: `rate(gateway_http_requests_total[5m]) < 0.1` (система неактивна)

## 📱 Настройка уведомлений

1. **Alerting** → **Notification channels**
2. Добавьте Slack, Email или Webhook
3. Привяжите к алертам

## 🔄 Обновление дашбордов

Файлы дашбордов находятся в:
```
monitoring/grafana/provisioning/dashboards/json/
```

После изменений:
```bash
docker-compose restart grafana
```

## 🌟 Полезные ссылки

- **Grafana UI**: http://localhost:3000
- **Prometheus UI**: http://localhost:9090  
- **API Metrics**: http://localhost:8001/metrics
- **API Docs**: http://localhost:8001/api/docs

---

**Готово!** Теперь вы можете мониторить производительность API в реальном времени! 🎉
