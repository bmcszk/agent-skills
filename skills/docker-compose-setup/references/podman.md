# Podman Support
## 5. Podman Support

### Compatibility

Podman is fully Docker-compatible with rootless by default:

```just
# justfile - Podman commands
podman-up:
    podman compose -f docker-compose.yml -f docker-compose.dev.yml up -d

podman-down:
    podman compose -f docker-compose.yml -f docker-compose.dev.yml down

podman-clean:
    podman system prune -f
```

### Direct Replacement

```bash
# Optional: Create aliases
alias docker=podman
alias docker-compose='podman-compose'

# Or use podman directly via justfile
just podman-up
```

### Key Differences

| Feature | Docker | Podman |
|---------|--------|--------|
| Rootless | Optional | Default |
| Daemon | dockerd | Daemonless |
| Compose | docker compose | podman-compose |
| Systemd | Manual | Quadlets (native) |
| Security | Good | Better (no daemon) |

### Podman Quadlet (Systemd Integration)

```ini
# ~/.config/containers/systemd/app.container
[Unit]
Description=Go Application

[Container]
Image=localhost/app:latest
PublishPort=8080:8080
Environment=APP_ENV=production

[Service]
Restart=always

[Install]
WantedBy=default.target
```

---

