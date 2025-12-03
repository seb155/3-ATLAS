# Skill: URL Check & Validation

**Purpose:** Validate URL allocations, check port availability, and display active URLs from the central registry.

**When to use:**
- Before proposing a new service/application
- To verify a domain is not already allocated
- To find available ports in a specific range
- To display all active URLs for reference

**Model:** Sonnet (quick validation) or Haiku (simple queries)

---

## Actions

### 1. Show All Active URLs

Display a summary of all allocated URLs from the registry.

**Read:**
```
D:\Projects\AXIOM\.dev\infra\url-registry.yml
```

**Output format:**
```markdown
## Active URLs (from url-registry.yml)

### AXIOM Applications
- SYNAPSE: https://synapse.axoiq.com (Frontend) | https://api.axoiq.com (API)
- NEXUS: https://nexus.axoiq.com (Frontend) | https://api-nexus.axoiq.com (API)
- CORTEX: https://cortex.axoiq.com (API) - Status: development
- PRISM: https://prism.axoiq.com - Status: planned
- ATLAS: https://atlas.axoiq.com - Status: planned

### FORGE Infrastructure
- Traefik: https://traefik.axoiq.com (port 8888)
- Grafana: https://grafana.axoiq.com (port 3000)
- pgAdmin: https://pgadmin.axoiq.com (port 5050)
- Prisma: https://prisma.axoiq.com (port 5555)
- Loki: https://loki.axoiq.com (port 3100)
- Wiki: https://wiki.axoiq.com (port 3080)

### Personal Projects
- FinDash: https://findash.axoiq.com (port 6400)
- Pulse: https://pulse.axoiq.com - Status: planned
- Trilium: https://trilium.axoiq.com - Status: planned

**Total Active:** {count} | **Total Planned:** {count}
```

---

### 2. Check Port Availability

Verify if a port is available in a specific range.

**Input required:**
- Port number to check
- Application range (FORGE, SYNAPSE, NEXUS, PRISM, ATLAS)

**Process:**
1. Read `url-registry.yml`
2. Extract all allocated ports for the specified range
3. Check if requested port is in the range
4. Check if port is already allocated
5. Suggest next available port if requested is taken

**Output format:**
```markdown
## Port Availability Check

**Range:** {APPLICATION} ({START}-{END})
**Requested Port:** {PORT}

**Status:** ✅ Available | ❌ Already allocated to {SERVICE}

**Allocated ports in this range:**
- {PORT1}: {SERVICE1}
- {PORT2}: {SERVICE2}
...

**Next available port:** {NEXT_PORT}
**Total allocated:** {COUNT} / 1000
**Remaining:** {REMAINING} ports
```

---

### 3. Validate Domain Name

Check if a proposed domain follows conventions and is not already used.

**Input required:**
- Proposed domain name

**Validation rules:**
1. **Format:** Must be `{app-name}.axoiq.com`
2. **Characters:** Lowercase alphanumeric + hyphens only
3. **Length:** 3-30 characters (excluding `.axoiq.com`)
4. **Uniqueness:** Not already allocated

**Process:**
1. Check format matches `{app-name}.axoiq.com`
2. Validate characters (lowercase, alphanumeric, hyphens)
3. Read `url-registry.yml`
4. Search for domain in all sections
5. Report status

**Output format:**
```markdown
## Domain Validation: {DOMAIN}

**Format Check:**
- ✅ Matches pattern `{app-name}.axoiq.com`
- ✅ Valid characters (lowercase, alphanumeric, hyphens)
- ✅ Appropriate length

**Availability:**
- ✅ Domain is available | ❌ Domain already allocated to {SERVICE}

**Recommendation:**
{If invalid or taken, suggest alternative domain}
```

---

### 4. Find Available Port in Range

Suggest the next available port for a specific application.

**Input required:**
- Application name (FORGE, SYNAPSE, NEXUS, PRISM, ATLAS, or custom)

**Process:**
1. Read `url-registry.yml`
2. Identify port range for application
3. Extract all allocated ports in range
4. Find lowest available port number
5. Suggest port + show allocation stats

**Output format:**
```markdown
## Available Ports for {APPLICATION}

**Range:** {START}-{END} (1000 ports total)
**Allocated:** {COUNT} ports
**Available:** {REMAINING} ports

**Recommended port:** {PORT}
  (First available port in range)

**Alternative ports:**
- {PORT+1}
- {PORT+10}
- {PORT+100}

**Allocated ports:**
{PORT1}, {PORT2}, {PORT3}...
```

