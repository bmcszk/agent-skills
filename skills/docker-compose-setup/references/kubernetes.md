# Kubernetes Local Development
## 6. Kubernetes Local Development

### Kind (Recommended for CI)

```yaml
# kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
    extraPortMappings:
      - containerPort: 30000
        hostPort: 8080
```

```just
# justfile - Kubernetes commands
k8s-kind-create:
    kind create cluster --config kind-config.yaml

k8s-kind-load:
    kind load docker-image myapp:latest

k8s-deploy:
    kubectl apply -f k8s/

k8s-kind-delete:
    kind delete cluster
```

```bash
# Usage
just k8s-kind-create
just k8s-kind-load
just k8s-deploy
```

### Minikube (Recommended for Dev)

```just
# justfile - Minikube commands
minikube-start:
    minikube start --driver=docker --cpus=4 --memory=8192

minikube-addons:
    minikube addons enable ingress
    minikube addons enable metrics-server

minikube-build:
    eval $(minikube docker-env) && docker build -t myapp:latest .
```

### Skaffold (Development Workflow)

```yaml
# skaffold.yaml
apiVersion: skaffold/v4beta9
kind: Config
build:
  artifacts:
    - image: myapp
      docker:
        dockerfile: Dockerfile
deploy:
  kubectl: {}
```

---

## 7. DevOps Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test

on: push

jobs:
