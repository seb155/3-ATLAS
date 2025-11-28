# Next Sprint: v0.3.0 - Multi-Tenant Authentication

**Status:** PLANNED  
**Target:** 2026-02-21 (2 weeks)  
**Priority:** HIGH

---

## Goal

Implement enterprise-grade authentication and multi-tenant architecture to support multiple organizations and projects.

---

## Scope

### 1. Azure AD Integration + SSO
- Azure AD authentication
- Single Sign-On (SSO)
- OAuth 2.0 / OpenID Connect
- Token refresh
- Logout flow

### 2. RBAC (5 Roles)
- **SysAdmin** - Full system access
- **OrgAdmin** - Manage organization and users
- **ProjectManager** - Manage projects, approve changes
- **Engineer** - Create/edit assets, run rules
- **Viewer** - Read-only access

**Permissions Matrix:** See [backlog/multi-tenant-auth.md](backlog/multi-tenant-auth.md)

### 3. Organization Hierarchy
- Organization → Clients → Projects
- User belongs to Organization
- User assigned to Projects
- Project isolation (data not shared across projects)

### 4. User Management UI
- Invite users (email)
- Assign roles
- Manage permissions
- User profile settings
- Audit user actions

### 5. Audit Trail Integration
- All actions logged with user context
- "Who changed what when" tracking
- Audit log filtering by user

---

## Database Schema Changes

```sql
-- Organizations
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    domain VARCHAR(100), -- e.g., aurumax.com
    azure_tenant_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Users (enhanced)
ALTER TABLE users 
ADD COLUMN organization_id UUID REFERENCES organizations(id),
ADD COLUMN azure_oid VARCHAR(100), -- Azure Object ID
ADD COLUMN role VARCHAR(20) DEFAULT 'ENGINEER';

-- Project Access
CREATE TABLE project_access (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    project_id UUID REFERENCES projects(id),
    role VARCHAR(20), -- Can override global role per project
    granted_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, project_id)
);
```

---

## Tasks

### Planning
- [x] Review Azure AD setup requirements
- [x] Document RBAC model
- [x] Document in backlog

### Implementation (Backend)
- [ ] Set up Azure AD application
- [ ] Implement OAuth 2.0 flow
- [ ] Add organization/user models
- [ ] Implement RBAC middleware
- [ ] Add project access control
- [ ] Update existing endpoints with auth checks

### Implementation (Frontend)
- [ ] Azure AD login flow
- [ ] Token management (refresh)
- [ ] User context provider
- [ ] User management UI
- [ ] Role-based UI hiding

### Verification
- [ ] Backend tests:
  ```bash
  docker exec synapse-backend-1 pytest tests/test_auth.py
  docker exec synapse-backend-1 pytest tests/test_rbac.py
  ```
- [ ] Frontend tests:
  ```bash
  cd apps/synapse/frontend
  npm run test -- Auth.test.tsx
  npm run test -- UserManagement.test.tsx
  ```
- [ ] Manual testing:
  - Login with Azure AD
  - Create organization
  - Invite user
  - Assign role
  - Verify permissions (try accessing restricted endpoint as Viewer)
  - Test SSO logout

---

## Dependencies

**Blocked by:** v0.2.11 (complete Core Platform)  
**Blocks:** v0.4.0 (background jobs need user context)

---

## Documentation

**Planning:** [backlog/multi-tenant-auth.md](backlog/multi-tenant-auth.md)

---

**Updated:** 2025-11-24
