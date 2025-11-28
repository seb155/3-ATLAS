# Using the Developer Console

**For**: Engineers, Project Managers, Developers

---

## Opening the DevConsole

**Keyboard Shortcut**: `Ctrl + \`

**Or**: Click the console icon in the top-right toolbar

---

## Interface Overview

The DevConsole has **two panels**:

```
┌─────────────────────────────────────────────┐
│  [Filters]  [Search]  [● Live]              │
├──────────────┬──────────────────────────────┤
│  TIMELINE    │  DETAILS                     │
│              │                              │
│  ● Import... │  Overview  Payload  Stack    │
│  ● Rules...  │                              │
│              │  [Selected item details]     │
│              │                              │
└──────────────┴──────────────────────────────┘
```

**Timeline** (Left): List of your actions  
**Details** (Right): Info about selected action

---

## Timeline: Your Activity Feed

### What You'll See

Actions are displayed as **workflows**:

```
● 17:02:15                          [●●●●●○○○○○] 50%
  Import Gold Mine
  └─ Job 2/4 running · 15 items · 4.1s
```

**Status Indicators**:
- ✅ **Green dot**: Completed successfully
- 🟣 **Purple dot (pulsing)**: Currently running
- 🔴 **Red dot**: Failed

### Expand to See Details

Click the **▼** icon to see job details:

```
● 17:02:15 - Import Gold Mine
  ├─ ✓ Fetch External Assets      2.3s
  ├─ ▶ Process Data                Running...
  ├─ ⏸ Update Database             Pending
  └─ ⏸ Generate Cables             Pending
