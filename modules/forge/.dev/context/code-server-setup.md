# code-server Setup - VS Code WebUI for ATLAS

> **Status:** En cours de configuration
> **Date:** 2025-12-01
> **Owner:** seb

## Overview

Configuration d'un environnement VS Code hybride pour ATLAS:
- **VS Code Windows** natif avec templates ATLAS
- **code-server WebUI** dans FORGE Docker
- **Docker-in-Docker** sécurisé avec Sysbox
- **Multi-utilisateurs** isolés (1 container/user)
- **Accès externe** gratuit: Cloudflare Tunnel + Tailscale

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ACCÈS EXTERNE                               │
├──────────────────────────┬──────────────────────────────────────────┤
│  Tailscale (E2E)         │  Cloudflare Tunnel (Web)                 │
│  code.tail.net           │  code.axoiq.com                          │
│  - WireGuard encryption  │  - OAuth/2FA via Cloudflare Access       │
│  - P2P, low latency      │  - Sans client (navigateur)              │
│  - Gratuit 3 users       │  - Gratuit 50 users                      │
└──────────────────────────┴──────────────────────────────────────────┘
                                    │
                            Pi-hole DNS
                     (pihole1 / pihole2 - HA)
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         TRAEFIK (Reverse Proxy)                     │
│  *.axoiq.com SSL wildcard + routing                                 │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │ code-seb     │ │ code-user1   │ │ code-user2   │
            │ Port: 3050   │ │ Port: 3051   │ │ Port: 3052   │
            │ Sysbox DinD  │ │ Sysbox DinD  │ │ Sysbox DinD  │
            └──────────────┘ └──────────────┘ └──────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │   forge-network     │
                         │ postgres, redis...  │
                         └─────────────────────┘
```

## Composants

### 1. code-server Docker

| Fichier | Description |
|---------|-------------|
| `docker-compose.code-server.yml` | Service Docker multi-user |
| Port principal | 3050 (seb), 3051-3059 réservés |
| Image | `lscr.io/linuxserver/code-server:latest` |
| Runtime | Sysbox (Docker-in-Docker sécurisé) |

### 2. DNS (Pi-hole)

| Entrée | Valeur | Pi-hole |
|--------|--------|---------|
| `code.axoiq.com` | IP WSL2 (ex: 172.x.x.x) | pihole1, pihole2 |
| `code-user1.axoiq.com` | IP WSL2 | pihole1, pihole2 |

**Pour obtenir l'IP WSL2:**
```bash
hostname -I | awk '{print $1}'
```

### 3. Accès Externe

| Service | Plan | Coût | Usage |
|---------|------|------|-------|
| **Tailscale** | Personal | Gratuit | Dev quotidien, E2E encryption |
| **Cloudflare** | Zero Trust Free | Gratuit | Accès web sans client |

## Installation

### Étape 1: Installer Sysbox sur WSL2

```bash
# Télécharger Sysbox CE (gratuit)
wget https://downloads.nestybox.com/sysbox/releases/v0.6.4/sysbox-ce_0.6.4-0.linux_amd64.deb
sudo dpkg -i sysbox-ce_0.6.4-0.linux_amd64.deb
sudo systemctl start sysbox

# Configurer Docker pour Sysbox
sudo tee -a /etc/docker/daemon.json << 'EOF'
{
  "runtimes": {
    "sysbox-runc": {
      "path": "/usr/bin/sysbox-runc"
    }
  }
}
EOF
sudo systemctl restart docker

# Vérifier
docker info | grep -i sysbox
```

### Étape 2: Configurer Pi-hole DNS

1. Accéder à Pi-hole Admin: `http://pihole1/admin` ou `http://pihole2/admin`
2. Aller dans **Local DNS > DNS Records**
3. Ajouter:
   - Domain: `code.axoiq.com`
   - IP: `<IP WSL2>` (obtenir avec `hostname -I`)
4. Répéter sur pihole2 pour la haute disponibilité

### Étape 3: Configurer le mot de passe

```bash
# Dans forge/.env, ajouter:
CODE_SERVER_PASSWORD_SEB=<mot-de-passe-fort>
```

### Étape 4: Démarrer code-server

