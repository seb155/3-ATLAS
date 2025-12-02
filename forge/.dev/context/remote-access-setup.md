# Remote Access Hub Setup - FORGE

> **Date:** 2025-12-01
> **Status:** Services running, testing in progress
> **Owner:** seb

## Overview

Configuration d'un hub d'accès distant sécurisé dans FORGE:
- **Sshwifty** - SSH WebUI (terminal dans navigateur)
- **RustDesk** - Remote desktop self-hosted (alternative TeamViewer)

## Services Déployés

| Service | Container | Port | Status |
|---------|-----------|------|--------|
| Sshwifty | forge-sshwifty | 3053 | Running |
| RustDesk hbbs | forge-rustdesk-hbbs | 21115-21116, 21118 | Running |
| RustDesk hbbr | forge-rustdesk-hbbr | 21117, 21119 | Running |

## Clé Publique RustDesk

```
tqzTJWscv4QGG8S0I3PAcavQmqJpgOtftoPJs88Ky6Q=
```

**Pour configurer un client RustDesk:**
1. Ouvrir RustDesk client
2. Settings > Network > ID/Relay Server
3. ID Server: `<ton-ip>:21116` ou `rustdesk.axoiq.com`
4. Relay Server: `<ton-ip>:21117`
5. Key: `tqzTJWscv4QGG8S0I3PAcavQmqJpgOtftoPJs88Ky6Q=`

## Fichiers Créés

| Fichier | Description |
|---------|-------------|
| `forge/docker-compose.remote-access.yml` | Docker Compose pour Sshwifty + RustDesk |
| `forge/config/sshwifty/sshwifty.conf.json` | Config Sshwifty avec presets SSH |
| `forge/.env` | Variables ajoutées: SSHWIFTY_SHARED_KEY, RUSTDESK_RELAY |
| `.dev/infra/registry.yml` | Ports 3053, 21115-21119 ajoutés |
| `.dev/infra/homelab-inventory.yml` | Inventaire infrastructure homelab |

## Commandes

### Démarrer les services

```bash
cd /home/seb/projects/AXIOM/forge
docker compose -f docker-compose.yml -f docker-compose.remote-access.yml up -d
```

### Vérifier l'état

```bash
docker ps --filter "name=forge-rustdesk" --filter "name=forge-sshwifty"
```

### Logs

```bash
docker logs forge-sshwifty -f
docker logs forge-rustdesk-hbbs -f
docker logs forge-rustdesk-hbbr -f
```

### Récupérer la clé RustDesk

```bash
docker cp forge-rustdesk-hbbs:/root/id_ed25519.pub /tmp/rustdesk_key.pub && cat /tmp/rustdesk_key.pub
```

## URLs (à configurer dans Traefik/DNS)

| Service | URL | Status |
|---------|-----|--------|
| Sshwifty | https://ssh.axoiq.com | Needs DNS |
| RustDesk WS | https://rustdesk-ws.axoiq.com | Needs DNS |

**Note:** Sshwifty refuse les connexions localhost - il faut accéder via le hostname configuré (`ssh.axoiq.com`).

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FORGE Docker                            │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Sshwifty   │  │ RustDesk    │  │ RustDesk    │             │
│  │  :3053      │  │ hbbs        │  │ hbbr        │             │
│  │  SSH WebUI  │  │ :21115-21118│  │ :21117,21119│             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│         │                │                │                     │
│         └────────────────┴────────────────┘                     │
│                          │                                      │
│                    forge-network                                │
│                          │                                      │
│                    ┌──────────┐                                 │
│                    │ Traefik  │                                 │
│                    │ :80/:443 │                                 │
│                    └──────────┘                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Découvertes Infrastructure Homelab

Pendant l'exploration SSH, on a découvert:

### Clarification importante

- `pihole01.home.s-gagnon.com` = **NPM** (Nginx Proxy Manager), pas Pi-hole!
- `pihole02.home.s-gagnon.com` = **NPM** (backup)
- Pi-hole original (192.168.1.10) = **N'existe plus**

### IPs découvertes

| Service | IP | Port |
|---------|-----|------|
| Proxmox PVE1 | 192.168.1.20 | 8006 |
| NPM (VIP) | 192.168.5.20 | 81 |
| Vaultwarden | 192.168.1.123 | 8000 |
| TrueNAS | 192.168.1.59 | 443 |
| Homepage | 192.168.10.10 | 3000 |

### SSH configuré

```bash
# Ces hosts sont accessibles en SSH passwordless
ssh root@pihole01.home.s-gagnon.com  # NPM1
ssh root@pihole02.home.s-gagnon.com  # NPM2
```

## Problème connu

**Sshwifty 403 Forbidden sur localhost:**
- Sshwifty n'accepte que les requêtes vers le hostname configuré (`ssh.axoiq.com`)
- Solution: Configurer DNS ou modifier `sshwifty.conf.json` pour ajouter `localhost`

## Prochaines étapes

1. [ ] Configurer DNS pour `ssh.axoiq.com` et `rustdesk-ws.axoiq.com`
2. [ ] Tester Sshwifty via le bon hostname
3. [ ] Tester client RustDesk avec la clé publique
4. [ ] Configurer Sunshine sur PC gaming (optionnel)

## Contexte pour reprise

**Session précédente:** VS Code setup terminé (code-server sur port 3050)

**Cette session:**
1. Exploration infrastructure via SSH vers NPM containers
2. Découverte que "pihole" = NPM, pas Pi-hole
3. Création Remote Access Hub (Sshwifty + RustDesk)
4. Services running, clé RustDesk générée

**Pour continuer:**
```bash
# Vérifier services
docker ps | grep -E "sshwifty|rustdesk"

# Lire ce fichier
cat forge/.dev/context/remote-access-setup.md
```
