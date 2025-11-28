# 🎉 Workspace EPCB - Configuration SSL Locale Complète!

Configuration terminée le: **2025-11-27**

---

## ✅ Ce qui est configuré

### 1. Certificat SSL Wildcard (mkcert)

**Certificat:** `*.axoiq.com`
- 📁 Emplacement: `config/traefik/axoiq.com.{crt,key}`
- 🔒 Type: mkcert (auto-signé de confiance)
- 📅 Valide jusqu'à: **2028-02-27**
- ✅ Aucun warning SSL dans le navigateur!

### 2. Serveur DNS Local (dnsmasq)

**Container:** `workspace-dnsmasq`
- 🌐 Port: `53` (DNS standard)
- 🎯 Résolution: `*.axoiq.com` → `127.0.0.1`
- 📊 Web UI: http://localhost:5380 (admin/admin)
- ✅ **TOUS les futurs sous-domaines fonctionnent automatiquement!**

### 3. Traefik (Reverse Proxy)

**Container:** `forge-traefik`
- 🔐 HTTPS: Port `443`
- 🌐 HTTP: Port `80`
- 📊 Dashboard: http://localhost:8888
- ✅ Routes configurées pour tous les services

---

## 🌐 Services Disponibles

Tous les services ci-dessous sont accessibles via HTTPS avec un certificat SSL valide!

### Applications Principales

| Service | URL HTTPS | URL Dev (HTTP) | Port Direct |
|---------|-----------|----------------|-------------|
| **Nexus** (Frontend) | https://nexus.axoiq.com | http://nexus.localhost | http://localhost:5173 |
| **Nexus** (Backend) | https://api-nexus.axoiq.com | http://api-nexus.localhost | http://localhost:8000 |
| **Synapse** (Frontend) | https://synapse.axoiq.com | http://synapse.localhost | http://localhost:4000 |
| **Synapse** (Backend) | https://api.axoiq.com | http://api.localhost | http://localhost:8001 |
| **Homepage Portal** | https://portal.axoiq.com | http://portal.localhost | http://localhost:3333 |
| **Owner Portal** | https://owner.axoiq.com | - | - |

### Monitoring & Observabilité

| Service | URL HTTPS | Credentials | Port Direct |
|---------|-----------|-------------|-------------|
| **Grafana** | https://grafana.axoiq.com | admin / admin | http://localhost:3000 |
| **Loki** | https://loki.axoiq.com | - | http://localhost:3100 |

### Base de Données

| Service | URL HTTPS | Credentials | Port Direct |
|---------|-----------|-------------|-------------|
| **pgAdmin** | https://pgadmin.axoiq.com | admin@example.com / admin | http://localhost:5050 |
| **Prisma Studio** | https://prisma.axoiq.com | - | http://localhost:5555 |
| **PostgreSQL** | - | postgres / postgres | localhost:5433 |
| **Redis** | - | - | localhost:6379 |

### Testing & Quality

| Service | URL HTTPS | Port Direct |
|---------|-----------|-------------|
| **ReportPortal** | https://reportportal.axoiq.com | http://localhost:8585 |
| **Allure** | https://allure.axoiq.com | http://localhost:5252 |

### Infrastructure

| Service | URL HTTPS | Credentials | Port Direct |
|---------|-----------|-------------|-------------|
| **Portainer** | https://portainer.axoiq.com | - | http://localhost:9000 |
| **Traefik Dashboard** | https://traefik.axoiq.com | - | http://localhost:8888 |
| **dnsmasq Web UI** | - | admin / admin | http://localhost:5380 |

---

## 🚀 Démarrage Rapide

### Démarrer tout le workspace:

```powershell
cd D:\Projects\EPCB-Tools\workspace

# Infrastructure de base
docker-compose up -d

# Traefik (reverse proxy)
docker-compose -f docker-compose.traefik.yml up -d

# DNS local (pour *.axoiq.com)
docker-compose -f docker-compose.dns.yml up -d

# Nexus
cd D:\Projects\nexus
docker-compose -f docker-compose.dev.yml -f docker-compose.traefik-labels.yml up -d
```

### Configurer le DNS Windows (une seule fois):

```powershell
cd D:\Projects\EPCB-Tools\workspace
.\configure-dns.ps1
```

---

## 📝 Ajouter un Nouveau Service

### Étape 1: Créer le service Docker

```yaml
services:
  mon-service:
    image: mon-image:latest
    networks:
      - forge-network  # Important!

networks:
  forge-network:
    external: true
```

