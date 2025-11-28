# Multi-Tenant Architecture & Access Control

**Updated:** 2025-11-22  
**Priority:** Critical for enterprise deployment

---

## 🎯 Requirements

### Data Isolation
1. ✅ **Multi-Client** - Multiple independent clients
2. ✅ **Multi-Project** - Each client has multiple projects
3. ✅ **Data Separation** - Complete isolation between clients
4. ✅ **Flexible Navigation** - By client OR by project

### Access Control
1. ✅ **Users, Groups, Roles** (modern RBAC)
2. ✅ **Read/Write permissions** (granular)
3. ✅ **Local auth** (Phase 1-5)
4. ✅ **Azure AD integration** (Phase 6)
5. ✅ **SSO with work computer** (Phase 6)

---

## 🏗️ Database Schema - Multi-Tenant

### Core Hierarchy

```
Organization (Optional - for multi-org)
    ↓
Clients (Mining companies, etc.)
    ↓
Projects (Greece Gold Mine, Brazil Copper, etc.)
    ↓
Assets, Cables, Rules, Packages, etc.
```

### Tables

```sql
-- Organizations (optional - if hosting multiple companies)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    domain VARCHAR(100),  -- For SSO (@acme-corp.com)
    created_at TIMESTAMP DEFAULT NOW()
);

-- Clients (mining companies, operators, etc.)
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),  -- Optional
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50) UNIQUE,  -- "AURUMAX", "GOLD_CORP"
    contact_info JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Projects (individual jobs)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) NOT NULL,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50),  -- "GREECE-GM-2025"
    description TEXT,
    country_code VARCHAR(2),  -- "GR", "BR", "CA"
    status VARCHAR(50) DEFAULT 'ACTIVE',  -- ACTIVE, ON_HOLD, COMPLETED, ARCHIVED
    start_date DATE,
    end_date DATE,
    budget DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(client_id, code)
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),  -- NULL for SSO users
    full_name VARCHAR(200),
    auth_provider VARCHAR(50) DEFAULT 'local',  -- 'local', 'azure_ad', 'google'
    external_id VARCHAR(255),  -- Azure AD user ID, etc.
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- User Groups (team-based)
CREATE TABLE user_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    organization_id UUID REFERENCES organizations(id),  -- Optional
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_group_members (
    user_id UUID REFERENCES users(id),
    group_id UUID REFERENCES user_groups(id),
    PRIMARY KEY (user_id, group_id)
);

-- Roles (permission sets)
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL,  -- {"assets": ["read", "write"], ...}
    is_system BOOLEAN DEFAULT FALSE,  -- System roles (admin, viewer)
    created_at TIMESTAMP DEFAULT NOW()
);

-- Project Access (who can access which projects)
CREATE TABLE project_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) NOT NULL,
    user_id UUID REFERENCES users(id),
    group_id UUID REFERENCES user_groups(id),
    role_id UUID REFERENCES roles(id) NOT NULL,
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT NOW(),
    
    -- Either user_id OR group_id must be set
    CHECK (
        (user_id IS NOT NULL AND group_id IS NULL) OR
        (user_id IS NULL AND group_id IS NOT NULL)
    )
);

-- Client Access (optional - for client-level permissions)
CREATE TABLE client_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) NOT NULL,
    user_id UUID REFERENCES users(id),
    group_id UUID REFERENCES user_groups(id),
    role_id UUID REFERENCES roles(id) NOT NULL,
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT NOW()
);

-- Add project_id to main tables
ALTER TABLE assets ADD COLUMN project_id UUID REFERENCES projects(id) NOT NULL;
ALTER TABLE cables ADD COLUMN project_id UUID REFERENCES projects(id) NOT NULL;
ALTER TABLE rule_definitions ADD COLUMN project_id UUID REFERENCES projects(id);
-- NULL for global rules, NOT NULL for project-specific

-- Indexes for performance
CREATE INDEX idx_assets_project ON assets(project_id);
CREATE INDEX idx_cables_project ON cables(project_id);
CREATE INDEX idx_project_access_user ON project_access(user_id);
CREATE INDEX idx_project_access_project ON project_access(project_id);
```

---

## 🔐 Role-Based Access Control (RBAC)

### Permission Model

**Resources:**
- `assets` - Engineering assets
- `cables` - Generated cables
- `rules` - Rule definitions
- `packages` - Work packages
- `users` - User management
- `projects` - Project settings