```bash
cd /home/seb/projects/AXIOM/forge

# Avec infrastructure complète
docker compose -f docker-compose.yml -f docker-compose.traefik.yml -f docker-compose.code-server.yml up -d

# Vérifier
docker logs forge-code-seb -f
```

### Étape 5: Accéder

- **Local:** https://code.axoiq.com
- **Dev:** http://code.localhost
- **Direct:** http://localhost:3050

## Configuration Tailscale

```bash
# Installer sur WSL2
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Accès via Tailscale: https://<hostname>:3050
```

## Configuration Cloudflare Tunnel

Si tu utilises déjà Cloudflare Tunnel, ajouter dans la config cloudflared:

```yaml
ingress:
  - hostname: code.axoiq.com
    service: http://forge-code-seb:8443
  # ... autres services
  - service: http_status:404
```

## Ajouter un utilisateur

1. Créer le répertoire utilisateur:
   ```bash
   sudo useradd -m -u 1001 user1
   sudo mkdir -p /home/user1/projects
   sudo chown 1001:1001 /home/user1/projects
   ```

2. Décommenter la section `code-user1` dans `docker-compose.code-server.yml`

3. Ajouter le mot de passe dans `.env`:
   ```
   CODE_SERVER_PASSWORD_USER1=<mot-de-passe>
   ```

4. Ajouter DNS dans Pi-hole: `code-user1.axoiq.com`

5. Redémarrer:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.code-server.yml up -d
   ```

## Dépannage

### Sysbox non disponible

Si Sysbox n'est pas installé, modifier `docker-compose.code-server.yml`:

```yaml
services:
  code-seb:
    # Commenter cette ligne:
    # runtime: sysbox-runc
    # Ajouter à la place:
    privileged: true
```

### Problème de permissions

```bash
# Vérifier PUID/PGID
id seb  # Doit retourner uid=1000(seb) gid=1000(seb)

# Corriger les permissions
sudo chown -R 1000:1000 /home/seb/projects
```

### Container ne démarre pas

```bash
# Logs détaillés
docker logs forge-code-seb

# Vérifier le réseau
docker network inspect forge-network | grep code
```

## Fichiers liés

| Fichier | Description |
|---------|-------------|
| `forge/docker-compose.code-server.yml` | Service Docker |
| `forge/config/traefik/dynamic.yml` | Routes Traefik |
| `forge/.env` | Mots de passe |
| `.dev/infra/registry.yml` | Ports alloués |
| `.claude/templates/vscode/` | Templates VS Code |

## Ports alloués

| Port | Service | Description |
|------|---------|-------------|
| 3050 | code-seb | Instance principale |
| 3051 | code-user1 | Réservé |
| 3052 | code-user2 | Réservé |
| 3053-3059 | - | Disponibles |

## Coûts

| Service | Plan | Coût mensuel |
|---------|------|--------------|
| Sysbox CE | Community | **$0** |
| code-server | Open Source | **$0** |
| Tailscale | Personal (3 users) | **$0** |
| Cloudflare ZT | Free (50 users) | **$0** |
| **Total** | | **$0/mois** |

## État de l'implémentation

### Fait (AI)
- [x] `docker-compose.code-server.yml` créé
- [x] Routes Traefik ajoutées (`dynamic.yml`)
- [x] Ports enregistrés (`registry.yml`: 3050-3052)
- [x] Password configuré (`.env`)
- [x] Templates VS Code créés (`.claude/templates/vscode/`)
- [x] Commande `/1-init-vscode` créée
- [x] Documentation complète

### À faire (Manuel)
- [ ] Installer Sysbox sur WSL2
- [ ] Configurer Pi-hole DNS (`code.axoiq.com` → IP Tailscale laptop)
- [ ] Configurer Tailscale DNS override
- [ ] Changer le password dans `.env`
- [ ] (Optionnel) Configurer Cloudflare Access (2FA)
- [ ] Tester code-server

## Références

- [LinuxServer code-server](https://docs.linuxserver.io/images/docker-code-server/)
- [Sysbox GitHub](https://github.com/nestybox/sysbox)
- [Tailscale](https://tailscale.com/kb/installation)
- [Cloudflare Zero Trust](https://developers.cloudflare.com/cloudflare-one/)
