---
layout: post
title: "Prometheus + Grafana: Monitoring Your App from Scratch"
date: "2026-05-23 00:00:00 +0530"
slug: prometheus-grafana-monitoring-guide
description: "Set up Prometheus and Grafana to collect, store, and visualize metrics for your application, with alerting rules and a working Docker Compose stack."
categories: ["Tutorials", "Programming"]
tags: ["prometheus", "grafana", "monitoring", "observability", "devops", "metrics", "alerting", "kubernetes", "dashboard"]
---

Flying blind in production — no metrics, no dashboards, no alerts — means you find out about problems when users report them. Prometheus and Grafana fix this. Prometheus scrapes and stores time-series metrics; Grafana turns those metrics into dashboards you can actually read. Together they're the de facto open-source monitoring stack for everything from a single server to a Kubernetes cluster.

## How Prometheus Works

Prometheus **pulls** metrics by making HTTP requests to `/metrics` endpoints on your services at a configured interval. Each service exposes metrics in a plain-text format:

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 1523
http_requests_total{method="POST",status="201"} 47
http_requests_total{method="GET",status="500"} 3
```

Prometheus stores these as time-series data and lets you query them with **PromQL**.

## Local Stack with Docker Compose

Create a `monitoring/` directory with this layout:

```
monitoring/
├── docker-compose.yml
├── prometheus/
│   └── prometheus.yml
└── grafana/
    └── datasources.yml
```

**`docker-compose.yml`**:

```yaml
services:
  prometheus:
    image: prom/prometheus:v2.53.0
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - promdata:/prometheus
    ports:
      - "9090:9090"
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.retention.time=15d"

  grafana:
    image: grafana/grafana:11.0.0
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafdata:/var/lib/grafana
      - ./grafana/datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml

  node-exporter:
    image: prom/node-exporter:v1.8.0
    pid: host
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - "--path.procfs=/host/proc"
      - "--path.sysfs=/host/sys"

volumes:
  promdata:
  grafdata:
```

**`prometheus/prometheus.yml`**:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "node"
    static_configs:
      - targets: ["node-exporter:9100"]

  - job_name: "myapp"
    static_configs:
      - targets: ["host.docker.internal:8000"]
    metrics_path: /metrics
```

**`grafana/datasources.yml`**:

```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true
```

Start it up:

```bash
$ docker compose up -d
$ open http://localhost:9090   # Prometheus UI
$ open http://localhost:3000   # Grafana (admin / admin)
```

## Instrumenting Your Application

**Python (with `prometheus_client`):**

```python
from prometheus_client import Counter, Histogram, start_http_server
import time

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["endpoint"]
)

# in your request handler:
def handle_request(method, endpoint):
    start = time.time()
    try:
        result = process(method, endpoint)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status="200").inc()
        return result
    except Exception:
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status="500").inc()
        raise
    finally:
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(time.time() - start)

# expose /metrics on port 8001
start_http_server(8001)
```

## Writing PromQL Queries

PromQL is the query language for Prometheus. A few essential patterns:

```promql
# request rate over the last 5 minutes
rate(http_requests_total[5m])

# error rate as a percentage
rate(http_requests_total{status=~"5.."}[5m])
  /
rate(http_requests_total[5m])
* 100

# 99th percentile latency
histogram_quantile(0.99,
  rate(http_request_duration_seconds_bucket[5m])
)

# CPU usage per core
100 - (avg by(cpu) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

## Setting Up Alerts

Add an `alerting_rules.yml` file and reference it in `prometheus.yml`:

```yaml
# prometheus/alerting_rules.yml
groups:
  - name: app_alerts
    rules:
      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status=~"5.."}[5m])
            /
          rate(http_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.job }}"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P99 latency above 1s"
```

```yaml
# in prometheus.yml, add:
rule_files:
  - "alerting_rules.yml"
```

## Grafana Dashboards

In Grafana, go to **Dashboards → New → Import** and use dashboard ID **1860** (Node Exporter Full) — a community dashboard with dozens of pre-built panels for CPU, memory, disk, and network.

For your application metrics, create a new dashboard and add panels with the PromQL queries above. Set the panel type to **Time series** for rates and latencies, **Stat** for current values, and **Gauge** for percentages.

## Conclusion

Prometheus's pull model makes it trivial to add new services to monitoring — just expose a `/metrics` endpoint and add a scrape target. PromQL is worth spending an hour learning; once you can write `rate()` and `histogram_quantile()` queries, you can answer almost any question about your system. Grafana turns those queries into dashboards that give you and your team at-a-glance health visibility, and alert rules mean you get paged before users notice something is wrong.
