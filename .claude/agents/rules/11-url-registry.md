# Règle 11: URL Registry - Gestion Centralisée des Adresses

**Status:** OBLIGATOIRE
**Dernière mise à jour:** 2025-11-29
**Scope:** Tous les agents AI

---

## PRINCIPE FONDAMENTAL

**Il existe UNE SEULE source de vérité pour toutes les URLs, domaines et ports:**

```
D:\Projects\AXIOM\.dev\infra\url-registry.yml
```

**TOUS les agents DOIVENT consulter ce fichier AVANT:**
- Proposer une nouvelle URL
- Allouer un port
- Créer un nouveau service
- Modifier une configuration réseau

---

## Responsabilités des Agents

### Tous les Agents

1. **TOUJOURS lire le registre** avant toute opération sur URLs/ports
2. **NE JAMAIS deviner** ou assumer qu'une URL est disponible
3. **NE JAMAIS utiliser localhost:PORT** dans la documentation destinée aux utilisateurs
4. **TOUJOURS référencer** le registre dans les plans et recommandations

### DevOps Manager (Responsabilité Spéciale)

Le **DevOps Manager** est l'autorité finale pour:
- Allocation de nouveaux ports
- Validation des configurations Traefik
- Mise à jour du registre après validation utilisateur
- Diagnostic des problèmes de routing

**Voir:** `.claude/agents/devops-manager.md` section "URL and Domain Management"

---

## Structure du Registre

Le fichier `url-registry.yml` contient:

### Sections Principales

1. **axiom_applications** - Applications core (SYNAPSE, NEXUS, CORTEX, etc.)
2. **forge_infrastructure** - Services infrastructure (Grafana, Traefik, etc.)
3. **personal_projects** - Projets personnels (FinDash, Pulse, etc.)
4. **testing_qa** - Services de test (ReportPortal, Allure, etc.)
5. **allocation_policy** - Règles d'allocation et conventions

### Exemple d'Entrée

```yaml
axiom_applications:
  synapse:
    name: "SYNAPSE"
    description: "MBSE Platform"
    frontend:
      url: "https://synapse.axoiq.com"
      port: 4000
    backend:
      url: "https://api.axoiq.com"
      port: 8001
    status: "active"
    traefik_enabled: true
    range: "4000-4999"
```

---

## Conventions de Nommage

### Format de Domaine

**TOUJOURS utiliser:**
```
{app-name}.axoiq.com
```

**Exemples valides:**
- `synapse.axoiq.com`
- `nexus.axoiq.com`
- `findash.axoiq.com`
- `prism.axoiq.com`

**Exemples INVALIDES:**
- ❌ `my-app.local`
- ❌ `test.localhost`
- ❌ `app.example.com`
- ❌ `localhost:5173`

### Format d'URL API

Pour les applications avec frontend + backend séparés:

- **Frontend:** `https://{app}.axoiq.com`
- **Backend:** `https://api-{app}.axoiq.com` OU `https://api.axoiq.com` (pour app principale)

**Exemples:**
- NEXUS: `nexus.axoiq.com` + `api-nexus.axoiq.com`
- SYNAPSE: `synapse.axoiq.com` + `api.axoiq.com` (app principale)

---

## Ranges de Ports

### Allocation par Application

| Application | Range | Ports Alloués | Disponibles |
|-------------|-------|---------------|-------------|
| **FORGE** | 3000-3999 | ~10 | ~990 |
| **SYNAPSE** | 4000-4999 | 2 | 998 |
| **NEXUS** | 5000-5999 | 2 | 998 |
| **PRISM** | 6000-6999 | 0 | 1000 |
| **ATLAS** | 7000-7999 | 0 | 1000 |

**Règle:** Chaque application a un range dédié de 1000 ports. Pas de chevauchement autorisé.

### Ports Réservés FORGE

Les ports suivants sont réservés pour FORGE infrastructure:

