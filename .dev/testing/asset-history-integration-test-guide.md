# Asset History Integration - Testing Guide

**Feature:** AssetHistory Component Integration into AssetDetails
**Version:** v0.2.5+
**Date:** 2025-11-28
**Status:** ✅ Build Passing - Ready for Manual Testing

---

## Overview

The AssetHistory component has been integrated into AssetDetails as a new "Version History" tab. This feature allows users to view complete version history, compare changes, and rollback assets to previous versions.

---

## 🚀 Quick Start

### 1. Start the Development Environment

```powershell
# Terminal 1 - Start FORGE infrastructure (if not running)
cd forge
docker compose up -d forge-postgres forge-redis

# Terminal 2 - Start Backend
cd apps/synapse
docker compose -f docker-compose.dev.yml up --build

# Terminal 3 - Start Frontend
cd apps/synapse/frontend
npm run dev
```

**Access URLs:**
- **Frontend:** http://localhost:4000
- **Backend API:** http://localhost:8001/docs
- **Database:** postgresql://postgres:postgres@localhost:5433/synapse

### 2. Login Credentials

```
Email:    admin@axoiq.com
Password: admin123!
```

---

## 📋 Test Scenarios

### Scenario 1: View Asset Version History

**Objective:** Verify version history loads and displays correctly

**Steps:**

1. Navigate to **Engineering Explorer**
   - URL: http://localhost:4000/engineering
   - Or click "Engineering" in sidebar

2. Select a project from the dropdown (top-left)

3. In the tree sidebar (left), expand any location/system

4. Click on any **asset** (instrument, motor, valve, etc.)
   - Example: Click an instrument tag like "FT-101"

5. Click the **"Version History"** tab
   - Look for tab with clock/history icon
   - It's the rightmost tab after "Documents"

**Expected Results:**

✅ **If asset has versions:**
- Version list appears with version numbers (v1, v2, v3...)
- Each version shows:
  - Version badge (blue)
  - Change source (e.g., "CSV Import", "Manual Edit", "Rule Execution")
  - Timestamp (formatted as "Nov 28, 2024, 2:30 PM")
  - Created by user (if available)
  - Change reason (if provided)
- "Compare" button on each version
- "Rollback" button on older versions

✅ **If asset has NO versions:**
- Empty state displays:
  - Clock icon (faded)
  - Message: "No version history available"

✅ **If projectId is missing:**
- Helpful message:
  - History icon (faded)
  - "Version history requires a project context"
  - "Please ensure projectId is provided"

---

### Scenario 2: Expand Version Snapshot

**Objective:** View complete snapshot data for a version

**Steps:**

1. From version list, click anywhere on a version card
   - Click the version header row

2. Observe the version card expansion

**Expected Results:**

✅ **Card expands with:**
- "Snapshot:" label
- JSON data in formatted code block
- Dark background with syntax highlighting
- Scrollable if content is large

✅ **Click again to collapse:**
- Card returns to compact state

---

### Scenario 3: Compare Two Versions

**Objective:** View differences between consecutive versions

**Steps:**

1. Click **"Compare"** button on any version (except v1)

2. Observe the diff view appears at top of version list

**Expected Results:**

✅ **Diff panel displays:**
- Header: "Changes from vX → vY"
- List of changed fields with:
  - Field name (bold)
  - Old value (left)
  - New value (right)
  - Color coding:
    - Green = Added field
    - Red = Removed field
    - Yellow = Modified field

✅ **Multiple changes:**
- All changed fields listed
- JSON values shown for complex fields

---

### Scenario 4: Rollback to Previous Version

**Objective:** Restore asset to a previous state

**Steps:**

1. Click **"Rollback"** button on an older version
   - Button only appears on versions older than latest

2. Confirm the browser confirmation dialog

3. Wait for success message

**Expected Results:**

✅ **Before rollback:**
- Confirmation dialog: "Rollback to version X? This will create a new version with the old data."
- User must click OK or Cancel

✅ **After rollback:**
- Success alert: "Rollback successful!"
- Version list reloads automatically
- New version created at top (e.g., v5) with data from old version (e.g., v2)
- Asset data in other tabs reflects rollback

✅ **Error handling:**
- If rollback fails, error message displays
- Example: "Rollback failed" or specific API error

---

### Scenario 5: Loading States

**Objective:** Verify loading indicators work

**Steps:**

