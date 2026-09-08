# Best Practices & Infrastructure as Code
## 4. Best Practices 2026

### Docker Compose Rules

1. **NO version field** - Deprecated since Compose v2
2. **ALWAYS define healthchecks** - Required for proper dependency management
3. **NEVER run as root** - Use `user: 1000:1000` or distroless
4. **Use .env files** - Never hardcode secrets
5. **Named volumes for persistence** - Anonymous volumes for temp data
6. **Bridge networks for isolation** - Custom networks per stack
7. **Resource limits** - Prevent runaway containers

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
```

### Multi-File Strategy (via justfile)

```just
# Define in justfile, NOT raw bash commands
compose_dev := "docker compose -f docker-compose.yml -f docker-compose.dev.yml"
compose_prod := "docker compose -f docker-compose.yml -f docker-compose.prod.yml"
compose_test := "docker compose -f docker-compose.test.yml"

dev-up:
    {{ compose_dev }} up -d

prod-up:
    {{ compose_prod }} up -d

test-e2e:
    {{ compose_test }} up --build --abort-on-container-exit

test-e2e-ci:
    docker compose -p ci-{{ env_var_or_default("BUILD_ID", "local") }} \
        -f docker-compose.test.yml up --build
```

### Healthcheck Reference (2026 Best Practices)

| Service | Test Command | Interval | Timeout | Retries | Start Period |
|---------|-------------|----------|---------|---------|--------------|
| PostgreSQL | `pg_isready -U user -d db` | 5s | 5s | 5 | 10s |
| MySQL | `mysqladmin ping -h localhost` | 5s | 5s | 5 | 30s |
| Redis | `redis-cli ping` | 5s | 3s | 5 | 5s |
| MongoDB | `mongosh --eval "db.adminCommand('ping')"` | 10s | 5s | 5 | 30s |
| HTTP API | `curl -f http://localhost/health` | 10s | 5s | 3 | 30s |
| RabbitMQ | `rabbitmq-diagnostics check_running` | 10s | 5s | 5 | 30s |

```yaml
# Healthcheck structure
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 10s      # Time between checks
  timeout: 5s        # Max time for check to complete
  retries: 3         # Failures before unhealthy
  start_period: 30s  # Grace period for startup
```

---

