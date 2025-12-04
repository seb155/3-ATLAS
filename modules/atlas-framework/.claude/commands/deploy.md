# Deploy Application

Deploy an application to forge (dev) or homelab (prod) environment.

## Arguments

- `$ARGUMENTS` - Format: `<app> <env>`
  - `app`: Application name (findash, nexus, echo, synapse, mechvision)
  - `env`: Target environment (forge, homelab)

## Instructions

Execute the deployment using the deploy-app.sh script:

```bash
.claude/scripts/deploy-app.sh $ARGUMENTS
```

### Environment Details

**FORGE (Dev)**
- Local Docker on Laptop WSL
- Network: forge-network
- Domain: *.axoiq.com

**HOMELAB (Prod)**
- Remote Docker VM at 192.168.10.55
- Deploys via SSH + rsync
- Domain: *.s-gagnon.com

### Examples

```
/deploy findash forge     # Deploy FinDash to local Docker
/deploy findash homelab   # Deploy FinDash to Homelab
/deploy nexus forge       # Deploy Nexus to local Docker
```

### Troubleshooting

If homelab deployment fails:
1. Check SSH connectivity: `ssh docker@192.168.10.55`
2. Ensure Tailscale/VPN is connected if remote
3. Verify the app has a docker-compose.yml

### Reference

- URL Registry: `.dev/infra/url-registry.yml`
- Infrastructure Doc: `.claude/docs/infrastructure.md`
