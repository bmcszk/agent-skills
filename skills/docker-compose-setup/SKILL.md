---
name: docker-compose-setup
description: Docker Compose project setup for Go applications with E2E testing isolation, multi-file strategies, and optional Podman/Kubernetes/DevOps support
license: MIT
metadata:
  audience: developers
  workflow: infrastructure
  category: containerization
  technologies: docker, docker-compose, podman, kubernetes, go
---

## What I do

Comprehensive Docker Compose setup for Go applications following 2026 best practices.

## Core Capabilities

1. **Docker Compose Project Setup** - Production-ready compose configurations
2. **E2E Testing Isolation** - Dual compose file strategy for isolated test environments
3. **Multi-Stage Dockerfiles** - Optimized Go application images
4. **Podman Support** - Docker-compatible alternative with rootless by default
5. **Kubernetes Ready** - Local development with Kind/Minikube
6. **DevOps Integration** - CI/CD pipelines and infrastructure as code

---


## References

Specialized topics are split into focused reference files:

- [Multi-Stage Dockerfile](references/dockerfile.md) — Production & development Dockerfiles, dependency caching, distroless runtime
- [Docker Compose](references/compose.md) — Base structure, dev override, migration pattern, healthchecks
- [E2E Testing & CI/CD](references/ci-cd.md) — Dual compose strategy, test runner, GitHub Actions, GitLab CI
- [Best Practices & IaC](references/iac.md) — Docker Compose rules, multi-file strategy, healthcheck reference
- [Podman](references/podman.md) — Compatibility, commands, quadlet systemd integration
- [Kubernetes](references/kubernetes.md) — Kind, Minikube, Skaffold configurations

## Critical Rules

### Justfile (MANDATORY)

1. ALL docker/compose commands MUST be in justfile
2. NEVER run raw docker compose commands
3. Use variables for compose file paths
4. Group related commands (dev-*, test-*, prod-*)

### Dockerfile

1. ALWAYS use multi-stage builds
2. ALWAYS use distroless or scratch for production
3. ALWAYS pin Go version
4. ALWAYS use build caches
5. NEVER run as root in production

### Docker Compose

1. NO version field (deprecated)
2. ALWAYS define healthchecks
3. ALWAYS use depends_on with condition
4. ALWAYS use named volumes for persistence
5. NEVER expose ports in production compose

### E2E Testing

1. ALWAYS use isolated compose file
2. ALWAYS use tmpfs for test databases
3. ALWAYS cleanup with down -v
4. ALWAYS use unique project names
5. NEVER share networks with dev

### Security

1. NEVER run containers as root
2. NEVER hardcode secrets
3. ALWAYS use .env files
4. ALWAYS scan images for vulnerabilities
5. ALWAYS pin image versions

---

## Justfile Commands (MANDATORY)

**ALL docker/compose commands MUST be in justfile, never raw bash:**

```just
# justfile

# Variables
docker := "docker"
compose := docker + " compose"
compose_test := compose + " -f docker-compose.test.yml"
compose_dev := compose + " -f docker-compose.yml -f docker-compose.dev.yml"
compose_prod := compose + " -f docker-compose.yml -f docker-compose.prod.yml"
project_name := "e2e-" + env_var_or_default("BUILD_ID", "local")

# Development
default: dev-up

dev-up:
    {{ compose_dev }} up -d

dev-logs:
    {{ compose_dev }} logs -f app

dev-down:
    {{ compose_dev }} down

dev-build:
    {{ compose_dev }} build

# E2E Testing
test-e2e-up:
    {{ compose_test }} up -d --build

test-e2e-run:
    go test -v -count=1 ./test/e2e/...

test-e2e-down:
    {{ compose_test }} down -v --remove-orphans

test-e2e: test-e2e-up test-e2e-run test-e2e-down

test-e2e-ci:
    {{ compose }} -p {{ project_name }} -f docker-compose.test.yml \
        up --build --abort-on-container-exit --exit-code-from app-test

test-e2e-cleanup:
    {{ compose }} -p {{ project_name }} -f docker-compose.test.yml \
        down -v --remove-orphans

# Production
prod-up:
    {{ compose_prod }} up -d

prod-down:
    {{ compose_prod }} down

prod-build:
    {{ compose_prod }} build

# Cleanup
clean:
    {{ compose }} down -v --remove-orphans --rmi local

clean-all:
    {{ compose }} down -v --remove-orphans --rmi local
    docker system prune -f

# Podman (alternative)
podman-up:
    podman compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Kubernetes
k8s-kind-create:
    kind create cluster --config kind-config.yaml

k8s-kind-load:
    kind load docker-image myapp:latest

k8s-deploy:
    kubectl apply -f k8s/

k8s-kind-delete:
    kind delete cluster
```

### Usage

```bash
# Development
just dev-up
just dev-logs
just dev-down

# E2E Testing
just test-e2e

# CI Pipeline
just test-e2e-ci

# Production
just prod-up

# Cleanup
just clean
```

---

## Forbidden

- NEVER run raw docker compose commands (use justfile)
- NEVER use version field in compose files
- NEVER run containers as root in production
- NEVER hardcode secrets in compose files
- NEVER skip healthchecks
- NEVER share test and dev networks
- NEVER forget cleanup in CI
- NEVER use :latest tag in production
