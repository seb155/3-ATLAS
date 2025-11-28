# Guide: Ajouter un nouveau service à axoiq.com

Ce guide explique comment ajouter rapidement un nouveau service dans le workspace avec SSL local.

---

## 🚀 Méthode rapide (3 étapes)

### 1️⃣ Ajouter l'entrée DNS locale

**Option A: Script automatique (Recommandé)**
```powershell
# Exécuter en tant qu'administrateur
.\add-service-to-hosts.ps1 -ServiceName "mon-nouveau-service"
```

**Option B: Manuelle**
```powershell
# Ouvrir en administrateur:
notepad C:\Windows\System32\drivers\etc\hosts

# Ajouter:
127.0.0.1    mon-nouveau-service.axoiq.com
```

---

### 2️⃣ Ajouter la route Traefik

Éditer: `config/traefik/dynamic.yml`

```yaml
http:
  routers:
    # Ajouter ces sections:

    # ========================================================================
    # PRODUCTION ROUTE (HTTPS avec certificat mkcert)
    # ========================================================================
    mon-nouveau-service-prod:
      rule: "Host(`mon-nouveau-service.axoiq.com`)"
      service: mon-nouveau-service
      entryPoints:
        - websecure
      tls: {}  # Utilise le certificat wildcard *.axoiq.com

    # ========================================================================
    # DEVELOPMENT ROUTE (HTTP pour localhost)
    # ========================================================================
    mon-nouveau-service-dev:
      rule: "Host(`mon-nouveau-service.localhost`)"
      service: mon-nouveau-service
      entryPoints:
        - web
      priority: 1

  services:
    # Ajouter le service backend:
    mon-nouveau-service:
      loadBalancer:
        servers:
          - url: "http://nom-container:port"
```

---

### 3️⃣ Redémarrer Traefik

```powershell
docker restart forge-traefik
```

**C'est tout!** Votre nouveau service est accessible à:
- ✅ https://mon-nouveau-service.axoiq.com (SSL valide, pas de warning!)
- ✅ http://mon-nouveau-service.localhost (dev)

---

## 📋 Exemples complets

### Exemple 1: Ajouter "reportportal"

**1. Hosts file:**
```
127.0.0.1    reportportal.axoiq.com
```

**2. Traefik (`dynamic.yml`):**
```yaml
http:
  routers:
    reportportal-prod:
      rule: "Host(`reportportal.axoiq.com`)"
      service: reportportal
      entryPoints:
        - websecure
      tls: {}

    reportportal-dev:
      rule: "Host(`reportportal.localhost`)"
      service: reportportal
      entryPoints:
        - web

  services:
    reportportal:
      loadBalancer:
        servers:
          - url: "http://reportportal-ui:8080"
```

**3. Redémarrer:**
```powershell
docker restart forge-traefik
```

**4. Accéder:**
- https://reportportal.axoiq.com ✅

---

### Exemple 2: Ajouter un service avec backend + frontend

**Service:** Allure Report (frontend + API)

**1. Hosts file:**
```
127.0.0.1    allure.axoiq.com
127.0.0.1    api-allure.axoiq.com
```

**2. Traefik:**
```yaml
http:
  routers:
    # Frontend
    allure-frontend-prod:
      rule: "Host(`allure.axoiq.com`)"
      service: allure-frontend
      entryPoints:
        - websecure
      tls: {}

    # Backend API
    allure-backend-prod:
      rule: "Host(`api-allure.axoiq.com`)"
      service: allure-backend
      entryPoints:
        - websecure
      tls: {}

  services:
    allure-frontend:
      loadBalancer:
        servers:
          - url: "http://allure-ui:5050"

    allure-backend:
      loadBalancer:
        servers:
          - url: "http://allure-api:8000"
```

---

## 🔐 Certificats SSL

**Bonne nouvelle:** Le certificat wildcard `*.axoiq.com` est déjà généré!

Il couvre automatiquement:
- ✅ nexus.axoiq.com
- ✅ synapse.axoiq.com
- ✅ **N'IMPORTE QUEL nouveau sous-domaine!**

Valide jusqu'en: **2028-02-27**

**Pas besoin de régénérer** pour chaque nouveau service! 🎉

---

## 🎯 Checklist pour nouveau service

- [ ] Ajouter entrée dans hosts file (`add-service-to-hosts.ps1`)
- [ ] Ajouter routes dans `config/traefik/dynamic.yml`
- [ ] Redémarrer Traefik (`docker restart forge-traefik`)
- [ ] Tester: https://mon-service.axoiq.com
- [ ] Vérifier cadenas vert 🔒

---

## 🔧 Dépannage

### Le service retourne 404

**Cause:** Traefik ne voit pas le service

**Solution:**
```powershell
# Vérifier que le conteneur est sur forge-network
docker network inspect forge-network | grep mon-service

# Vérifier les routes Traefik
curl http://localhost:8888/api/http/routers | findstr mon-service

# Redémarrer Traefik
docker restart forge-traefik
```

---

### Le service retourne "Bad Gateway"

**Cause:** Le conteneur n'est pas démarré ou l'URL backend est incorrecte

**Solution:**
```powershell
# Vérifier que le conteneur tourne
docker ps | findstr mon-service

# Vérifier le nom du conteneur dans dynamic.yml
# Doit matcher exactement le nom du container
```

---

### Pas de SSL / Warning SSL

**Cause:** Le certificat n'est pas chargé ou la route n'a pas `tls: {}`

**Solution:**
```powershell
# Vérifier que la route a bien tls: {}
cat config/traefik/dynamic.yml | findstr -A 5 mon-service

# Redémarrer Traefik
docker restart forge-traefik
```

---

## 📚 Services déjà configurés

| Service | URL Production | URL Dev |
|---------|---------------|---------|
| Nexus Frontend | https://nexus.axoiq.com | http://nexus.localhost |
| Nexus Backend | https://api-nexus.axoiq.com | http://api-nexus.localhost |
| Synapse Frontend | https://synapse.axoiq.com | http://synapse.localhost |
| Synapse Backend | https://api.axoiq.com | http://api.localhost |
| Portal | https://portal.axoiq.com | http://portal.localhost |
| Grafana | https://grafana.axoiq.com | http://grafana.localhost |
| Loki | https://loki.axoiq.com | http://loki.localhost |
| pgAdmin | https://pgadmin.axoiq.com | http://pgadmin.localhost |
| Prisma | https://prisma.axoiq.com | http://prisma.localhost |

---

**Dernière mise à jour:** 2025-11-27