```

### Click to Navigate

Click on **entity tags** (like `P-101`) to open that item:

```
✓ Created P-101  ← Click here to open P-101
```

---

## Details Panel: Dive Deeper

When you click on an action in the Timeline, the **Details panel** shows:

### Overview Tab
Summary information:
- Who did the action
- When it happened
- How long it took
- How many items were created/updated

### Payload Tab
Technical details in JSON format.

**Features**:
- **Click values** to navigate (e.g., `assetId: "123"` → opens asset)
- **Search** to filter the data
- **Copy** button to copy the data

### Timeline Tab
Visual representation of the workflow jobs.

### Stack Tab
(Only for errors) Shows the error details and stack trace.

---

## Filtering Your Activity

### Quick Filters

**Time**:
- `ALL` - Everything
- `5M` - Last 5 minutes
- `15M` - Last 15 minutes  
- `1H` - Last hour
- `24H` - Last 24 hours

**Level**:
- `ERROR` - Only errors
- `WARN` - Warnings and errors
- `INFO` - Most events
- `DEBUG` - Everything (Dev mode only)

**Topics**:
- `ASSETS` - Asset-related actions
- `RULES` - Rule executions
- `CABLES` - Cable generation
- `IMPORT` - Data imports

**Scope**:
- `MY` - Only your actions
- `ALL` - Everyone's actions

### Preset Filters

Click the **Quick Filters** dropdown for common combinations:
- **My Recent Changes**: Your recent edits (last 15 minutes)
- **Errors Only**: Only failed actions
- **Rule Executions**: All rule-related activity

---

## User Mode vs Dev Mode

### User Mode (Default) 👤
**For**: Day-to-day work

**Shows**:
- Your important actions (imports, rules, exports)
- Simple, clear messages
- Only what you need to see

**Hides**:
- System logs
- Network requests
- Debug messages

---

### Dev Mode 🔧
**For**: Debugging, troubleshooting

**Shows**:
- Everything (all logs, all levels)
- Technical details
- Performance metrics
- Raw payloads

**Toggle**: Click the mode button in the top-left  
`[👤 User]` ↔ `[🔧 Dev]`

---

## Common Tasks

### 1. Check Import Status

1. Open DevConsole (`Ctrl + \`)
2. Look for your import in the Timeline
3. Check the status:
   - ✅ **Green**: Import completed
   - 🟣 **Purple (pulsing)**: Still running
   - 🔴 **Red**: Something failed

4. If failed, click the item to see error details

---

### 2. Find Out What Went Wrong

1. Filter by `ERROR` level
2. Click the failed action
3. Go to **Stack** tab to see the error
4. Copy error details to share with support

---

### 3. See What Rules Were Applied

1. Filter by `RULES` topic
2. Expand the rule execution workflow
3. See which assets were affected
4. Click entity tags to review changes

---

### 4. Navigate to an Entity

When you see an entity tag in the logs (e.g., `P-101`):
1. Click the tag in the Timeline
2. **OR** select the log and click `[View Asset →]` in Details panel

The asset detail page will open.

---

### 5. Copy Log Data

**Single log**:
- Hover over log → Click **Copy** icon

**All visible logs**:
- Click **Export** button → Choose format:
  - Plain text
  - JSON (for technical support)
  - CSV (for Excel)

---

### 6. Share Activity with Support

1. Filter to show the problem (e.g., last 15 minutes, errors only)
2. Click **Export** → JSON
3. Attach the file to your support request

---

## Panel Controls

### Resize the Panel
Drag the **edge** of the panel to resize it.

### Move the Panel
Click the **dock icon** to switch positions:
- Bottom (default, horizontal)
- Right (vertical)

### Close the Panel
- Press `Ctrl + \`
- **OR** Click the **X** button

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + \` | Open/Close DevConsole |
| `↑ / ↓` | Navigate timeline |
| `Enter` | Expand selected item |
| `c` | Copy selected log |
| `Esc` | Clear selection |
| `/` | Focus search bar |

---

## Tips & Tricks

### 💡 Tip 1: Keep Console Open
Keep the DevConsole open while working to see:
- Rule execution results in real-time
- Import progress
- Any errors immediately

### 💡 Tip 2: Use Time Filters
When looking for something recent, use **5M** or **15M** filters instead of scrolling through everything.

### 💡 Tip 3: Quick Navigation
Double-click an entity tag to open it quickly.

### 💡 Tip 4: Export Before Big Changes
Before running major operations (bulk imports, mass rule executions):
1. Export current logs
2. Run the operation
3. If something goes wrong, you have the "before" state

### 💡 Tip 5: Search in Payload
In the **Payload** tab, use the search box to find specific data:
- Search for asset tags: `P-101`
- Search for values: `active`
- Search for IDs: `abc123`

---

## Troubleshooting

### Console Won't Open
- **Fix**: Refresh the page, try again

### Logs Not Updating
- **Check**: WebSocket status in top-right
- If **Offline**, the console will auto-reconnect in 3 seconds
- If still offline after 10 seconds, refresh the page

### Too Many Logs
- **Use filters** to narrow down what you see
- Switch to **User Mode** to hide technical logs
- Use **Time filter** (15M or 1H) instead of ALL

### Can't Find My Action
- Check **User filter**: Make sure it's on `MY` (not `ALL`)
- Check **Time filter**: Increase to `1H` or `24H`
- Try **Search**: Type the entity tag or action name

---

## FAQ

**Q: What's the difference between Timeline and Details?**  
**A**: Timeline shows the **list** of actions. Details shows **information** about the selected action.

**Q: Why do some actions have jobs and others don't?**  
**A**: Complex actions (imports, rule executions) are broken into jobs. Simple actions (create asset) are single-step.

**Q: Can I undo an action from the DevConsole?**  
**A**: Some actions show a **Rollback** button in the Details panel. Click it to undo that specific action.

**Q: What does "Live" status mean?**  
**A**: Green "Live" means you're receiving real-time updates. If it's gray, updates are paused (but will reconnect automatically).

**Q: Can I save my filter settings?**  
**A**: Not yet, but it's planned for a future release!

---

**Need Help?** Contact support or see [Developer Guide](../developer-guide/workflow-engine.md) for technical details.
