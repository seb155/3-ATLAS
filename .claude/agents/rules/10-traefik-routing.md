<!-- 🔒 PROTECTED: Infrastructure rule - DO NOT MODIFY WITHOUT OWNER VALIDATION -->

# Règle 10: Routage Traefik Obligatoire

**Status:** OBLIGATOIRE
**Dernière mise à jour:** 2025-11-30

---

## RÈGLE ABSOLUE

**TOUTES les applications AXIOM DOIVENT être accédées via Traefik avec des noms de domaine.**

**INTERDIT:**
- Accéder via `localhost:PORT`
- Démarrer sans les labels Traefik
- Modifier les ports dans les docker-compose

---

## URLs Officielles (SEULES VALIDES)

**⚠️ SOURCE DE VÉRITÉ:** `.dev/infra/url-registry.yml`

Consultez toujours le registre central pour les URLs à jour. Cette section est un résumé.

### Applications AXIOM

| App | URL Frontend | URL API | Statut |
|-----|--------------|---------|--------|
| **SYNAPSE** | `https://synapse.axoiq.com` | `https://api.axoiq.com` | ✅ Active |
| **NEXUS** | `https://nexus.axoiq.com` | `https://api-nexus.axoiq.com` | ✅ Active |
| **CORTEX** | - | `https://cortex.axoiq.com` | 🚧 Dev |
| **APEX** | `https://apex.axoiq.com` | - | 📋 Planned |
| **ATLAS** | - | - | ✅ Active (AI OS) |

### Infrastructure FORGE

| Service | URL |
|---------|-----|
| **Traefik Dashboard** | `https://traefik.axoiq.com` ou `http://localhost:8888` |
| **Grafana** | `https://grafana.axoiq.com` |
| **pgAdmin** | `https://pgadmin.axoiq.com` |
| **Prisma Studio** | `https://prisma.axoiq.com` |
| **Loki** | `https://loki.axoiq.com` |
| **Wiki (Docsify)** | `https://wiki.axoiq.com` |
| **Portainer** | `https://portainer.axoiq.com` (planned) |

### Projets Personnels

| App | URL |
|-----|-----|
| **FinDash** | `https://findash.axoiq.com` |
| **Pulse** | `https://pulse.axoiq.com` |
| **Trilium** | `https://trilium.axoiq.com` |
| **Neo4j** | `https://neo4j.axoiq.com` |
| **Homelab** | `https://homelab.axoiq.com` |

---

## Comment Démarrer les Apps (SEULE MÉTHODE VALIDE)

### 1. FORGE (Infrastructure) - Toujours en premier

```powershell
cd D:\Projects\AXIOM\forge
docker compose -f docker-compose.yml -f docker-compose.traefik.yml up -d
```

### 2. SYNAPSE

```powershell
cd D:\Projects\AXIOM\apps\synapse
docker compose -f docker-compose.dev.yml -f docker-compose.traefik-labels.yml up -d
```

### 3. NEXUS

```powershell
cd D:\Projects\AXIOM\apps\nexus
docker compose -f docker-compose.dev.yml -f docker-compose.traefik-labels.yml up -d
```

### 4. CORTEX

```powershell
cd D:\Projects\AXIOM\apps\cortex
docker compose -f docker-compose.dev.yml -f docker-compose.traefik-labels.yml up -d
```

---

## Configuration Requise

### Fichier Hosts (Windows)

**Fichier:** `C:\Windows\System32\drivers\etc\hosts`

**Entrées obligatoires:**
```
# AXIOM Core
127.0.0.1 synapse.axoiq.com
127.0.0.1 api.axoiq.com
127.0.0.1 nexus.axoiq.com
127.0.0.1 api-nexus.axoiq.com
127.0.0.1 cortex.axoiq.com

# FORGE Infrastructure
127.0.0.1 traefik.axoiq.com
127.0.0.1 grafana.axoiq.com
127.0.0.1 pgadmin.axoiq.com
127.0.0.1 prisma.axoiq.com
127.0.0.1 loki.axoiq.com

# Projets Personnels
127.0.0.1 findash.axoiq.com
127.0.0.1 pulse.axoiq.com
127.0.0.1 trilium.axoiq.com
127.0.0.1 neo4j.axoiq.com
127.0.0.1 graph.axoiq.com
```

**Source:** `.dev/infra/hosts-entries.txt`

