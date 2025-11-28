# SYNAPSE - Vision & Context

**Why this project exists and who it's for.**

---

## Mission

Build a PLM platform for EPCM automation projects that reduces 80% of repetitive engineering work through rule-based automation and intelligent data management.

**Focus:** Core PLM value first, advanced features later.

---

## The Problem

### Current Manual Process

1. Import incomplete P&IDs/instrument lists
2. Manually complete specs (voltage, HP, location, etc.)
3. Copy/paste data into Excel templates
4. Generate deliverables (BID LST, Cable Schedule, IO List)
5. Repeat for 11 packages

**Time:** 100+ hours per project
**Errors:** High (copy/paste, inconsistencies)

### Typical EPCM Project

- 3000+ IO points
- Multi-discipline (Process, Electrical, Controls)
- Self-perform construction
- 3-6 month timeline
- Tight budget

### Pain Points

- Repetitive data entry
- Copy/paste errors
- Manual deliverable generation
- Late changes requiring rework

---

## The Solution

### SYNAPSE Automated Process

1. Import CSV/Excel (3000 instruments)
2. Rules auto-complete data → 5000+ assets
3. One-click generate 11 packages
4. Export professional deliverables

**Time:** 10-20 hours
**Errors:** Minimal (rule-validated)
**Savings:** 80-90% reduction

### Core Automation

**6 Action Types:**
- `CREATE_CHILD` - Pump → Motor
- `SET_PROPERTY` - Set voltage 400V
- `CREATE_CABLE` - Motor → MCC cable
- `CREATE_PACKAGE` - Group assets
- `ALLOCATE_IO` - Assign PLC terminal
- `VALIDATE` - Check constraints

**4-Tier Priority:**
- CLIENT (100) > PROJECT (50) > COUNTRY (30) > FIRM (10)

**Result:** 100 instruments → 500+ completed assets automatically

---

## User Profile

**Role:** Senior Automation Engineer
**Experience:** 10+ years EPCM (mining, water treatment)
**Location:** Québec, Canada
**Projects:** 100-500 instruments per project

### Expertise

- PlantPAX, ControlLogix
- Instrumentation (E+H, 4-20mA, HART)
- Electrical codes (CEC, 600V systems)
- P&IDs, motor sizing

### Technical Preferences

**Keep Simple:**
- Proven technologies
- Minimal dependencies
- Easy to maintain

**Prefer:**
- PostgreSQL over NoSQL
- JWT over sessions
- React over Angular/Vue
- FastAPI over Django

---

## Engineering Standards

### Electrical

- CEC (Canadian Electrical Code)
- 600V standard (Canada)
- Cable sizing per CEC tables

### Automation

- PlantPAX Architecture
- ISA-88 (batch)
- ISA-95 (integration)

### Naming

- ISA-5.1 (instrument tags)
- Natural language (not code-style)

---

## Business Value

### Time Savings

| Metric | Before | After |
|--------|--------|-------|
| Hours per project | 100+ | 10-20 |
| Reduction | - | 80-90% |
| ROI | - | ~$10K/project |

### Quality Improvement

- **Errors:** 90% reduction (rule-validated)
- **Consistency:** 100% (same rules always)
- **Traceability:** Complete history

### Knowledge Reuse

- Project templates
- Rule library
- Catalog database
- **Future projects:** 50% faster

---

## Comparison

| vs | Advantage |
|----|-----------|
| **Manual Excel** | 80% faster, 90% fewer errors, complete traceability |
| **Generic PLM (Aras, Teamcenter)** | Purpose-built for EPCM, no customization, 10x cheaper |
| **Other EPCM Tools** | Rule-based automation (unique), multi-dimensional org |

---

## Development Philosophy

### v0.2.0 (Core)

- Solid foundation
- Proven value
- Engineer feedback
- Stable & reliable

### v0.3.0+ (Advanced)

- AI integration
- Drawing automation
- Enterprise auth
- Based on v0.2.0 learnings

**Progressive, not all-at-once.**

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Time savings | 100h → 10-20h per project |
| Error reduction | 90% fewer |
| Adoption | Engineers using daily |
| ROI | $10K+ savings per project |

---

## Security & Privacy

### Data Sensitivity

- Client names: Confidential
- Project specs: Confidential
- Engineering rules: Proprietary

### Deployment

- Self-hosted (Proxmox)
- No cloud dependencies (v0.2.0)
- Local authentication

### Future (v0.3.0+)

- Azure AD (enterprise)
- SSO

---

**This is why SYNAPSE exists: to give engineers their time back.**