```
3000  - Grafana
3080  - Wiki (Docsify)
3100  - Loki
5050  - pgAdmin
5433  - PostgreSQL (port externe)
5555  - Prisma Studio
6379  - Redis
7700  - MeiliSearch
8888  - Traefik Dashboard
```

---

## Processus d'Allocation - Guide Étape par Étape

### Étape 1: Lecture du Registre

```
Read: D:\Projects\AXIOM\.dev\infra\url-registry.yml
```

Analyser:
- Ports disponibles dans le range approprié
- URLs déjà allouées
- Conventions utilisées

### Étape 2: Proposition

Créer une proposition incluant:

```markdown
**Nouvelle allocation proposée:**

- Nom: {APPLICATION_NAME}
- Description: {BRIEF_DESCRIPTION}
- Domaine: {app-name}.axoiq.com
- Port(s): {PORT_NUMBER(S)}
- Range: {APPLICATION}-{RANGE}
- Traefik: Oui/Non
```

### Étape 3: Validation Utilisateur

**OBLIGATOIRE:** Utiliser `AskUserQuestion` pour valider:

```typescript
AskUserQuestion({
  questions: [{
    question: "Approuvez-vous cette allocation d'URL ?",
    header: "URL Allocation",
    multiSelect: false,
    options: [
      {
        label: "Approuver",
        description: "Domaine: {app}.axoiq.com, Port: {port}"
      },
      {
        label: "Modifier",
        description: "Proposer un autre domaine/port"
      }
    ]
  }]
})
```

### Étape 4: Mise à Jour du Registre

Après validation, mettre à jour `url-registry.yml`:

```yaml
{app_section}:
  {app_name}:
    name: "{DISPLAY_NAME}"
    description: "{DESCRIPTION}"
    url: "https://{app-name}.axoiq.com"
    port: {PORT}
    status: "planned" | "development" | "active"
    traefik_enabled: true | false
    range: "{RANGE}"
```

### Étape 5: Mise à Jour des Fichiers Associés

Dans cet ordre:

