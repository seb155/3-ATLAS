# SYNAPSE Portal - Modern Development Dashboard

**Professional application portal with reverse proxy, SSL, and modern UI**

---

## 🚀 Quick Start

```powershell
# Windows (PowerShell)
cd workspace
.\start-portal.ps1
```

```bash
# Linux/macOS (Bash)
cd workspace
chmod +x start-portal.sh
./start-portal.sh
```

Access Portal: https://portal.localhost

**First time?** Your browser will warn about SSL. That's normal for `.localhost` - click "Advanced" → "Continue".

---

## 🎯 What's Included

### Portal Dashboard (Homepage)
- **Modern UI** - Glassmorphism, gradients, animations
- **Docker Integration** - Real-time container status
- **Quick Access** - All services in one place
- **System Monitoring** - CPU, RAM, disk usage
- **Future Ready** - Prepared for AI search/chatbot

### Owner Portal (React) – NEW
- **Read-only** dashboard for health, tests, tech debt, architecture checkpoints
- Served at `https://portal.localhost` (via Traefik)
- Data source: `synapse_analytics.owner.*` (API read-only)

### Reverse Proxy (Traefik)
- **Auto SSL** - Automatic HTTPS for all services
- **Smart Routing** - Domain-based (no more ports!)
- **Dashboard** - http://localhost:8888
- **Production Ready** - Let's Encrypt support

---

## 📱 Access URLs

### Development (Default)
```
Portal:       https://portal.localhost
Traefik:      http://localhost:8888

Applications:
  Frontend:   https://synapse.localhost
  API:        https://api.localhost/docs

Monitoring:
  Grafana:    https://grafana.localhost
  Loki:       https://loki.localhost

Databases:
  pgAdmin:    https://pgadmin.localhost
  Prisma:     https://prisma.localhost
```

### Production (Your Domain)
Edit `workspace/.env`:
```env
DOMAIN=yourdomain.com
ACME_EMAIL=youremail@domain.com
```

Then access via:
```
https://portal.yourdomain.com
https://synapse.yourdomain.com
https://api.yourdomain.com
(etc...)
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│  Internet / Browser                 │
└──────────┬──────────────────────────┘
           │
           ↓
┌──────────────────────────────────────┐
│  Traefik (Reverse Proxy)             │
│  • SSL termination                   │
│  • Routing by domain                 │
│  • Let's Encrypt                     │
└──────────┬───────────────────────────┘
           │
     ┌─────┴─────┬──────────┬─────────┐
     ↓           ↓          ↓         ↓
  Homepage   Synapse    Grafana   pgAdmin
  (Portal)   (App)   (Monitoring) (DB)
```

---

## 📁 Files Structure

```
workspace/
├── docker-compose.yml                      # Core infrastructure
├── docker-compose.traefik.yml              # Reverse proxy
├── docker-compose.homepage.yml             # Portal dashboard
├── docker-compose.traefik-labels.yml       # Traefik routing
│
├── .env                                    # Configuration
├── .env.example                            # Template
│
├── start-portal.ps1                        # Start everything
├── stop-portal.ps1                         # Stop everything
│
└── homepage/
    └── config/
        ├── settings.yaml                   # Portal settings
        ├── services.yaml                   # Services list
        ├── widgets.yaml                    # Dashboard widgets
        ├── docker.yaml                     # Docker integration
        ├── bookmarks.yaml                  # Quick links
        └── custom.css                      # Modern design

apps/synapse/
└── docker-compose.traefik-labels.yml       # Synapse routing
```

---

## 🎨 Design Features

**Modern Tech Startup Style:**
- ✅ Glassmorphism (blurred glass effect)
- ✅ Gradient colors (blue/purple/cyan)
- ✅ Smooth animations & hover effects
- ✅ Glow effects on active elements
- ✅ Responsive design
- ✅ Dark theme optimized

**Inspired by:** Vercel, Linear, Arc Browser

---

## ⚙️ Configuration

### Domain Configuration

**Development (.localhost):**
```env
# workspace/.env
DOMAIN=localhost
```
- Auto SSL via Traefik
- Works without DNS
- Browser might warn (normal)

**Production (Real Domain):**
```env
# workspace/.env
DOMAIN=yourdomain.com
ACME_EMAIL=youremail@domain.com
```

**DNS Setup:**
Point these A records to your server IP:
```
portal.yourdomain.com       → YOUR_SERVER_IP
synapse.yourdomain.com      → YOUR_SERVER_IP
api.yourdomain.com          → YOUR_SERVER_IP
grafana.yourdomain.com      → YOUR_SERVER_IP
(etc...)
```

**Traefik Production SSL:**
Edit `workspace/docker-compose.traefik.yml`:
```yaml
# Remove this line (staging server):
- "--certificatesresolvers.letsencrypt.acme.caserver=https://acme-staging-v02.api.letsencrypt.org/directory"
```

### Customize Homepage

**Edit Services:**
```yaml
# workspace/homepage/config/services.yaml
- Applications:
    - My New Service:
        icon: mdi-rocket
        href: https://myservice.${HOMEPAGE_VAR_DOMAIN:-localhost}
        description: My awesome service
```

**Edit Design:**
```css
/* workspace/homepage/config/custom.css */
:root {
  --brand-primary: #your-color;
}
```

