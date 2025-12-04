# Infrastructure Multi-Environnement

> Documentation centralisée des environnements de développement et production.

## Vue d'Ensemble

| Environnement | Domain | Reverse Proxy | Location |
|---------------|--------|---------------|----------|
| **FORGE (DEV)** | `*.axoiq.com` | Traefik | Laptop WSL |
| **HOMELAB (PROD)** | `*.s-gagnon.com` | nginx | Proxmox PVE1/PVE2 |

---

## FORGE - Environnement de Développement

**Location:** `/home/seb/projects/AXIOM/modules/forge/`

### Services Infrastructure

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| Traefik | 8888 | traefik.axoiq.com | Reverse proxy + SSL |
| PostgreSQL | 5433 | - | Base de données partagée |
| Redis | 6379 | - | Cache & Sessions |
| Grafana | 3000 | grafana.axoiq.com | Monitoring & Logs |
| Loki | 3100 | - | Agrégation des logs |
| pgAdmin | 5050 | pgadmin.axoiq.com | Admin PostgreSQL |
| Prisma Studio | 5555 | prisma.axoiq.com | Viewer BDD |
| MeiliSearch | 7700 | - | Full-text search |

### Applications Déployées

| App | Port | URL | Status |
|-----|------|-----|--------|
| **Nexus** | 5173 | nexus.axoiq.com | Active |
| **Echo** | 7200 | echo.axoiq.com | Active |
| **FinDash** | 6400 | findash.axoiq.com | Active |
| **MechVision** | (interne) | mechvision.axoiq.com | Active |
| Synapse | 4000 | synapse.axoiq.com | Development |

### Configuration Hosts (Windows)

Pour accéder via `*.axoiq.com`, ajouter dans `C:\Windows\System32\drivers\etc\hosts`:

```
127.0.0.1 findash.axoiq.com
127.0.0.1 nexus.axoiq.com
127.0.0.1 echo.axoiq.com
127.0.0.1 synapse.axoiq.com
127.0.0.1 grafana.axoiq.com
127.0.0.1 traefik.axoiq.com
127.0.0.1 pgadmin.axoiq.com
127.0.0.1 prisma.axoiq.com
```

**Script automatique:** `AXIOM/modules/forge/add-all-services-to-hosts.bat`

### Réseau Docker

```bash
# Vérifier le réseau
docker network ls | grep forge

# Toutes les apps doivent être sur forge-network
docker-compose.yml:
  networks:
    forge-network:
      external: true
```

---

## HOMELAB - Environnement de Production

**Location:** `/home/seb/projects/homelab/`

### Topologie Réseau

```
Internet
    │
    ▼
┌─────────────────────────────────────────────┐
│ UDM-SE (192.168.1.1) - UniFi Router        │
│   ├── VLAN 1: Management (192.168.1.x)     │
│   └── VLAN 10: Servers (192.168.10.x)      │
└─────────────────────────────────────────────┘
    │
    ├── PVE1 (192.168.1.20) - Web Services
    │     └── TrueNAS
    │
    ├── PVE2 (192.168.1.21) - AI/ML + Gaming
    │     └── 2x RTX 3080 Ti
    │
    └── Docker VM (192.168.10.55) - Containers
          ├── nginx (reverse proxy)
          ├── pihole (DNS)
          └── Applications...
```

### Nodes Proxmox

| Node | IP | Rôle | Ressources |
|------|----|----|------------|
| **PVE1** | 192.168.1.20 | Web Services, TrueNAS | Mini PC |
| **PVE2** | 192.168.1.21 | Gaming, AI/ML | 2x GPU RTX 3080 Ti |
| **Docker VM** | 192.168.10.55 | Containers production | VM 600 sur PVE |

### Services DNS (pihole)

Le pihole gère la résolution `*.s-gagnon.com` vers la Docker VM:

```
# Entrées DNS pihole
findash.s-gagnon.com → 192.168.10.55
grafana.s-gagnon.com → 192.168.10.55
home.s-gagnon.com → 192.168.10.55
```

### Reverse Proxy (nginx)

Configuration type pour une app:

```nginx
# /etc/nginx/sites-available/findash.s-gagnon.com
server {
    listen 443 ssl;
    server_name findash.s-gagnon.com;

    ssl_certificate /etc/letsencrypt/live/s-gagnon.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/s-gagnon.com/privkey.pem;

    location / {
        proxy_pass http://localhost:6400;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

---

## Déploiement d'Applications

### Vers FORGE (Dev)

```bash
# Option 1: Docker Compose
cd /path/to/app
docker-compose up -d

# Option 2: Slash command Atlas
/deploy findash forge
```

### Vers HOMELAB (Prod)

```bash
# Option 1: SSH + Docker
ssh docker@192.168.10.55 "cd /apps/findash && docker-compose up -d"

# Option 2: Slash command Atlas
/deploy findash homelab
```

---

## Allocation des Ports

| Range | Environnement/App |
|-------|-------------------|
| 3000-3999 | FORGE infrastructure |
| 4000-4999 | SYNAPSE |
| 5000-5999 | NEXUS |
| 6000-6999 | APEX + Personal projects |
| 7000-7999 | ATLAS/CORTEX |

**Référence complète:** `.dev/infra/url-registry.yml`

---

## Accès Rapides

### FORGE (Dev)
- FinDash: http://localhost:6400
- Nexus: http://localhost:5173
- Grafana: http://localhost:3000

### HOMELAB (Prod)
- FinDash: https://findash.s-gagnon.com
- Homepage: https://home.s-gagnon.com

---

## Troubleshooting

### Port déjà utilisé
```bash
# Voir quel process utilise un port
lsof -i :5173
ss -tlnp | grep 5173

# Vite auto-incrémente si le port est pris (5173 → 5174)
```

### Container ne démarre pas
```bash
# Vérifier les logs
docker logs findash-app -f --tail 100

# Vérifier le réseau
docker network inspect forge-network
```

### Hosts file ne fonctionne pas
```powershell
# Windows: Flush DNS cache
ipconfig /flushdns

# Vérifier que le fichier hosts est bien sauvegardé (en admin)
notepad C:\Windows\System32\drivers\etc\hosts
```

---

## Fichiers de Référence

| Fichier | Description |
|---------|-------------|
| `.dev/infra/url-registry.yml` | Registry centralisé URLs/Ports |
| `AXIOM/modules/forge/docker-compose.yml` | Services Forge |
| `homelab/docker-compose.yml` | Services Homelab |
| `.claude/docs/infrastructure.md` | Ce document |
