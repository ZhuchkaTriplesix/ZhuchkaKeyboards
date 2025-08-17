# 🚀 Performance Testing Suite

Comprehensive performance testing suite for ZhuchkaKeyboards API with realistic data generation and RPS testing.

## 📊 Test Categories

### 🎯 RPS Tests (Requests Per Second)
- **`test_high_rps.py`** - High-load RPS tests targeting 1000+ RPS
- **`test_all_methods_rps.py`** - RPS tests for all API methods (GET, POST, PUT, DELETE)
- **`test_rps_benchmarks.py`** - Comprehensive benchmarks comparing different load scenarios

### 📈 Performance Analysis
- **`test_metrics_load.py`** - Tests metrics collection performance under load
- **`test_simple_rps.py`** - Basic RPS tests for debugging and validation
- **`test_realistic_load.py`** - Tests with realistic user behavior patterns

## 🏭 Test Data Generation

### Realistic Data Generators
- **`data_generators.py`** - Generates massive amounts of realistic keyboard manufacturing data
- **`load_test_data.py`** - Loads test data into the API for performance testing

### Dataset Sizes
- **Small**: 5 warehouses, 100 items, 200 inventory levels
- **Medium**: 20 warehouses, 2,000 items, 5,000 inventory levels  
- **Large**: 50 warehouses, 10,000 items, 50,000 inventory levels
- **Massive**: 100 warehouses, 50,000 items, 250,000 inventory levels

## 🎮 Quick Start

### 1. Start the API
```bash
make dev  # Starts postgres, redis, gateway
```

### 2. Generate Test Data Files
```bash
make generate-test-data
```

### 3. Load Test Data into API
```bash
# Small dataset for quick testing
make load-test-data-small

# Medium dataset for realistic testing
make load-test-data-medium

# Large dataset for stress testing
make load-test-data-large
```

### 4. Run Performance Tests
```bash
# All performance tests
make test-performance

# Specific RPS tests
make test-rps                    # High RPS tests
make test-all-methods-rps       # All API methods
make test-rps-benchmarks        # Comprehensive benchmarks
```

## 📊 Test Data Categories

### Warehouses
- **50 realistic locations** across Asia, USA, Europe, Australia
- **Strategic facility types**: Distribution centers, assembly plants, testing labs
- **Geographic distribution**: Shenzhen, Taipei, Seoul, Los Angeles, London, etc.
- **Operational details**: Capacity, security levels, climate control

### Items (Keyboard Components)
- **Switches**: Cherry, Gateron, Kailh (Red, Blue, Brown, etc.)
- **Keycaps**: ABS, PBT profiles (OEM, Cherry, SA, XDA)
- **PCBs**: 60%, 65%, 75%, TKL layouts with hot-swap, RGB
- **Cases**: Aluminum, plastic materials in various colors
- **Cables**: USB-C, coiled, aviator connectors
- **Tools**: Switch pullers, lube, films, springs

### Suppliers
- **200+ realistic suppliers** from major manufacturing regions
- **Certification tracking**: ISO, RoHS compliance
- **Payment terms**: Net 30, Net 15, COD, Prepayment
- **Quality ratings** and lead times

### Inventory Levels
- **Realistic stock patterns**: 10% low stock, 80% normal, 10% overstock
- **Warehouse locations**: Zone/row/shelf/bin tracking
- **ABC classification**: Fast/medium/slow velocity items
- **Reserved quantities** for pending orders

## ⚡ Performance Targets

### Current Baseline (Single Container)
- **Health endpoint**: ~68-718 RPS (20 concurrent connections)
- **GET operations**: 150-300 RPS target
- **POST operations**: 30-50 RPS target  
- **Mixed CRUD**: 100 RPS target
- **Analytics**: 50 RPS target

### Production Goals
- **GET operations**: 500+ RPS
- **POST operations**: 100+ RPS
- **Concurrent users**: 1000+
- **Response time**: <100ms P95

## 🔧 Test Architecture

### Async Performance Testing
- **aiohttp**: High-performance async HTTP client
- **Concurrent connections**: Configurable connection pools
- **Batch testing**: Parallel request processing
- **Real-time metrics**: Response times, success rates, throughput

### Load Simulation Patterns
- **Burst load**: Maximum requests as fast as possible
- **Sustained load**: Consistent RPS over time
- **Gradual ramp-up**: Finding breaking points
- **User simulation**: Realistic think times and patterns

## 📈 Metrics Collection

### Response Time Analysis
- **Average, Min, Max** response times
- **Median and P95** percentiles
- **Distribution analysis** across different endpoints

### Throughput Metrics
- **Actual RPS** achieved vs target
- **Success rate** percentage
- **Error distribution** by status code
- **Performance degradation** under load

### Resource Usage
- **Connection pool** utilization
- **Database performance** impact
- **Memory and CPU** usage patterns
- **Network throughput** analysis

## 🎯 Test Scenarios

### Empty Database Baseline
Tests API performance with minimal database load to establish baseline metrics.

### Loaded Database Performance
Tests with realistic amounts of data (thousands of items, hundreds of warehouses).

### Heavy Database Stress
Complex queries, large result sets, multiple filters, analytics operations.

### Mixed CRUD Operations
Realistic distribution: 70% GET, 20% POST, 8% PUT, 2% DELETE operations.

### Concurrent User Simulation
Multiple users with realistic behavior patterns and think times.

## 🚀 Optimization Recommendations

Based on performance test results, the following optimizations are recommended:

### Database Optimizations
- **Indexing**: Add indexes for search and filter operations
- **Connection pooling**: Optimize PostgreSQL connection limits
- **Query optimization**: Analyze slow queries with EXPLAIN

### Caching Strategy
- **Redis caching**: Cache frequently accessed read operations
- **Response caching**: Cache analytics and search results
- **Session caching**: Reduce database hits for user sessions

### Application Scaling
- **Uvicorn workers**: Multiple worker processes
- **Load balancing**: Nginx or cloud load balancer
- **Connection limits**: Fine-tune async connection pools

### Infrastructure
- **Database replicas**: Read replicas for analytics
- **CDN**: Static content delivery
- **Auto-scaling**: Container orchestration

## 📊 Sample Test Results

```bash
📊 Mixed CRUD Operations Results:
  Total requests: 1000
  Successful: 847
  Success rate: 84.70%
  Target RPS: 100
  Actual RPS: 76.12
  Test duration: 11.13s
  Avg response time: 145.23ms
  🟡 Performance: 76.1% (Good)
```

## 🔍 Debugging Performance Issues

### Common Issues
- **Connection timeouts**: Increase timeout values
- **Database locks**: Check for blocking queries
- **Memory leaks**: Monitor container memory usage
- **Slow queries**: Use database query analysis

### Monitoring
- **Prometheus metrics**: Built-in metrics collection
- **Grafana dashboards**: Real-time performance visualization
- **Application logs**: Detailed error tracking
- **Database monitoring**: Query performance analysis

## 🎉 Best Practices

### Test Data Management
- **Isolated environments**: Separate test databases
- **Data cleanup**: Reset between test runs
- **Realistic datasets**: Mirror production data patterns
- **Version control**: Track test data schemas

### Performance Testing
- **Baseline establishment**: Always start with empty database tests
- **Gradual load increase**: Find breaking points systematically
- **Multiple runs**: Average results across multiple test executions
- **Environment consistency**: Same hardware/network conditions

### Results Analysis
- **Trend tracking**: Monitor performance over time
- **Bottleneck identification**: Profile slow operations
- **Capacity planning**: Predict scaling requirements
- **Optimization validation**: Measure improvement impact