**Actions:**
- `read` - View data
- `write` - Create/update data
- `delete` - Delete data
- `execute` - Execute rules, generate deliverables
- `admin` - Full control

**Permission JSON:**
```json
{
  "assets": ["read", "write"],
  "cables": ["read", "write", "execute"],
  "rules": ["read", "execute"],
  "packages": ["read"],
  "users": [],
  "projects": ["read"]
}
```

### System Roles (Predefined)

```python
# backend/app/models/auth.py
SYSTEM_ROLES = {
    "super_admin": {
        "name": "Super Admin",
        "description": "Full system access",
        "permissions": "*"  # All permissions
    },
    
    "project_manager": {
        "name": "Project Manager",
        "description": "Manage project, assign users, execute rules",
        "permissions": {
            "assets": ["read", "write", "delete"],
            "cables": ["read", "write", "delete", "execute"],
            "rules": ["read", "write", "execute"],
            "packages": ["read", "write", "execute"],
            "users": ["read"],
            "projects": ["read", "write"]
        }
    },
    
    "engineer": {
        "name": "Engineer",
        "description": "Full access to engineering data",
        "permissions": {
            "assets": ["read", "write"],
            "cables": ["read", "write", "execute"],
            "rules": ["read", "execute"],
            "packages": ["read", "write"],
            "users": [],
            "projects": ["read"]
        }
    },
    
    "viewer": {
        "name": "Viewer",
        "description": "Read-only access",
        "permissions": {
            "assets": ["read"],
            "cables": ["read"],
            "rules": ["read"],
            "packages": ["read"],
            "users": [],
            "projects": ["read"]
        }
    },
    
    "client_viewer": {
        "name": "Client Viewer",
        "description": "Client read-only (for client stakeholders)",
        "permissions": {
            "assets": ["read"],
            "cables": ["read"],
            "packages": ["read"],
            # No access to rules (proprietary)
            "users": [],
            "projects": ["read"]
        }
    }
}
```

---

## 🔑 Authentication Strategy

### Phase 1-5: Local Authentication (JWT)

**Current implementation - Continue using**

```python
# backend/app/services/auth_service.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def authenticate_user(self, email: str, password: str):
        user = get_user_by_email(email)
        if not user or not self.verify_password(password, user.password_hash):
            return None
        return user
    
    def create_access_token(self, user_id: str, project_id: str = None):
        # Include project_id in token
        payload = {
            "sub": user_id,
            "project_id": project_id,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
    
    def hash_password(self, password):
        return pwd_context.hash(password)
```

---

### Phase 6: Azure AD Integration (SSO)

**Technology:**
- **Microsoft Authentication Library (MSAL)**
- **OAuth 2.0 / OpenID Connect**

**Implementation:**

```python
# backend/app/services/azure_ad_service.py
from msal import ConfidentialClientApplication

class AzureADService:
    def __init__(self):
        self.app = ConfidentialClientApplication(
            client_id=settings.AZURE_CLIENT_ID,
            client_credential=settings.AZURE_CLIENT_SECRET,
            authority=f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}"
        )
    
    def get_authorization_url(self):
        return self.app.get_authorization_request_url(
            scopes=["User.Read"],
            redirect_uri=settings.AZURE_REDIRECT_URI
        )
    
    def exchange_code_for_token(self, code: str):
        result = self.app.acquire_token_by_authorization_code(
            code=code,
            scopes=["User.Read"],
            redirect_uri=settings.AZURE_REDIRECT_URI
        )
        return result
    
    def get_or_create_user(self, azure_user_info):
        # Check if user exists by external_id
        user = db.query(User).filter(
            User.external_id == azure_user_info["id"]
        ).first()
        
        if not user:
            # Create new user
            user = User(
                email=azure_user_info["mail"],
                full_name=azure_user_info["displayName"],
                auth_provider="azure_ad",
                external_id=azure_user_info["id"],
                password_hash=None  # SSO, no password
            )
            db.add(user)
            db.commit()
        
        return user
```

**Frontend Flow:**

```typescript
// src/services/authService.ts
async function loginWithAzureAD() {
  // Redirect to Azure AD login
  const authUrl = await api.get('/api/v1/auth/azure/login');
  window.location.href = authUrl.url;
}

// Callback handler
async function handleAzureCallback(code: string) {
  const response = await api.post('/api/v1/auth/azure/callback', { code });
  localStorage.setItem('token', response.token);
  // User logged in
}
```

---

## 🗂️ UI: Client & Project Selection

### Top Navigation Bar

