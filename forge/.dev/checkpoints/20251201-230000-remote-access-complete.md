# Checkpoint: Remote Access Hub Complete

> **Date:** 2025-12-01 23:00
> **Session:** Remote Access Hub Setup
> **Status:** Cloudflare Tunnel + Sshwifty WORKING

---

## What Works

### Cloudflare Tunnel
- Tunnel: `axiom-forge`
- Container: `forge-cloudflared`
- Token in: `forge/.env` (CLOUDFLARE_TUNNEL_TOKEN)

### Sshwifty (SSH WebUI)
- **URL:** https://ssh.axoiq.com
- **Password:** `byfSA14PgmqHZnQr2KCWyF90TrO5RQug`
- 15+ presets SSH (PVE, NPM, TrueNAS, Vaultwarden, etc.)
- Config: `forge/config/sshwifty/sshwifty.conf.json`

### Headscale VPN
- Container: `forge-headscale`
- User: seb (ID: 1)
- Node: forge-gateway (100.64.0.1) - CONNECTED
- Routes: 192.168.1.0/24, 192.168.5.0/24, 192.168.10.0/24, 192.168.30.0/24
- **Note:** External clients can't connect via CF Tunnel (WebSocket issue)

---

## What Doesn't Work

### RustDesk via Cloudflare
- 502 Bad Gateway
- Cause: UDP + WebSocket not supported by CF Tunnel
- Solution: Use locally only or port forward

### Headscale External Access
- ts2021 protocol requires WebSocket upgrade
- Cloudflare strips headers
- Workaround: Docker containers connect directly

---

## Files Created This Session

```
forge/docker-compose.cloudflared.yml    # Cloudflare Tunnel
forge/docker-compose.headscale.yml      # Headscale VPN server
forge/docker-compose.tailscale.yml      # Tailscale client (gateway)
forge/config/headscale/config.yaml      # Headscale config
```

## Files Modified

```
forge/.env                              # Added tokens
forge/config/sshwifty/sshwifty.conf.json  # SSH presets
forge/config/traefik/dynamic.yml        # Routes
```

---

## Next Session TODO

1. **Apache Guacamole** - RDP/VNC in browser
   - URL: rdp.axoiq.com
   - For: Work laptop (no install)

2. **Moonlight Web Stream** - Game streaming in browser
   - URL: play.axoiq.com
   - For: Gaming from work laptop
   - Requires: Sunshine on gaming PC

3. **Phone Access**
   - Option A: UniFi Teleport (built into UDM-SE)
   - Option B: Tailscale official (free)

---

## Quick Commands

```bash
# Start all remote access services
cd /home/seb/projects/AXIOM/forge
docker compose -f docker-compose.yml \
  -f docker-compose.cloudflared.yml \
  -f docker-compose.headscale.yml \
  -f docker-compose.tailscale.yml \
  -f docker-compose.remote-access.yml \
  up -d

# Check status
docker ps --filter "name=forge-"

# Headscale nodes
docker exec forge-headscale headscale nodes list

# New Tailscale key
docker exec forge-headscale headscale preauthkeys create --user 1 --reusable --expiration 720h
```

---

## Recovery

Pour reprendre:
```bash
/0-session-continue forge
```

Puis lire:
- Ce fichier
- `forge/.dev/context/remote-access-setup.md`
- Plan: `~/.claude/plans/giggly-gliding-popcorn.md`