---

### 5. Full Allocation Check

Complete validation before proposing a new service.

**Input required:**
- Service name
- Proposed domain
- Proposed port(s)
- Application category (AXIOM app, FORGE infra, Personal project)

**Process:**
Combines all checks:
1. Validate domain format and availability
2. Check port availability in appropriate range
3. Verify no conflicts with existing services
4. Provide complete validation report

**Output format:**
```markdown
## Full Allocation Check: {SERVICE_NAME}

### Proposed Configuration
- **Name:** {SERVICE_NAME}
- **Domain:** {DOMAIN}
- **Port(s):** {PORT}
- **Category:** {CATEGORY}

### Validation Results

**Domain:**
- Format: ✅ Valid | ❌ Invalid ({reason})
- Availability: ✅ Available | ❌ Taken by {service}

**Port(s):**
- Range: {RANGE} ({appropriate for category})
- Availability: ✅ Available | ❌ Conflict with {service} on port {port}

**Overall Status:**
✅ Ready for allocation | ⚠️ Issues found | ❌ Conflicts detected

### Next Steps
{If valid:}
1. Update `url-registry.yml`
2. Add to `hosts-entries.txt`
3. Configure Traefik labels
4. Update `10-traefik-routing.md`

{If issues:}
- Fix: {list of required fixes}
- Suggested alternatives: {alternatives}
```

---

## Usage Examples

### Example 1: Check all active URLs

```
skill: "zz-url-check"
action: "show-all"
```

### Example 2: Check port availability

```
skill: "zz-url-check"
action: "check-port"
port: 6100
range: "PRISM"
```

### Example 3: Validate domain

```
skill: "zz-url-check"
action: "validate-domain"
domain: "prism.axoiq.com"
```

### Example 4: Find available port

```
skill: "zz-url-check"
action: "find-port"
application: "PRISM"
```

### Example 5: Full allocation check

```
skill: "zz-url-check"
action: "full-check"
service_name: "PRISM"
domain: "prism.axoiq.com"
port: 6000
category: "AXIOM application"
```

---

## Integration with Workflow

**Before any URL/port allocation, agents should:**

1. **Run full-check** with proposed configuration
2. **Review validation results**
3. **Fix any issues** identified
4. **Use AskUserQuestion** to validate with user
5. **Proceed with allocation** only after approval

**Example workflow:**

```markdown
User: "I want to add PRISM dashboard"

Agent:
1. Skill: zz-url-check (full-check: PRISM, prism.axoiq.com, 6000, AXIOM)
2. Review: ✅ Domain available, ✅ Port 6000 available in PRISM range
3. AskUserQuestion: "Approve allocation? Domain: prism.axoiq.com, Port: 6000"
4. After approval: Update registry + configure Traefik
```

---

## Error Handling

### Port outside range

```markdown
❌ Error: Port {PORT} is outside {APPLICATION} range ({RANGE})

**Solution:** Choose a port within the allocated range.
**Recommended:** {FIRST_AVAILABLE_PORT} (next available in range)
```

### Domain format invalid

```markdown
❌ Error: Domain "{DOMAIN}" does not match required format

**Required format:** {app-name}.axoiq.com
**Valid example:** prism.axoiq.com
**Your domain:** {DOMAIN}

**Fix:** Use lowercase letters, numbers, hyphens only, ending with .axoiq.com
```

### Port already allocated

```markdown
❌ Error: Port {PORT} is already allocated

**Used by:** {SERVICE} ({DOMAIN})
**Allocated to:** {CATEGORY}

**Alternative ports in {RANGE}:**
- {ALT1}
- {ALT2}
- {ALT3}
```

---

## Reference Files

**Primary:**
- `D:\Projects\AXIOM\.dev\infra\url-registry.yml` - Source of truth

**Related:**
- `.dev/infra/QUICK-REFERENCE-URLS.md` - Quick reference
- `.dev/infra/hosts-entries.txt` - Hosts file template
- `.claude/agents/rules/10-traefik-routing.md` - Routing rules
- `.claude/agents/rules/11-url-registry.md` - Allocation process

---

## Changelog

| Date | Change |
|------|--------|
| 2025-11-29 | Initial creation of URL check skill |
| 2025-11-29 | Added 5 validation actions |
| 2025-11-29 | Integrated with url-registry.yml |

---

**Note:** This skill is READ-ONLY. It validates and suggests but does NOT modify the registry. Actual modifications must be done by agents after user approval.