```
┌─────────────────────────────────────────────────────────┐
│ [SYNAPSE Logo] │ Client ▼ │ Project ▼ │ [User Menu ▼] │
└─────────────────────────────────────────────────────────┘
```

### Client Selector

```typescript
// src/components/ClientSelector.tsx
<Select
  value={selectedClient}
  onChange={(client) => {
    setSelectedClient(client);
    loadClientProjects(client.id);
    setSelectedProject(null);  // Clear project
  }}
>
  <SelectItem value="aurumax">
    <ClientIcon /> AuruMax Corp
  </SelectItem>
  <SelectItem value="goldfields">
    <ClientIcon /> Gold Fields Ltd
  </SelectItem>
  <SelectItem value="all">
    <AllIcon /> All Clients (Admin only)
  </SelectItem>
</Select>
```

### Project Selector (Two Modes)

**Mode 1: By Client (Filtered)**
```typescript
// After selecting client
<Select
  value={selectedProject}
  onChange={(project) => {
    setSelectedProject(project);
    loadProjectData(project.id);
  }}
>
  <SelectItem value="greece-gm-2025">
    🇬🇷 Greece Gold Mine 2025
  </SelectItem>
  <SelectItem value="brazil-cm-2024">
    🇧🇷 Brazil Copper Mine 2024
  </SelectItem>
</Select>
```

**Mode 2: Direct (All Projects)**
```typescript
// Search all projects (if user has access)
<Combobox
  placeholder="Search projects..."
  onSearch={searchProjects}
  onSelect={(project) => {
    setSelectedProject(project);
    setSelectedClient(project.client);  // Auto-set client
    loadProjectData(project.id);
  }}
>
  <ComboboxItem value="greece-gm-2025">
    🇬🇷 Greece Gold Mine 2025 (AuruMax)
  </ComboboxItem>
  <ComboboxItem value="canada-nm-2025">
    🇨🇦 Canada Nickel Mine 2025 (Gold Fields)
  </ComboboxItem>
</Combobox>
```

### User Menu

```
┌─────────────────────────────────┐
│ Jean-François (Engineer)        │
├─────────────────────────────────┤
│ My Profile                      │
│ Switch Project                  │
│ Manage Users (if admin)         │
│ Settings                        │
│ ────────────────────────────    │
│ Logout                          │
└─────────────────────────────────┘
```

---

## 🛡️ Permission Checking (Backend)

### FastAPI Dependency

```python
# backend/app/dependencies/auth.py
from fastapi import Depends, HTTPException, Header
from jose import jwt

async def get_current_user(
    token: str = Header(..., alias="Authorization")
) -> User:
    try:
        payload = jwt.decode(token.replace("Bearer ", ""), SECRET_KEY)
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(401, "Invalid user")
        return user
    except JWTError:
        raise HTTPException(401, "Invalid token")

async def get_current_project(
    project_id: str = Header(..., alias="X-Project-ID"),
    user: User = Depends(get_current_user)
) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    
    # Check access
    has_access = db.query(ProjectAccess).filter(
        ProjectAccess.project_id == project_id,
        ProjectAccess.user_id == user.id
    ).first()
    
    if not has_access:
        raise HTTPException(403, "Access denied to this project")
    
    return project

def require_permission(resource: str, action: str):
    async def check_permission(
        user: User = Depends(get_current_user),
        project: Project = Depends(get_current_project)
    ):
        # Get user's role for this project
        access = db.query(ProjectAccess).filter(
            ProjectAccess.project_id == project.id,
            ProjectAccess.user_id == user.id
        ).first()
        
        role = db.query(Role).filter(Role.id == access.role_id).first()
        
        # Check permission
        if role.permissions == "*":  # Super admin
            return True
        
        if resource in role.permissions:
            if action in role.permissions[resource]:
                return True
        
        raise HTTPException(403, f"No {action} permission for {resource}")
    
    return check_permission
```

### API Endpoint with Permission

```python
# backend/app/api/endpoints/assets.py
@router.get("/api/v1/assets/")
async def list_assets(
    project: Project = Depends(get_current_project),
    _: None = Depends(require_permission("assets", "read"))
):
    assets = db.query(Asset).filter(
        Asset.project_id == project.id
    ).all()
    return assets

@router.post("/api/v1/assets/")
async def create_asset(
    asset_data: AssetCreate,
    project: Project = Depends(get_current_project),
    user: User = Depends(get_current_user),
    _: None = Depends(require_permission("assets", "write"))
):
    asset = Asset(**asset_data.dict(), project_id=project.id, created_by=user.id)
    db.add(asset)
    db.commit()
    return asset
```

