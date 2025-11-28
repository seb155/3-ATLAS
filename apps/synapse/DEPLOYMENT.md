# SYNAPSE - Guide de Déploiement Production

## Vue d'ensemble

Ce guide couvre le déploiement de SYNAPSE pour **10-100 utilisateurs** sur:
- Serveur Linux local
- AWS EC2
- Hetzner Cloud

**Stack 100% gratuit et open source** (sauf si vous choisissez OpenAI/Gemini pour l'IA)

---

## Prérequis

### Matériel Recommandé

| Utilisateurs | CPU | RAM | Stockage |
|--------------|-----|-----|----------|
| 10-15 | 4 cores | 16GB | 100GB SSD |
| 15-50 | 8 cores | 32GB | 200GB SSD |
| 50-100 | 16 cores | 64GB | 500GB SSD |

### Logiciels

```bash
# Ubuntu 22.04+ / Debian 12+
sudo apt update && sudo apt install -y \
    docker.io \
    docker-compose-plugin \
    git \
    curl

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker
```

---

## Déploiement Rapide (5 minutes)

### 1. Cloner le repository

```bash
git clone https://github.com/votre-org/EPCB-Tools.git
cd EPCB-Tools
```

### 2. Démarrer l'infrastructure partagée

```bash
cd workspace
docker compose up -d forge-postgres forge-redis
```

### 3. Configurer l'environnement

```bash
cd ../apps/synapse
cp .env.production.example .env.production

# Éditer la configuration
nano .env.production
```

**Configuration minimale requise:**
```bash
POSTGRES_PASSWORD=VotreMotDePasseFort123!
SECRET_KEY=$(openssl rand -hex 32)
AI_PROVIDER=ollama
```

### 4. Démarrer SYNAPSE

```bash
# Démarrage standard (2 backends)
docker compose -f docker-compose.prod.yml --env-file .env.production up -d

# Avec plus de backends pour 50+ utilisateurs
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --scale backend=4
```

### 5. Initialiser le modèle AI (Ollama)

```bash
# Télécharger le modèle (première fois seulement, ~4GB)
docker exec synapse-ollama ollama pull llama3.2

# Pour un modèle plus performant (si GPU disponible)
docker exec synapse-ollama ollama pull llama3.1:70b
```

### 6. Accéder à l'application

- **URL:** http://votre-serveur:80
- **Login par défaut:** admin@aurumax.com / admin123!

---

## Configuration AI

### Option 1: Ollama (Gratuit - Recommandé)

**Avantages:**
- 100% gratuit
- Données restent sur votre serveur
- Pas de dépendance externe
- Performances acceptables même sur CPU

```bash
# .env.production
AI_PROVIDER=ollama
AI_MODEL=llama3.2
OLLAMA_BASE_URL=http://ollama:11434
```

**Modèles recommandés:**

| Modèle | Taille | RAM requise | Usage |
|--------|--------|-------------|-------|
| llama3.2 | 3B | 8GB | Rapide, CPU OK |
| mistral | 7B | 16GB | Équilibré |
| llama3.1:70b | 70B | 64GB + GPU | Meilleure qualité |

### Option 2: OpenAI (Payant)

```bash
# .env.production
AI_PROVIDER=openai
AI_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

**Coûts estimés:**
- gpt-4o-mini: ~$0.15/1M tokens (~$5-10/mois pour 50 users)
- gpt-4o: ~$2.50/1M tokens (~$50-100/mois)

### Option 3: Google Gemini (Payant + Tier gratuit)

```bash
# .env.production
AI_PROVIDER=gemini
AI_MODEL=gemini-1.5-flash
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxx
```

**Tier gratuit:** 15 requêtes/minute, 1500/jour

### Option 4: Désactivé

```bash
# .env.production
AI_PROVIDER=none
```

Classification manuelle uniquement.

---

## Scaling pour 50-100 Utilisateurs

### Augmenter les backends

```bash
# Éditer .env.production
BACKEND_REPLICAS=4
BACKEND_WORKERS=4
DB_POOL_SIZE=30
DB_MAX_OVERFLOW=50

# Appliquer
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

### Ressources recommandées par conteneur

| Service | CPU | RAM |
|---------|-----|-----|
| backend (x4) | 1 core chacun | 2GB chacun |
| frontend | 0.5 core | 512MB |
| nginx | 0.5 core | 256MB |
| postgres | 2 cores | 4GB |
| redis | 0.5 core | 1GB |
| ollama | 2+ cores (ou GPU) | 8-32GB |

---

## SSL/HTTPS (Production)

### Option A: Let's Encrypt (Gratuit)

```bash
# Installer certbot
sudo apt install certbot

# Obtenir certificat
sudo certbot certonly --standalone -d synapse.votredomaine.com

# Copier certificats
sudo cp /etc/letsencrypt/live/synapse.votredomaine.com/fullchain.pem ./nginx/ssl/
sudo cp /etc/letsencrypt/live/synapse.votredomaine.com/privkey.pem ./nginx/ssl/
```

Puis décommenter la section HTTPS dans `nginx/nginx.prod.conf`.

### Option B: Certificat auto-signé (Dev/Interne)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/privkey.pem \
    -out nginx/ssl/fullchain.pem \
    -subj "/CN=synapse.local"
```

---

## Monitoring

### Logs

```bash
# Tous les logs
docker compose -f docker-compose.prod.yml logs -f

# Backend uniquement
docker compose -f docker-compose.prod.yml logs -f backend

# Nginx (requêtes)
docker logs synapse-nginx -f
```

### Métriques

```bash
# Utilisation CPU/RAM
docker stats

# Connexions DB
docker exec forge-postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
```

### Health Checks

```bash
# Backend
curl http://localhost/health

# Nginx
curl http://localhost/nginx-health

# AI
curl http://localhost/api/v1/ai/health
```

---

## Backup

### Base de données

```bash
# Backup
docker exec forge-postgres pg_dump -U postgres synapse > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20241128.sql | docker exec -i forge-postgres psql -U postgres synapse
```

### Volumes Docker

```bash
# Liste des volumes
docker volume ls | grep synapse

# Backup volume Ollama (modèles AI)
docker run --rm -v synapse-ollama-models:/data -v $(pwd):/backup alpine tar cvf /backup/ollama-models.tar /data
```

---

## Mise à jour

```bash
# Arrêter
docker compose -f docker-compose.prod.yml down

# Mettre à jour le code
git pull origin main

# Reconstruire
docker compose -f docker-compose.prod.yml build --no-cache

# Redémarrer
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

---

## Dépannage

### Backend ne démarre pas

```bash
# Vérifier les logs
docker logs synapse-backend 2>&1 | tail -50

# Cause commune: PostgreSQL pas prêt
docker exec forge-postgres pg_isready -U postgres
```

### Ollama lent

```bash
# Vérifier si GPU est utilisé
docker exec synapse-ollama ollama ps

# Si CPU uniquement, utiliser un modèle plus petit
docker exec synapse-ollama ollama pull llama3.2:1b
```

### Erreurs 502 Bad Gateway

```bash
# Vérifier que les backends tournent
docker compose -f docker-compose.prod.yml ps

# Vérifier les connexions
docker exec synapse-nginx nginx -t
```

---

## Support

- **Documentation:** CLAUDE.md
- **Issues:** GitHub Issues
- **Logs détaillés:** Grafana sur port 3000 (si configuré)