1. **url-registry.yml** ✅ (déjà fait à l'étape 4)
2. **hosts-entries.txt** - Ajouter `127.0.0.1 {app-name}.axoiq.com`
3. **10-traefik-routing.md** - Ajouter à la table des URLs
4. **QUICK-REFERENCE-URLS.md** - Ajouter à la section appropriée

### Étape 6: Configuration Traefik (si applicable)

Si `traefik_enabled: true`, créer/mettre à jour:

```yaml
# apps/{app}/docker-compose.traefik-labels.yml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.{app}.rule=Host(`{app-name}.axoiq.com`)"
  - "traefik.http.routers.{app}.entrypoints=websecure"
  - "traefik.http.routers.{app}.tls.certresolver=letsencrypt"
  - "traefik.http.services.{app}.loadbalancer.server.port={PORT}"
```

### Étape 7: Instructions Utilisateur

Informer l'utilisateur des actions manuelles requises:

```markdown
**Actions manuelles requises:**

1. Mettre à jour le fichier hosts (admin requis):
   - Ouvrir PowerShell en tant qu'Administrateur
   - Exécuter: `notepad C:\Windows\System32\drivers\etc\hosts`
   - Ajouter: `127.0.0.1 {app-name}.axoiq.com`

2. Flusher le cache DNS:
   ```powershell
   ipconfig /flushdns
   ```

3. Vérifier la résolution:
   ```powershell
   ping {app-name}.axoiq.com
   ```

4. Démarrer les services:
   ```powershell
   # FORGE (si pas déjà démarré)
   cd D:\Projects\AXIOM\forge
   docker compose -f docker-compose.yml -f docker-compose.traefik.yml up -d

   # Application
   cd {APP_PATH}
   docker compose -f docker-compose.dev.yml -f docker-compose.traefik-labels.yml up -d
   ```
```

---

## Skill de Validation

Avant toute allocation, utiliser le skill dédié:

```
skill: "zz-url-check"
```

**Ce skill fournit:**
- Liste des ports disponibles dans un range
- Vérification de conflit de domaine
- Validation de la convention de nommage
- Suggestion de port optimal

---

## Cas d'Usage Courants

### Cas 1: Nouvelle Application AXIOM

**Scénario:** Créer PRISM (Enterprise Dashboard)

```markdown
1. Read: url-registry.yml
2. Identifier range: PRISM = 6000-6999
3. Choisir port: 6000 (premier port du range)
4. Domaine: prism.axoiq.com
5. Valider avec utilisateur
6. Mettre à jour registre
7. Configurer Traefik labels
8. Informer utilisateur
```

### Cas 2: Projet Personnel

**Scénario:** Ajouter Pulse (Homelab Monitor)

```markdown
1. Read: url-registry.yml
2. Section: personal_projects
3. Choisir port libre (ex: 6500)
4. Domaine: pulse.axoiq.com
5. Valider avec utilisateur
6. Mettre à jour registre
7. Pas de Traefik si standalone
8. Informer utilisateur
```

### Cas 3: Service Infrastructure

**Scénario:** Ajouter Portainer (Docker GUI)

```markdown
1. Read: url-registry.yml
2. Section: forge_infrastructure
3. Vérifier ports FORGE disponibles (3000-3999)
4. Domaine: portainer.axoiq.com
5. Port: Utiliser port par défaut Portainer (9000) OU choisir dans range
6. Valider avec utilisateur
7. Mettre à jour registre
8. Configurer Traefik
9. Informer utilisateur
```

---

## Diagnostic de Problèmes

### Port Déjà Utilisé

**Symptôme:** `bind: address already in use`

**Solution:**
1. Read: url-registry.yml
2. Vérifier quel service utilise le port
3. Choisir un port différent dans le range
4. Mettre à jour la proposition

### Domaine Ne Résout Pas

**Symptôme:** `Could not resolve host`

**Diagnostic:**
1. Vérifier fichier hosts: `type C:\Windows\System32\drivers\etc\hosts`
2. Vérifier DNS cache: `ipconfig /displaydns`
3. Flusher cache: `ipconfig /flushdns`
4. Tester: `ping {app-name}.axoiq.com`

### Traefik 502 Bad Gateway

**Symptôme:** Erreur 502 via Traefik

**Diagnostic:**
1. Vérifier container actif: `docker ps | findstr {app}`
2. Vérifier network: `docker inspect {container} | findstr forge-network`
3. Vérifier labels Traefik: `docker inspect {container} | findstr traefik`
4. Consulter logs: `docker logs forge-traefik --tail 50`

---

## Références

### Fichiers Clés

| Fichier | Rôle |
|---------|------|
| **url-registry.yml** | Source de vérité (AUTHORITATIVE) |
| **QUICK-REFERENCE-URLS.md** | Vue d'ensemble rapide |
| **hosts-entries.txt** | Template pour fichier hosts Windows |
| **10-traefik-routing.md** | Règle routing Traefik |
| **devops-manager.md** | Agent responsable URL management |

### Skills Associés

- **zz-url-check** - Validation d'allocation
- **zz-infra** - Status infrastructure

### Agents Responsables

- **DevOps Manager** - Autorité finale sur allocations
- **All Agents** - Lecture obligatoire du registre

---

## Changelog

| Date | Change |
|------|--------|
| 2025-11-29 | Création de la règle 11 - URL Registry |
| 2025-11-29 | Définition du processus d'allocation |
| 2025-11-29 | Ajout des conventions et cas d'usage |

---

**RAPPEL IMPORTANT:**

```
AVANT toute opération sur URLs/ports/domaines:
→ Read: D:\Projects\AXIOM\.dev\infra\url-registry.yml
```

**Pas d'exception à cette règle.**