**Add Widgets:**
```yaml
# workspace/homepage/config/widgets.yaml
- weather:
    latitude: 45.5017
    longitude: -73.5673
```

---

## 🔧 Management

### Start Portal
```powershell
.\workspace\start-portal.ps1
```

### Stop Portal
```powershell
.\workspace\stop-portal.ps1
```

### Start Individual Services

```powershell
# Just core infrastructure
cd workspace
docker-compose up -d

# Add Traefik
docker-compose -f docker-compose.yml -f docker-compose.traefik.yml up -d

# Add Homepage
docker-compose -f docker-compose.yml -f docker-compose.traefik.yml -f docker-compose.homepage.yml -f docker-compose.traefik-labels.yml up -d

# Frontend E2E (Playwright) and backend pytest are run from their app folders
```

### Restart Single Service
```powershell
docker restart forge-homepage
docker restart forge-traefik
```

### View Logs
```powershell
docker logs -f forge-homepage
docker logs -f forge-traefik
```

---

## 🐛 Troubleshooting

### SSL Certificate Warnings

**Problem:** Browser shows "Not Secure"

**For `.localhost` (Dev):**
- Normal! Traefik generates self-signed certs
- Click "Advanced" → "Proceed to localhost (unsafe)"
- Or install Traefik CA in your system

**For Production:**
- Wait 30-60 seconds for Let's Encrypt
- Check DNS is pointed correctly
- Check Traefik logs: `docker logs forge-traefik`

### Can't Access Portal

**Check services:**
```powershell
docker ps --filter "name=workspace"
```

**Check Traefik routing:**
```powershell
# Open dashboard
Start http://localhost:8888

# Check "HTTP Routers" section
```

**Check logs:**
```powershell
docker logs forge-traefik
docker logs forge-homepage
```

### Service Not Routing

**1. Check labels:**
```bash
docker inspect forge-homepage | grep traefik
```

**2. Check Traefik can see it:**
- Open http://localhost:8888
- Go to "HTTP" → "Routers"
- Should see `homepage` router

**3. Restart Traefik:**
```powershell
docker restart forge-traefik
```

### Homepage Not Showing Services

**1. Check Docker socket:**
```powershell
docker exec forge-homepage ls -la /var/run/docker.sock
```

**2. Check services.yaml syntax:**
```powershell
# Validate YAML
docker exec forge-homepage cat /app/config/services.yaml
```

**3. Restart Homepage:**
```powershell
docker restart forge-homepage
```

---

## 🚀 Production Deployment

### Prerequisites
1. Server with Docker & Docker Compose
2. Domain name (e.g., `yourdomain.com`)
3. DNS access to create A records
4. Ports 80 & 443 open

### Steps

**1. Clone repo:**
```bash
git clone <your-repo>
cd EPCB-Tools/workspace
```

**2. Configure environment:**
```bash
cp .env.example .env
nano .env
```

```env
DOMAIN=yourdomain.com
ACME_EMAIL=youremail@domain.com
```

**3. Setup DNS:**
Point these to your server IP:
- `portal.yourdomain.com`
- `synapse.yourdomain.com`
- `api.yourdomain.com`
- `grafana.yourdomain.com`
- (etc...)

**4. Enable production SSL:**
Edit `docker-compose.traefik.yml`:
```yaml
# Comment out or remove:
# - "--certificatesresolvers.letsencrypt.acme.caserver=..."
```

**5. Start portal:**
```bash
./start-portal.sh  # Or use PowerShell script
```

**6. Verify:**
- Open `https://portal.yourdomain.com`
- Check for valid SSL (green padlock)
- All services accessible

### Security Hardening

**1. Change default credentials:**
- Grafana: https://grafana.yourdomain.com
- pgAdmin: https://pgadmin.yourdomain.com
- ReportPortal: https://reportportal.yourdomain.com

**2. Enable Traefik dashboard auth:**
```yaml
# docker-compose.traefik.yml
- "--api.insecure=false"  # Disable insecure API
# Add BasicAuth middleware
```

**3. Firewall rules:**
```bash
# Allow only 80, 443, SSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

**4. Regular updates:**
```bash
docker-compose pull
docker-compose up -d
```

---

## 🔮 Future: AI Integration

The portal is prepared for AI search & chatbot:

**Planned Features:**
- 🔍 **Enterprise Search** - Query logs, tests, code, docs
- 💬 **AI Assistant** - ChatGPT-style interface
- 🤖 **Auto-debugging** - AI analyzes failed tests
- 📊 **Smart Insights** - Predictive analytics

**Architecture Ready:**
- Search widget slot reserved
- API endpoints planned
- Vector DB integration prepared
- See: `workspace/README-TESTING.md` for details

---

## 📚 Resources

**Homepage:**
- Docs: https://gethomepage.dev
- Icons: https://pictogrammers.com/library/mdi/
- Widgets: https://gethomepage.dev/latest/widgets/

**Traefik:**
- Docs: https://doc.traefik.io/traefik/
- Dashboard: http://localhost:8888
- Routing: https://doc.traefik.io/traefik/routing/overview/

**Project Docs:**
- Testing: `workspace/README-TESTING.md`
- Credentials: `.dev/context/credentials.md`
- Architecture: `docs/getting-started/03-architecture-overview.md`

---

**Updated:** 2025-11-24
