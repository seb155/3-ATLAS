# 🚀 SYNAPSE Portal - Enterprise Dashboard

**Last Updated:** 2025-11-24
**Version:** Portal v1.0 | SYNAPSE v0.2.1

---

## ✅ Portal Homepage

**Main URL:** http://localhost:3333

Your central enterprise dashboard with access to all SYNAPSE platform services.

---

## 📊 All Services (13 Total)

### Applications (2 services)
| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:4000 | React 19 Application |
| Backend API | http://localhost:8001/docs | FastAPI Documentation |

### Testing & Reporting (0 dedicated services)
Tests use local HTML reports and Vitest UI; no extra reporting containers are required.

### Databases (2 services)
| Service | URL | Description |
|---------|-----|-------------|
| pgAdmin | http://localhost:5050 | PostgreSQL Admin UI |
| Prisma Studio | http://localhost:5555 | Visual Database Viewer |

### Monitoring & Logging (2 services)
| Service | URL | Description | Credentials |
|---------|-----|-------------|-------------|
| Grafana | http://localhost:3000 | Metrics & Log Dashboards | `admin` / `xZfFu3&FZCBe` |
| Loki API | http://localhost:3100/ready | Log Aggregation Service | - |

**Pre-configured Dashboards:**
- SYNAPSE Logs (ID: 1)
- System Metrics

### Infrastructure (2 services)
| Service | URL | Description |
|---------|-----|-------------|
| Traefik Dashboard | http://localhost:8888 | Reverse Proxy & SSL Manager |
| Portainer | http://localhost:9000 | Docker Management UI |

---

## 🔗 Quick Links

### Development
- **GitHub Repository:** https://github.com/seb155/EPCB-Tools
- **Project Documentation:** https://github.com/seb155/EPCB-Tools/tree/main/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React 19 Docs:** https://react.dev
- **Homepage Docs:** https://gethomepage.dev

### Internal
- **Credentials:** `.dev/context/credentials.md`
- **Project State:** `.dev/context/project-state.md`
- **Roadmap:** `.dev/roadmap/README.md`

---

## 🚀 Starting the Portal

### Quick Start (All Services)
```powershell
# Start everything (workspace + SYNAPSE + ReportPortal)
.\dev.ps1
```

### Manual Start
```powershell
# Start infrastructure + Portal
cd workspace
docker-compose -f docker-compose.yml -f docker-compose.traefik.yml -f docker-compose.homepage.yml up -d

# Start SYNAPSE app
cd ..\apps\synapse
docker-compose -f docker-compose.dev.yml up -d
```

### Selective Start (Light Mode - No ReportPortal)
```powershell
cd workspace
docker-compose -f docker-compose.yml -f docker-compose.traefik.yml -f docker-compose.homepage.yml up -d

cd ..\apps\synapse
docker-compose -f docker-compose.dev.yml up -d
```

---

## 🛑 Stopping Everything

```powershell
# Stop all services
.\stop.ps1

# Or manually
cd workspace
docker-compose down
docker-compose -f docker-compose.reportportal.yml down

cd ..\apps\synapse
docker-compose down
```

---

## 🎨 Portal Features

### Modern UI
- **Clean Dark Theme** - Professional enterprise design
- **Real-time Docker Stats** - CPU, Memory, Container status
- **Service Widgets** - Live status for all services
- **Quick Search** - Fast access to any service
- **Responsive Design** - Works on desktop, tablet, mobile

### Custom Styling
- Located in: `workspace/homepage/config/custom.css`
- Professional dark theme
- Minimalist design
- Corporate color palette

### Configuration Files
```
workspace/homepage/config/
├── settings.yaml      # Portal settings (theme, layout)
├── services.yaml      # Service definitions (13 services)
├── bookmarks.yaml     # Quick links
├── widgets.yaml       # Dashboard widgets
├── docker.yaml        # Docker socket config
└── custom.css         # Custom styling
```

---

## 🔧 Technical Details

### Stack Versions
- **Traefik:** v3.6.2 (Docker 29 compatible)
- **Homepage:** latest (gethomepage)
- **Docker:** 29.0.1
- **ReportPortal:** Latest (v5.x)

### Docker Containers (Typical Dev Setup)

**SYNAPSE (2):**
- synapse-frontend-1
- synapse-backend

**Workspace Core (6):**
- workspace-postgres
- workspace-redis
- workspace-loki
- workspace-grafana
- workspace-promtail
- workspace-pgadmin

**Portal & Infrastructure (3):**
- workspace-homepage
- workspace-traefik
- workspace-prisma

**ReportPortal:** Removed (using local HTML + Vitest UI)

---

## 🧪 Testing Infrastructure

### Backend Testing (pytest + HTML)
```bash
cd apps/synapse/backend
docker exec -it synapse-backend pytest --html=reports/backend-report.html --self-contained-html
```

### Frontend E2E (Playwright)
```bash
cd apps/synapse/frontend
npx playwright test
```
HTML report: `apps/synapse/frontend/playwright-report/index.html`

---

## 🔍 Troubleshooting

### Portal not loading?
```powershell
# Check Homepage container
docker logs workspace-homepage --tail 50

# Restart Homepage
cd workspace
docker-compose -f docker-compose.yml -f docker-compose.traefik.yml -f docker-compose.homepage.yml restart homepage
```

### Service not accessible?
```powershell
# Check if container is running
docker ps | findstr [service-name]

# Check logs
docker logs [container-name] --tail 50
```

### Docker widgets not showing?
Docker socket permissions issue. Fixed by Homepage config:
```yaml
# workspace/homepage/config/docker.yaml
docker-socket:
  socket: /var/run/docker.sock
```

---

## 🌍 Production Deployment

When deploying to production:

1. **Update environment variables:**
   ```env
   # workspace/.env
   DOMAIN=aurumax.com
   ACME_EMAIL=admin@aurumax.com
   ```

2. **Enable Let's Encrypt SSL:**
   ```yaml
   # Remove staging line in docker-compose.traefik.yml
   # Uncomment production ACME server
   ```

3. **Configure DNS:**
   ```
   portal.aurumax.com     → SERVER_IP
   synapse.aurumax.com    → SERVER_IP
   api.aurumax.com        → SERVER_IP
   grafana.aurumax.com    → SERVER_IP
   ```

4. **Update Homepage URLs:**
   ```yaml
   # workspace/homepage/config/services.yaml
   # Change all http://localhost:PORT to https://service.aurumax.com
   ```

5. **Deploy:**
   ```bash
   ./start-portal.sh
   ```

**SSL certificates will be automatic!** ✅

---

## 📚 Documentation

| Topic | Location |
|-------|----------|
| Testing Guide | `workspace/README-TESTING.md` |
| Developer Guide | `docs/developer-guide/` |
| Backend Guide | `docs/developer-guide/02-backend-guide.md` |
| Frontend Guide | `docs/developer-guide/03-frontend-guide.md` |
| Database | `docs/developer-guide/04-database.md` |
| ReportPortal Setup | `docs/developer-guide/06-testing-reportportal.md` |

---

## 💡 Tips

- **Fastest Access:** Bookmark `http://localhost:3333` in your browser
- **DevConsole:** Press `Ctrl + \` in Frontend for real-time logs
- **Docker Stats:** Portal homepage shows live container status
- **Testing:** Use ReportPortal for centralized trends and analytics

---

**Enjoy your SYNAPSE Enterprise Portal!** 🎉

For issues or questions:
- **GitHub Issues:** https://github.com/seb155/EPCB-Tools/issues
- **Documentation:** `.dev/context/` and `docs/`
