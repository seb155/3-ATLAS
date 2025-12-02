# Checkpoint: Remote Access Hub Setup

> **Date:** 2025-12-01 21:15
> **Session:** Remote Access Hub (Sshwifty + RustDesk)
> **Status:** Services running, need DNS config

---

## Session Summary

Création d'un hub d'accès distant dans FORGE:
- **Sshwifty** running sur port 3053 (SSH WebUI)
- **RustDesk** running sur ports 21115-21119 (remote desktop)
- Clé publique RustDesk générée
- Exploration infrastructure homelab via SSH

---

## Completed Tasks

| Task | Status | Details |
|------|--------|---------|
| SSH keys vers NPM containers | ✅ | root@pihole01/02.home.s-gagnon.com |
| docker-compose.remote-access.yml | ✅ | Sshwifty + RustDesk hbbs/hbbr |
| Config Sshwifty | ✅ | Presets pour NPM1, NPM2, PVE1 |
| Registry.yml update | ✅ | Ports 3053, 21115-21119 |
| Services started | ✅ | 3 containers running |
| Clé RustDesk | ✅ | `tqzTJWscv4QGG8S0I3PAcavQmqJpgOtftoPJs88Ky6Q=` |
| Homelab inventory | ✅ | `.dev/infra/homelab-inventory.yml` |

## Pending Tasks

- [ ] Configurer DNS pour ssh.axoiq.com
- [ ] Tester Sshwifty via hostname (pas localhost)
- [ ] Tester client RustDesk
- [ ] (Optionnel) Sunshine pour gaming

---

## Key Files Created

```
forge/docker-compose.remote-access.yml      # Services Docker
forge/config/sshwifty/sshwifty.conf.json   # Config Sshwifty
forge/.env                                  # Variables ajoutées
forge/.dev/context/remote-access-setup.md   # Documentation complète
.dev/infra/registry.yml                     # Ports ajoutés
.dev/infra/homelab-inventory.yml            # Inventaire homelab
```

---

## Important Discoveries

### "Pi-hole" = Nginx Proxy Manager!

- `pihole01.home.s-gagnon.com` → NPM container (pas Pi-hole)
- `pihole02.home.s-gagnon.com` → NPM container (pas Pi-hole)
- Pi-hole original (192.168.1.10) → **N'existe plus**

### Homelab IPs

| Service | IP |
|---------|-----|
| PVE1 | 192.168.1.20 |
| NPM | 192.168.5.20 |
| Vaultwarden | 192.168.1.123 |
| TrueNAS | 192.168.1.59 |

---

## RustDesk Configuration

**Clé publique:**
```
tqzTJWscv4QGG8S0I3PAcavQmqJpgOtftoPJs88Ky6Q=
```

**Pour client RustDesk:**
- ID Server: `<ip>:21116`
- Relay Server: `<ip>:21117`
- Key: (ci-dessus)

---

## Recovery Commands

```bash
# Vérifier services
cd /home/seb/projects/AXIOM/forge
docker ps | grep -E "sshwifty|rustdesk"

# Redémarrer si nécessaire
docker compose -f docker-compose.yml -f docker-compose.remote-access.yml up -d

# Logs
docker logs forge-sshwifty -f
docker logs forge-rustdesk-hbbs -f
```

---

## Known Issue

**Sshwifty 403 sur localhost:**
- Sshwifty vérifie le hostname de la requête
- Refuse si != `ssh.axoiq.com` (configuré)
- Solution: accéder via DNS ou modifier config

---

## Next Session

1. Lire: `forge/.dev/context/remote-access-setup.md`
2. Configurer DNS pour `ssh.axoiq.com` → IP laptop
3. Tester Sshwifty via navigateur
4. Tester RustDesk client