---

## 🌐 Frontend: Permission-Aware UI

### React Context

```typescript
// src/contexts/PermissionContext.tsx
interface PermissionContextValue {
  canRead: (resource: string) => boolean;
  canWrite: (resource: string) => boolean;
  canDelete: (resource: string) => boolean;
  canExecute: (resource: string) => boolean;
}

export function PermissionProvider({ children }) {
  const { currentProject, currentUser } = useAuth();
  const [permissions, setPermissions] = useState({});
  
  useEffect(() => {
    if (currentProject && currentUser) {
      // Fetch user's role for current project
      api.get(`/api/v1/projects/${currentProject.id}/my-permissions`)
        .then(perms => setPermissions(perms));
    }
  }, [currentProject, currentUser]);
  
  const canRead = (resource: string) => {
    return permissions[resource]?.includes('read') ?? false;
  };
  
  // ... similar for write, delete, execute
  
  return (
    <PermissionContext.Provider value={{ canRead, canWrite, ... }}>
      {children}
    </PermissionContext.Provider>
  );
}
```

### Component Usage

```typescript
// src/components/AssetGrid.tsx
function AssetGrid() {
  const { canWrite, canDelete } = usePermissions();
  
  return (
    <AGGridReact
      rowData={assets}
      // ...
      onCellValueChanged={(params) => {
        if (!canWrite('assets')) {
          toast.error("No write permission");
          params.node.setData(params.oldValue);  // Revert
          return;
        }
        updateAsset(params.data);
      }}
      
      // Hide delete button if no permission
      components={{
        deleteButton: canDelete('assets') 
          ? DeleteButton 
          : null
      }}
    />
  );
}
```

---

## 📊 User Management UI

### Admin Panel

```
┌──────────────────────────────────────────────────────────┐
│ User Management                              [+ Add User]│
├──────────────────────────────────────────────────────────┤
│ Email              │ Name      │ Groups    │ Projects   │
├────────────────────┼───────────┼───────────┼────────────┤
│ jf@acme.com        │ Jean-F    │ Engineers │ 3 projects │
│ → Edit │ Deactivate │ View Access                        │
│                                                          │
│ maria@acme.com     │ Maria S   │ PM        │ 5 projects │
│ → Edit │ Deactivate │ View Access                        │
└──────────────────────────────────────────────────────────┘
```

### Grant Access Modal

```
┌──────────────────────────────────────────────────────────┐
│ Grant Project Access: Greece Gold Mine 2025             │
├──────────────────────────────────────────────────────────┤
│ User/Group: [Search users...]                           │
│                                                          │
│ Role: ○ Super Admin                                     │
│       ● Project Manager                                 │
│       ○ Engineer                                        │
│       ○ Viewer                                          │
│       ○ Client Viewer                                   │
│                                                          │
│ Permissions Preview:                                    │
│ ✅ Read/Write assets, cables                            │
│ ✅ Execute rules                                         │
│ ✅ Manage packages                                       │
│ ❌ Manage users                                          │
│                                                          │
│          [Cancel]  [Grant Access]                        │
└──────────────────────────────────────────────────────────┘
```

---

## 🔄 Migration Strategy (Simplified Start)

### Phase 2-3: Basic Multi-Project
- Add `projects` table
- Add `project_id` to assets/cables
- Single default user (admin)
- No permission checking yet

### Phase 4: Users & Groups
- Add `users`, `user_groups` tables
- JWT authentication
- Basic read/write permissions

### Phase 5: Full RBAC
- Add `roles`, `project_access` tables
- Permission checking on all endpoints
- UI permission awareness

### Phase 6: Enterprise Auth
- Azure AD integration
- SSO with work computer
- Client-level permissions

---

## ✅ Summary

**Data Model:**
- Organizations → Clients → Projects → Assets
- Complete isolation between projects

**Navigation:**
- Client dropdown → Project dropdown (filtered)
- OR direct project search (all accessible projects)

**Auth Strategy:**
- Phase 1-5: Local JWT (simple start)
- Phase 6: Azure AD + SSO (enterprise)

**Permissions:**
- RBAC with 5 system roles
- Granular (read/write/delete/execute)
- Project-level access control

**Implementation:**
- Start simple (Phase 2-3)
- Add complexity progressively
- Full enterprise auth by Phase 6

**Ready for enterprise multi-tenant deployment!**
