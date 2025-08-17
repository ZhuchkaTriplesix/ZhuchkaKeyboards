# ZhuchkaKeyboards Monitoring Setup

This directory contains the complete monitoring stack for the ZhuchkaKeyboards application using Prometheus, Grafana, and Loki.

## 📊 Monitoring Stack Overview

### Components

1. **Prometheus** - Metrics collection and storage
2. **Grafana** - Visualization and dashboards  
3. **Loki** - Log aggregation and storage
4. **Promtail** - Log shipping agent
5. **Exporters** - Additional metrics collection:
   - PostgreSQL Exporter
   - Redis Exporter  
   - Node Exporter

## 🚀 Quick Start

### Start Monitoring Stack

```bash
# Start the main application first
make dev

# Start monitoring services
make monitoring
```

### Access URLs

- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin123`
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100

## 📈 Metrics Collected

### Application Metrics

- **HTTP Requests**: Total requests, response times, status codes
- **Database**: Query duration, connection count, errors
- **Redis**: Operations, connection pool size
- **Business Logic**: Orders, production tasks, quality checks
- **Errors**: Application errors by type and component
- **Cache**: Hit/miss ratios, operation counts

### Infrastructure Metrics

- **PostgreSQL**: Database performance, connections, queries
- **Redis**: Memory usage, operations, clients
- **System**: CPU, memory, disk, network (via Node Exporter)

## 🎯 Dashboards

### Pre-configured Dashboards

1. **ZhuchkaKeyboards Overview**
   - Application performance overview
   - HTTP metrics and error rates
   - Database and Redis performance
   - Business metrics (orders, production)

### Custom Dashboards

You can create additional dashboards in Grafana for:
- Detailed production monitoring
- Inventory management metrics  
- User activity analytics
- Quality control metrics

## 📝 Logging

### Log Sources

- **Application Logs**: FastAPI application logs
- **Database Logs**: PostgreSQL query logs
- **Docker Logs**: Container logs
- **System Logs**: System journal logs

### Log Structure

Application logs include:
- Request/response logging
- Database query logging
- Error tracking
- Business logic events

## ⚙️ Configuration

### Prometheus Configuration

Located in `prometheus/prometheus.yml`:
- Scrape intervals and targets
- Alert rules (if configured)
- Service discovery

### Grafana Configuration

Located in `grafana/provisioning/`:
- **Datasources**: `datasources/datasources.yml`
- **Dashboards**: `dashboards/dashboards.yml`
- **Dashboard JSON**: `dashboards/json/`

### Loki Configuration

Located in `loki/loki-config.yml`:
- Storage configuration
- Retention settings
- Query limits

## 🔧 Customization

### Adding New Metrics

1. **In Application Code**:
   ```python
   from services.metrics import prometheus_metrics
   
   # Record custom metric
   prometheus_metrics.record_custom_metric("metric_name", value)
   ```

2. **Add to Prometheus Config**:
   ```yaml
   scrape_configs:
     - job_name: 'your-service'
       static_configs:
         - targets: ['your-service:port']
   ```

3. **Create Grafana Dashboard**:
   - Add new panels with your metrics
   - Configure alerts if needed

### Adding Alerts

1. **Prometheus Alert Rules**:
   ```yaml
   groups:
     - name: zhuchka.rules
       rules:
         - alert: HighErrorRate
           expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.1
   ```

2. **Grafana Notifications**:
   - Configure notification channels
   - Add alert rules to dashboards

## 🔍 Troubleshooting

### Common Issues

1. **Metrics Not Showing**:
   - Check if Prometheus can reach your service
   - Verify metrics endpoint: `curl http://localhost:8001/metrics`
   - Check Prometheus targets: http://localhost:9090/targets

2. **Grafana Dashboard Issues**:
   - Verify datasource configuration
   - Check Prometheus query syntax
   - Ensure proper time range selection

3. **Logs Not Appearing**:
   - Check Promtail configuration
   - Verify Loki connectivity
   - Check log file permissions

### Health Checks

```bash
# Check all services
make health

# Check specific services
curl http://localhost:8001/api/health/deep
curl http://localhost:9090/-/healthy
curl http://localhost:3100/ready
```

## 📊 Performance Tuning

### Prometheus

- Adjust scrape intervals based on needs
- Configure retention policies
- Optimize query performance

### Grafana

- Use query caching
- Optimize dashboard queries
- Configure refresh intervals appropriately

### Loki

- Configure log retention
- Optimize log parsing
- Use structured logging

## 🛡️ Security

### Default Credentials

**⚠️ Change default passwords in production!**

```yaml
# In docker-compose.yaml
environment:
  - GF_SECURITY_ADMIN_PASSWORD=your-secure-password
```

### Network Security

- Use Docker networks for service isolation
- Configure firewalls for external access
- Use HTTPS in production

## 📚 Resources

### Documentation

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)

### Example Queries

```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status_code=~"5.."}[5m])

# 95th percentile response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Database query duration
rate(db_query_duration_seconds_sum[5m]) / rate(db_query_duration_seconds_count[5m])
```
