# E2E Testing Isolation
## 3. E2E Testing Isolation (Dual Compose Strategy)

### Test Compose (docker-compose.test.yml)

```yaml
# Isolated test environment - NO port conflicts with dev
services:
  app-test:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    environment:
      - APP_ENV=test
      - DATABASE_URL=postgres://test:test@postgres-test:5432/testdb
      - REDIS_URL=redis://redis-test:6379
    networks:
      - test-network
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8080/health"]
      interval: 5s
      timeout: 5s
      retries: 10
      start_period: 10s
    depends_on:
      postgres-test:
        condition: service_healthy
      redis-test:
        condition: service_healthy

  postgres-test:
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: testdb
    tmpfs:
      - /var/lib/postgresql/data  # RAM disk for faster tests
    # Aggressive PostgreSQL settings for testing (NOT for production!)
    command:
      - postgres
      - -c
      - fsync=off
      - -c
      - synchronous_commit=off
      - -c
      - full_page_writes=off
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test -d testdb"]
      interval: 2s
      timeout: 2s
      retries: 10
      start_period: 5s
    networks:
      - test-network

  redis-test:
    image: redis:7-alpine
    tmpfs:
      - /data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 2s
      timeout: 2s
      retries: 10
    networks:
      - test-network

networks:
  test-network:
    driver: bridge
    # Isolated network - no external access
```

### Test Runner Pattern (via justfile)

```just
# justfile - E2E testing commands
compose_test := "docker compose -f docker-compose.test.yml"
project_name := "e2e-" + env_var_or_default("BUILD_ID", "local")

test-e2e-up:
    {{ compose_test }} up -d --build

test-e2e-run:
    go test -v -count=1 ./test/e2e/...

test-e2e-down:
    {{ compose_test }} down -v --remove-orphans

test-e2e: test-e2e-up test-e2e-run test-e2e-down

# CI: Run tests with project isolation
test-e2e-ci:
    docker compose -p {{ project_name }} -f docker-compose.test.yml \
        up --build --abort-on-container-exit --exit-code-from app-test

test-e2e-cleanup:
    docker compose -p {{ project_name }} -f docker-compose.test.yml \
        down -v --remove-orphans
```

```bash
# Usage
just test-e2e        # Local development
just test-e2e-ci     # CI pipeline
just test-e2e-cleanup
```

### E2E Test Helper (Go)

```go
package e2e_test

import (
    "context"
    "testing"
    "time"
)

type DockerCompose struct {
    projectName string
    composeFile string
}

func NewTestEnvironment(t *testing.T) *DockerCompose {
    t.Helper()
    projectName := fmt.Sprintf("e2e-%s-%d", t.Name(), time.Now().UnixNano())
    
    // Start isolated environment
    exec.Command("docker", "compose", "-p", projectName,
        "-f", "docker-compose.test.yml",
        "up", "-d", "--build").Run()
    
    t.Cleanup(func() {
        // Cleanup on test end
        exec.Command("docker", "compose", "-p", projectName,
            "-f", "docker-compose.test.yml",
            "down", "-v", "--remove-orphans").Run()
    })
    
    return &DockerCompose{projectName: projectName}
}
```

---


---

# DevOps Integration
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: extractions/setup-just@v2
      
      - name: Run E2E Tests
        env:
          BUILD_ID: ${{ github.run_id }}
        run: just test-e2e-ci
      
      - name: Cleanup
        if: always()
        env:
          BUILD_ID: ${{ github.run_id }}
        run: just test-e2e-cleanup
```

### GitLab CI

```yaml
# .gitlab-ci.yml
e2e-tests:
  stage: test
  image: golang:1.24
  before_script:
    - apt-get update && apt-get install -y just docker-compose
  script:
    - BUILD_ID=$CI_PIPELINE_ID just test-e2e-ci
  after_script:
    - BUILD_ID=$CI_PIPELINE_ID just test-e2e-cleanup
```

---

## 8. Project Structure

```
project/
├── justfile                   # All docker/compose commands
├── Dockerfile                 # Multi-stage production
├── Dockerfile.dev            # Development with hot reload
├── docker-compose.yml        # Base services
├── docker-compose.dev.yml    # Dev overrides
├── docker-compose.test.yml   # Isolated E2E testing
├── docker-compose.prod.yml   # Production overrides
├── .env.example              # Environment template
├── .dockerignore             # Build context exclusions
├── k8s/                      # Kubernetes manifests
│   ├── base/
│   └── overlays/
├── kind-config.yaml          # Kind cluster config
└── skaffold.yaml             # Dev workflow
```

---

