# First Steps

Learn the basics of using SYNAPSE in 10 minutes.

---

## Prerequisites

✅ You've completed [Installation](01-installation.md)  
✅ SYNAPSE is running (http://localhost:4000)

---

## 1. Login

1. Navigate to http://localhost:4000
2. Enter credentials:
   - Email: `admin@aurumax.com`
   - Password: `admin123!`
3. Click **Login**

**You'll be redirected to the dashboard.**

---

## 2. Select Project

After login, you'll see the **Project Selector**.

**Available projects (seeded data):**
- **GoldMine Phase 1** - Has 12 sample assets
- **Test Import Project** - Empty (for testing imports)

**Select "GoldMine Phase 1"** to work with sample data.

---

## 3. Navigate the UI

### Top Bar
- **Client** dropdown - Switch between clients
- **Project** dropdown - Switch between projects
- **User** menu - Account, logout

### Left Panel (Navigation)
- **Dashboard** - Overview, stats
- **Engineering Explorer** - Browse assets
- **Rules Management** - View/edit rules
- **Ingestion** - Import data
- **Cables** - View cable schedules

### Main Area
- **AG Grid** - Asset tables with filters, sorting
- **Detail Panel** - Asset properties when selected
- **DevConsole** (bottom) - Real-time logs

---

## 4. Browse Assets

1. Click **Engineering Explorer** in left panel
2. You'll see a grid with 12 assets:
   - Pumps (210-PP-001, 210-PP-002, 210-PP-003)
   - Motors (210-M-001, 210-M-002, 210-M-003)
   - Cables (C-210-PP-001-M-001, etc.)

**Try this:**
- Click on any asset row → Detail panel opens
- Use **Search** box to filter  
- Click column headers to sort
- Right-click columns → Show/hide columns

---

## 5. View Rules

1. Click **Rules Management** in left panel
2. You'll see ~14 baseline rules

**Rule examples:**
- **FIRM: Centrifugal Pumps require Electric Motor** (priority 10)
- **COUNTRY-CA: 600V Standard Voltage** (priority 30)

**Each rule shows:**
- Name, description
- Source (FIRM, COUNTRY, PROJECT, CLIENT)
- Priority (higher wins conflicts)
- Condition (when it applies)
- Action (what it does)

---

## 6. Execute Your First Rule

Let's create a new pump and watch rules auto-complete it:

### Step 1: Add New Asset

1. In **Engineering Explorer**, click **+ Add Asset** button
2. Fill in:
   - Tag: `210-PP-999`
   - Description: `Test Centrifugal Pump`
   - Type: `PUMP`
   - Area: `210`
3. Click **Save**

### Step 2: Execute Rules

1. With asset selected, click **Execute Rules** button
2. Watch **DevConsole** (bottom panel) show:
   ```
   [INFO] Loaded 14 rules
   [INFO] Rule "Centrifugal Pumps require Electric Motor" matched
   [INFO] Created child motor: 210-M-999
   [INFO] Created cable: C-210-PP-999-M-999
   ```

### Step 3: Verify Results

1. Refresh asset grid
2. You should now see:
   - `210-PP-999` (your pump)
   - `210-M-999` (auto-created motor)
   - `C-210-PP-999-M-999` (auto-created cable)

**🎉 That's the power of SYNAPSE!** Rules automated asset completion.

---

## 7. Import Sample Data (Optional)

Want to try importing P&ID data?

1. Click **Ingestion** in left panel
2. Click **Choose File** button
3. Select `apps/synapse/backend/data/sample_pid_import.csv`
4. Click **Import**
5. Watch DevConsole process 20 assets
6. Rules auto-execute → ~60 assets created total

---

## 8. Explore Cables

1. Click **Cables** in left panel
2. View auto-generated cable schedule
3. Each cable shows:
   - Tag (e.g., C-210-PP-001-M-001)
   - From/To assets
   - Cable type, size, length

**Try this:**
- Export to Excel (click **Export** button)
- Filter cables by area

---

## 9. Use Prisma Studio (DB Explorer)

Want to see the raw database?

1. Open http://localhost:5555
2. Browse tables:
   - `assets` - All engineering assets
   - `cables` - Generated cables
   - `rule_definitions` - Automation rules
3. Run queries, edit data (dev only!)

---

## 10. DevConsole Tips

The **DevConsole** (bottom panel) shows real-time logs:

**Log levels:**
- `[INFO]` - Normal operations
- `[WARNING]` - Potential issues
- `[ERROR]` - Problems
- `[DEBUG]` - Detailed traces

**Try this:**
- Click **Clear** to reset logs
- Use **Search** to filter logs
- Click **Export** to save logs

---

## Next Steps

✅ **You've learned the basics!**

**Continue to:**
- **[Architecture Overview](03-architecture-overview.md)** - Understand how it works

**For developers:**
- **[Project Structure](../developer-guide/01-project-structure.md)** - Dive into code
- **[Backend Guide](../developer-guide/02-backend-guide.md)** - Add features

---

## Common Questions

**Q: Where's my data stored?**  
A: PostgreSQL database in forge-postgres container (port 5433)

**Q: Can I edit rules?**  
A: Yes! Go to Rules Management → Click rule → Edit (future feature in UI)

**Q: How do I add custom properties?**  
A: Properties are flexible JSON. See [Backend Guide](../developer-guide/02-backend-guide.md)

**Q: Can I deploy this?**  
A: Yes! See [Deployment Guide](../developer-guide/06-deployment.md)

---

**Need help?** Check [Troubleshooting](01-installation.md#troubleshooting) or ask in discussions.
