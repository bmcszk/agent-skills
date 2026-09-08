# Docker Compose Configuration
## 2. Docker Compose Configuration

### Base Structure (docker-compose.yml)

```yaml
# NO version field - deprecated in 2025+
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    restart: unless-stopped
    environment:
      - APP_ENV=production
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    networks:
      - backend
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  postgres:
    image: postgres:17-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-app}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-secret}
      POSTGRES_DB: ${POSTGRES_DB:-appdb}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-app}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

networks:
  backend:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

### Development Override (docker-compose.dev.yml)

```yaml
services:
  app:
    build:
      target: development
    volumes:
      - .:/app
      - go_mod_cache:/go/pkg/mod
    environment:
      - APP_ENV=development
      - LOG_LEVEL=debug
    ports:
      - "8080:8080"
      - "40000:40000"  # Delve debugger
    security_opt:
      - "seccomp:unconfined"
    cap_add:
      - SYS_PTRACE

  postgres:
    ports:
      - "5432:5432"

  redis:
    ports:
      - "6379:6379"

volumes:
  go_mod_cache:
```

### Migration Pattern (service_completed_successfully)

```yaml
# Run migrations before starting app - 2026 best practice
services:
  migrate:
    build: .
    command: go run ./cmd/migrate
    environment:
      - DATABASE_URL=postgres://app:secret@postgres:5432/appdb
    depends_on:
      postgres:
        condition: service_healthy

  app:
    depends_on:
      migrate:
        condition: service_completed_successfully  # Wait for exit code 0
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
```
  go_mod_cache:
```

---