1. Navigate to AssetHistory tab on an asset

2. Observe loading state before data appears

**Expected Results:**

✅ **Initial load:**
- Spinner or skeleton loader
- Text: "Loading version history..."

✅ **Compare/Diff load:**
- Brief loading indication when comparing

---

### Scenario 6: Error Handling

**Objective:** Test error scenarios

**Test 6.1 - Network Error:**

1. Stop the backend server
   ```powershell
   docker stop synapse-backend
   ```

2. Try to load version history

**Expected:**
- ❌ Error message displays
- Red background with alert icon
- Message: "Failed to load version history"

3. Restart backend:
   ```powershell
   docker start synapse-backend
   ```

**Test 6.2 - Invalid Asset:**

1. Manually navigate to invalid asset ID in URL
2. Open DevTools Console (F12) - check for errors

**Expected:**
- Graceful error handling
- No console errors breaking the app

---

## 🔍 Visual Regression Checks

### UI Appearance

**Tab Button:**
- ✅ History icon (14px) displays correctly
- ✅ Text: "Version History"
- ✅ Active state: Teal underline border
- ✅ Inactive state: Transparent border, gray text
- ✅ Hover: Smooth transition

**Version Cards:**
- ✅ Border: Slate gray (#334155)
- ✅ Hover: Border color lightens
- ✅ Background: Dark slate
- ✅ Spacing: Consistent padding
- ✅ Badges: Blue background for version number
- ✅ Buttons: Proper spacing and sizing

**Diff View:**
- ✅ Fixed to top of version list
- ✅ Dark background distinguishes from versions
- ✅ Color coding clear and readable
- ✅ Monospace font for values

---

## 🧪 Backend API Verification

### Test API Endpoints Directly

**1. Get Version History:**

```bash
curl -X GET "http://localhost:8001/api/v1/workflow/assets/{asset_id}/versions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Project-ID: YOUR_PROJECT_ID"
```

**Expected Response:**
```json
{
  "versions": [
    {
      "version": 1,
      "created_at": "2025-11-28T10:30:00Z",
      "created_by": "admin@axoiq.com",
      "change_source": "csv_import",
      "change_reason": "Initial import",
      "snapshot": { "tag": "FT-101", ... }
    }
  ]
}
```

**2. Get Version Diff:**

```bash
curl -X GET "http://localhost:8001/api/v1/workflow/assets/{asset_id}/diff?from_version=1&to_version=2" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Project-ID: YOUR_PROJECT_ID"
```

**Expected Response:**
```json
{
  "changes": [
    {
      "field": "description",
      "old_value": "Flow Transmitter",
      "new_value": "Flow Transmitter - Updated",
      "change_type": "modified"
    }
  ]
}
```

**3. Rollback Version:**

```bash
curl -X POST "http://localhost:8001/api/v1/workflow/assets/{asset_id}/rollback" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Project-ID: YOUR_PROJECT_ID" \
  -H "Content-Type: application/json" \
  -d '{"target_version": 2}'
```

**Expected Response:**
```json
{
  "message": "Asset rolled back successfully",
  "new_version": 5,
  "restored_from_version": 2
}
```

---

## 📊 Test Data Setup

### Create Test Versions Manually

**Option 1 - Via CSV Import:**

1. Import BBA.csv with initial assets
   - Navigate to http://localhost:4000/ingestion
   - Upload CSV file
   - This creates version 1 for all assets

2. Re-import same CSV with modified values
   - Edit description or other fields
   - This creates version 2

**Option 2 - Via Asset Edit:**

1. Go to Engineering Explorer
2. Select asset
3. Go to "Datasheet" tab
4. Edit any field
5. Save changes
6. Each save creates a new version

**Option 3 - Via Rule Execution:**

1. Create a rule that modifies assets
2. Execute the rule
3. Rule creates new versions with `change_source = "rule_execution"`

---

## 🐛 Known Issues / Edge Cases

### Issue 1: ProjectId Missing
**Symptom:** Empty state shows "requires project context"
**Cause:** EngineeringExplorer didn't pass `currentProject?.id`
**Status:** ✅ Fixed - projectId now passed correctly

### Issue 2: API Import Path
**Symptom:** Build error "apiClient not found"
**Cause:** Wrong import syntax (named vs default export)
**Status:** ✅ Fixed - using `import apiClient from '...'`

### Edge Case: No Versions
**Behavior:** Newly created assets (not imported) may have no versions
**Expected:** Empty state displays correctly

---

## 📸 Screenshots to Capture

For documentation, capture these screenshots:

1. **Version List View**
   - Multiple versions showing
   - Highlight version badges, timestamps

2. **Expanded Version**
   - Snapshot JSON visible
   - Chevron icon indicating collapse

3. **Diff Comparison**
   - Two versions compared
   - Changes highlighted with colors

4. **Rollback Confirmation**
   - Browser confirmation dialog

5. **Empty State**
   - "No version history available"

6. **Error State**
   - Network error message

---

## ✅ Acceptance Criteria

### Must Pass:

- [ ] Version list loads for assets with history
- [ ] Empty state shows for assets without history
- [ ] Version cards expand/collapse on click
- [ ] Compare shows accurate diff between versions
- [ ] Rollback creates new version with old data
- [ ] Loading states display during API calls
- [ ] Error messages show for network failures
- [ ] Tab integrates seamlessly with existing tabs
- [ ] No console errors during normal operation
- [ ] Mobile responsive (optional - check on narrow screen)

### Performance:

- [ ] Version list loads in < 2 seconds
- [ ] Expanding version is instant (< 100ms)
- [ ] Compare loads diff in < 1 second
- [ ] UI remains responsive during operations

### Accessibility:

- [ ] Tab navigation works with keyboard
- [ ] Buttons have hover states
- [ ] Color contrast meets WCAG standards
- [ ] Screen reader labels present (optional)

---

## 🔧 Troubleshooting

### Problem: Version History Tab Not Visible

**Solution:**
1. Verify you're viewing an **asset** (not a location/folder)
2. Check browser console for errors
3. Verify `projectId` is being passed to AssetDetails

### Problem: "No version history" for ALL assets

**Solution:**
1. Check backend is running: http://localhost:8001/docs
2. Verify database has `asset_versions` table
3. Check backend logs for errors:
   ```powershell
   docker logs synapse-backend -f
   ```

### Problem: Compare/Rollback Not Working

**Solution:**
1. Check network tab in DevTools (F12)
2. Verify API endpoints return 200 OK
3. Check authorization token is valid
4. Verify `X-Project-ID` header is sent

---

## 📝 Test Report Template

```markdown
# Asset History Integration - Test Report

**Tester:** [Your Name]
**Date:** YYYY-MM-DD
**Environment:** Development / Local
**Browser:** Chrome / Firefox / Edge

## Test Results

| Scenario | Status | Notes |
|----------|--------|-------|
| View version history | ✅ Pass / ❌ Fail | |
| Expand version snapshot | ✅ Pass / ❌ Fail | |
| Compare versions | ✅ Pass / ❌ Fail | |
| Rollback version | ✅ Pass / ❌ Fail | |
| Loading states | ✅ Pass / ❌ Fail | |
| Error handling | ✅ Pass / ❌ Fail | |

## Issues Found

1. **[Issue Title]**
   - Severity: Critical / High / Medium / Low
   - Steps to reproduce:
   - Expected:
   - Actual:
   - Screenshot:

## Overall Assessment

- ✅ Ready for production
- ⚠️ Minor issues - can proceed with notes
- ❌ Blocking issues - needs fixes

**Comments:**
[Your feedback here]
```

---

## 🚢 Next Steps After Testing

1. **If tests pass:**
   - Update `test-status.md` - mark Manual Test as ✅
   - Create git commit
   - Move to next priority (Demo data / CI setup)

2. **If tests fail:**
   - Document issues in `.dev/issues/`
   - Create GitHub issue (if applicable)
   - Fix bugs and re-test

---

## 📚 Related Documentation

- **Backend Workflow API:** [apps/synapse/backend/app/api/endpoints/workflow.py](../../../apps/synapse/backend/app/api/endpoints/workflow.py)
- **AssetHistory Component:** [apps/synapse/frontend/src/components/AssetHistory.tsx](../../../apps/synapse/frontend/src/components/AssetHistory.tsx)
- **AssetDetails Integration:** [apps/synapse/frontend/src/components/AssetDetails.tsx](../../../apps/synapse/frontend/src/components/AssetDetails.tsx)
- **Test Status Tracker:** [.dev/testing/test-status.md](./test-status.md)

---

**Version:** 1.0
**Last Updated:** 2025-11-28
**Author:** ATLAS AI Assistant