### Étape 2: Ajouter la route Traefik

Éditer: `workspace/config/traefik/dynamic.yml`

```yaml
http:
  routers:
    mon-service-prod:
      rule: "Host(`mon-service.axoiq.com`)"
      service: mon-service
      entryPoints:
        - websecure
      tls: {}  # Certificat wildcard automatique!

  services:
    mon-service:
      loadBalancer:
        servers:
          - url: "http://nom-container:port"
```

### Étape 3: Redémarrer Traefik

```powershell
docker restart forge-traefik
```

### Étape 4: Accéder

**C'est tout!** Accédez à: `https://mon-service.axoiq.com`
- ✅ SSL valide automatiquement
- ✅ DNS automatiquement (grâce à dnsmasq)
- ✅ Routing automatiquement (grâce à Traefik)

---

## 🔧 Commandes Utiles

### Vérifier les services

```powershell
# Tous les conteneurs
docker ps

# Services sur forge-network
docker network inspect forge-network

# Routes Traefik
curl http://localhost:8888/api/http/routers | python -m json.tool

# Tester DNS
nslookup nexus.axoiq.com
# Devrait répondre: 127.0.0.1
```

### Logs

```powershell
# Traefik
docker logs forge-traefik --tail 50 -f

# dnsmasq
docker logs workspace-dnsmasq --tail 50 -f

# Nexus
docker logs nexus-backend --tail 50 -f
docker logs nexus-frontend --tail 50 -f
```

### Redémarrer les services

```powershell
# Traefik
docker restart forge-traefik

# DNS
docker restart workspace-dnsmasq

# Nexus
docker restart nexus-backend nexus-frontend

# Synapse
docker restart synapse-backend synapse-frontend-1
```

---

## 🛡️ Sécurité

### Certificats SSL

- **Environnement:** Développement local uniquement
- **Validité:** Les certificats mkcert sont valides **uniquement sur votre machine**
- **Production:** Pour la production, utilisez Let's Encrypt avec le DNS Challenge de Cloudflare

### DNS

- **Environnement:** Développement local
- **Fallback:** Toutes les requêtes non-`*.axoiq.com` sont envoyées à Google DNS (8.8.8.8)
- **Pi-hole:** Votre Pi-hole principal reste actif pour le reste du réseau

---

## 🔄 Revenir à la configuration DNS précédente

Si vous voulez désactiver le DNS local:

```powershell
# PowerShell en administrateur
Set-DnsClientServerAddress -InterfaceAlias 'Wi-Fi' -ResetServerAddresses

# OU utiliser votre Pi-hole
Set-DnsClientServerAddress -InterfaceAlias 'Wi-Fi' -ServerAddresses ('192.168.x.x')
```

---

## 📚 Documentation

- **Configuration SSL:** `LOCAL-SSL-SETUP.md`
- **Ajouter services:** `ADDING-NEW-SERVICES.md`
- **Roadmap Nexus:** `../apps/nexus/.dev/roadmap/README.md`

---

## ✨ Avantages de cette configuration

✅ **SSL valide** - Pas de warning "Not Secure"
✅ **Wildcard automatique** - Nouveaux services fonctionnent instantanément
✅ **Pas de hosts file** - Plus besoin de le modifier manuellement
✅ **Production-like** - Même domaine dev/prod
✅ **Isolé** - N'affecte pas votre réseau principal
✅ **Révocable** - Un seul commit pour tout désactiver

---

## 🆘 Dépannage

### Service retourne 404

1. Vérifier que le conteneur est sur `forge-network`
2. Vérifier la route dans `config/traefik/dynamic.yml`
3. Redémarrer Traefik: `docker restart forge-traefik`

### DNS ne résout pas

1. Vérifier que dnsmasq tourne: `docker ps | grep dnsmasq`
2. Vérifier la config DNS Windows: `Get-DnsClientServerAddress -InterfaceAlias 'Wi-Fi'`
3. Vider le cache: `ipconfig /flushdns`
4. Tester: `nslookup nexus.axoiq.com`

### Certificat SSL invalide

1. Vérifier que mkcert CA est installée: `mkcert -install`
2. Vider le cache du navigateur
3. Redémarrer Traefik: `docker restart forge-traefik`

---

**Dernière mise à jour:** 2025-11-27
**Version:** 1.0.0
**Auteur:** EPCB Workspace Team