---

## Fichiers de Configuration Traefik

| Fichier | Rôle |
|---------|------|
| `forge/docker-compose.traefik.yml` | Définition du service Traefik |
| `forge/config/traefik/dynamic.yml` | Routes et services (file provider) |
| `forge/config/traefik/certificates.yml` | Certificats SSL |
| `apps/*/docker-compose.traefik-labels.yml` | Labels par application |

---

## Diagnostic

### Vérifier que Traefik fonctionne

```powershell
# Status
docker ps | findstr traefik

# Logs
docker logs forge-traefik --tail 50

# Dashboard
# Ouvrir http://localhost:8888
```

### Vérifier le routage

```powershell
# Test SYNAPSE
curl -k https://synapse.axoiq.com

# Test NEXUS
curl -k https://nexus.axoiq.com

# Test API
curl -k https://api-nexus.axoiq.com/api/v1/health
```

---

## Erreurs Courantes

### 502 Bad Gateway

**Cause:** Container non trouvé par Traefik

**Solutions:**
1. Vérifier que le container est sur `forge-network`
2. Vérifier le nom du container dans `dynamic.yml`
3. Redémarrer Traefik: `docker restart forge-traefik`

### Connection Refused

**Cause:** Hosts file non configuré

**Solution:** Ajouter les entrées hosts (voir ci-dessus)

### Certificate Error

**Cause:** Certificat self-signed

**Solution:** Accepter le certificat dans le navigateur ou utiliser `-k` avec curl

---

## IMPORTANT - Ne Jamais Faire

1. **NE JAMAIS** accéder via `localhost:5173`, `localhost:4000`, etc.
2. **NE JAMAIS** démarrer sans `-f docker-compose.traefik-labels.yml`
3. **NE JAMAIS** modifier les ports exposés dans docker-compose
4. **NE JAMAIS** contourner Traefik pour le développement

**Raison:** Garantir la cohérence entre dev et prod, éviter les conflits de ports.

---

## Comment Demander une Nouvelle Adresse

### Pour les Agents AI

**AVANT de créer un nouveau service/app**, vous DEVEZ:

1. **Lire le registre central:**
   ```
   Read: D:\Projects\AXIOM\.dev\infra\url-registry.yml
   ```

2. **Vérifier le range de ports disponible** pour l'application
   - FORGE: 3000-3999
   - SYNAPSE: 4000-4999
   - NEXUS: 5000-5999
   - APEX: 6000-6999
   - CORTEX: 7000-7999

3. **Choisir un port libre** dans le range approprié

4. **Proposer un nom de domaine** suivant la convention:
   - Format: `{app-name}.axoiq.com`
   - ✅ Exemples valides: `apex.axoiq.com`, `cortex.axoiq.com`, `findash.axoiq.com`
   - ❌ Exemples invalides: `my-app.local`, `test.localhost`, `app.example.com`

5. **Créer un plan** incluant:
   - Domaine choisi
   - Port(s) requis
   - Labels Traefik nécessaires
   - Mise à jour du registre

6. **Utiliser AskUserQuestion** pour valider avec l'utilisateur

### Processus de Mise à Jour

Après validation utilisateur, mettre à jour dans cet ordre:

1. **Ajouter au registre:** `.dev/infra/url-registry.yml`
2. **Ajouter au hosts template:** `.dev/infra/hosts-entries.txt`
3. **Configurer Traefik:** Labels dans `docker-compose.traefik-labels.yml`
4. **Mettre à jour cette règle:** `10-traefik-routing.md` (section URLs)
5. **Informer l'utilisateur** des commandes manuelles à exécuter:
   - Modifier `C:\Windows\System32\drivers\etc\hosts` (admin requis)
   - Exécuter `ipconfig /flushdns`

### Validation

Avant toute allocation, utiliser le skill de validation:
```
skill: "zz-url-check"
```

Ce skill vérifie:
- Port disponible dans le range
- Domaine suit la convention
- Pas de conflit avec URLs existantes

---

## Référence Rapide

Pour une vue d'ensemble rapide de toutes les URLs:
- **Registre complet:** `.dev/infra/url-registry.yml` (SOURCE DE VÉRITÉ)
- **Quick reference:** `.dev/infra/QUICK-REFERENCE-URLS.md`
- **Règle allocation:** `.claude/agents/rules/11-url-registry.md`
