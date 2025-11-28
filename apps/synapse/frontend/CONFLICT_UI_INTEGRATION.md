# Phase 2: Conflict Detection UI Integration Guide

## Overview

This guide shows how to integrate the `RuleConflicts` component into the RulesManagement page to visualize rule conflicts and enforcement violations.

## Component Created

**File:** `src/components/rules/RuleConflicts.tsx`

This component displays:
- ✅ Summary stats (total rules, conflicts, violations)
- ⚠️ Enforcement violations (critical - blocked rules)
- 📊 Valid overrides (informational)
- ✅ No conflicts message

## Integration Steps

### 1. Import the Component

Add to `src/pages/RulesManagement.tsx`:

```typescript
import { RuleConflicts } from '../components/rules/RuleConflicts';
import { Tabs } from '../components/ui/Tabs';
import { AlertTriangle } from 'lucide-react';
```

### 2. Add State Management

```typescript
const [activeTab, setActiveTab] = useState<string>('rules');
const [conflictsData, setConflictsData] = useState<any>(null);
const [conflictsLoading, setConflictsLoading] = useState(false);
```

### 3. Add Conflict Fetching Function

```typescript
const fetchConflicts = async () => {
  setConflictsLoading(true);
  try {
    // Get project ID from context or use default
    const projectId = 'default-project'; // Replace with actual project ID
    const response = await axios.get(`${API_URL}/api/rules/conflicts/${projectId}`);
    setConflictsData(response.data);
    logger.info(`Detected ${response.data.conflicts_count} conflicts`);
  } catch (error) {
    logger.error('Failed to fetch conflicts', error as Error);
  } finally {
    setConflictsLoading(false);
  }
};

const handleCheckConflicts = () => {
  setActiveTab('conflicts');
  fetchConflicts();
};
```

###4. Add Check Conflicts Button

In the filters/actions section:

```typescript
<Button
  variant="primary" // Or use appropriate variant
  onClick={handleCheckConflicts}
  className="whitespace-nowrap"
>
  <AlertTriangle className="w-5 h-5 mr-2" />
  Check Conflicts
</Button>
```

### 5. Add Tabs Navigation

After the filters section:

```typescript
<Tabs
  tabs={[
    { id: 'rules', label: 'Rules', icon: BookOpen, count: rules.length },
    { 
      id: 'conflicts', 
      label: 'Conflicts', 
      icon: AlertTriangle,
      count: conflictsData ? conflictsData.conflicts_count + conflictsData.enforcement_violations_count : undefined
    }
  ]}
  activeTab={activeTab}
  onTabChange={setActiveTab}
/>
```

### 6. Add Tab Content

Replace the rules table with conditional rendering:

```typescript
{activeTab === 'rules' && (
  <>
    {/* Stats Bar */}
    <div className="grid grid-cols-4 gap-4 mb-6">
      {/* ... existing stats ... */}
    </div>

    {/* Rules Table */}
    <RulesTable
      rules={rules}
      onEdit={handleEdit}
      onToggle={handleToggle}
      onDelete={handleDelete}
      onTest={handleTest}
    />
  </>
)}

{activeTab === 'conflicts' && (
  <RuleConflicts
    projectId="default-project"
    conflictsData={conflictsData}
    isLoading={conflictsLoading}
    onRefresh={fetchConflicts}
  />
)}
```

## Quick Integration (Minimal Changes)

If full tab integration is too complex, you can add a simple conflicts section at the bottom:

```typescript
{/* Add after existing content */}
<div className="mt-8">
  <div className="flex items-center justify-between mb-4">
    <h2 className="text-2xl font-bold text-white flex items-center gap-3">
      <AlertTriangle className="w-6 h-6 text-amber-500" />
      Rule Conflicts
    </h2>
    <Button onClick={fetchConflicts}>
      Refresh Conflicts
    </Button>
  </div>
  
  <RuleConflicts
    projectId="default-project"
    conflictsData={conflictsData}
    isLoading={conflictsLoading}
    onRefresh={fetchConflicts}
  />
</div>
```

## Testing

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Run migration: `alembic upgrade head`
3. Seed rules: `python3 -m app.scripts.seed_baseline_rules`
4. Start frontend: `npm run dev`
5. Navigate to Rules Management
6. Click "Check Conflicts" button
7. View conflicts in the Conflicts tab

## Expected Output

- **No conflicts**: Green success message
- **Valid overrides**: Amber/yellow conflict cards showing which rules override others
- **Enforcement violations**: Red error cards showing blocked rules that tried to override enforced rules

## Screenshot Placeholders

(Would show screenshots of:)
1. Rules Management page with "Check Conflicts" button
2. Conflicts tab showing no conflicts
3. Conflicts tab showing enforcement violation
4. Conflicts tab showing valid override

---

**Status:** Component Created  
**Ready for:** Manual Integration  
**Complexity:** Medium (requires tab navigation)
