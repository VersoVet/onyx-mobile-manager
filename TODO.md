# TODO - onyx-mobile-manager

## ✅ Terminé
- [x] Backend API FastAPI (devices, history, apk modules)
- [x] SQLite schema + async CRUD operations
- [x] Pydantic models for validation
- [x] GUI client PyQt6 (4 panels: devices, vpn, apk, history)
- [x] Documentation (API.md, ARCHITECTURE.md, CLAUDE.md)
- [x] Unit tests for all modules (smoke tests)
- [x] Type checking (mypy strict mode)
- [x] Code linting (ruff check/format)
- [x] Git integration + .gitignore
- [x] Forge validation (18 phases)

## 🚀 À faire (futures versions)

### Tests & Quality
- [ ] Integration tests (API bout-en-bout)
- [ ] Coverage report (pytest --cov)
- [ ] End-to-end GUI tests (PyQt6 automation)
- [ ] Load testing (concurrent devices)

### Fonctionnalités métier
- [ ] WireGuard server-side (key generation, cert distribution)
- [ ] ADB wireless pairing automation
- [ ] Bulk device provisioning
- [ ] Device groups & profiles
- [ ] Configuration templates

### Infrastructure
- [ ] Notifications push via Redis events
- [ ] Metrics export (Prometheus)
- [ ] Centralized logging (ELK)
- [ ] Dashboard web (complement GUI)
- [ ] Multi-user authentication & RBAC

### Deployment
- [ ] GUI packaging avec PyInstaller
- [ ] Helm charts / Kubernetes
- [ ] Docker image for backend
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Automated releases

### Documentation
- [ ] API client SDK (Python)
- [ ] Deployment guide
- [ ] Developer guide (extending modules)
- [ ] User manual for GUI
- [ ] Troubleshooting guide
