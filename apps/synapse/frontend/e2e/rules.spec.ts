import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Rules Management
 *
 * Tests the complete rule management workflow from UI to backend.
 */

test.describe('Rules Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to Rules Management page
    await page.goto('http://localhost:5173');

    // Login (if needed)
    // TODO: Adjust based on your auth flow
    // await page.fill('[name="username"]', 'testuser');
    // await page.fill('[name="password"]', 'password');
    // await page.click('button[type="submit"]');

    // Navigate to Rules page
    await page.click('text=Rules Management');
  });

  test('should display rules table', async ({ page }) => {
    // Wait for rules to load
    await page.waitForSelector('table', { timeout: 10000 });

    // Check if table headers are visible
    await expect(page.locator('th:has-text("Rule Name")')).toBeVisible();
    await expect(page.locator('th:has-text("Source")')).toBeVisible();
    await expect(page.locator('th:has-text("Priority")')).toBeVisible();
    await expect(page.locator('th:has-text("Action")')).toBeVisible();
  });

  test('should filter rules by source', async ({ page }) => {
    // Select FIRM source filter
    await page.selectOption('select:near(text="All Sources")', 'FIRM');

    // Wait for filtered results
    await page.waitForTimeout(1000);

    // Check that all visible rules have FIRM badge
    const firmBadges = await page.locator('text=FIRM').count();
    expect(firmBadges).toBeGreaterThan(0);
  });

  test('should search rules by name', async ({ page }) => {
    // Type in search box
    await page.fill('input[placeholder*="Search rules"]', 'motor');

    // Press Enter or click search
    await page.press('input[placeholder*="Search rules"]', 'Enter');

    // Wait for filtered results
    await page.waitForTimeout(1000);

    // Check that results contain "motor" in the name
    const ruleNames = await page.locator('table tbody tr td:nth-child(2)').allTextContents();
    const hasMotor = ruleNames.some(name => name.toLowerCase().includes('motor'));
    expect(hasMotor).toBeTruthy();
  });

  test('should open create rule modal', async ({ page }) => {
    // Click Create Rule button
    await page.click('button:has-text("Create Rule")');

    // Check if modal is visible
    await expect(page.locator('text=Create New Rule')).toBeVisible();

    // Check if form fields are visible
    await expect(page.locator('input[placeholder*="Rule Name"]')).toBeVisible();
    await expect(page.locator('select:near(text="Source")')).toBeVisible();
  });

  test('should create a new rule', async ({ page }) => {
    // Open create modal
    await page.click('button:has-text("Create Rule")');

    // Fill in basic information
    await page.fill('input[placeholder*="Rule Name"]', 'E2E Test Rule');
    await page.fill('textarea', 'This is a test rule created by E2E tests');

    // Select source
    await page.selectOption('select:near(text="Source")', 'FIRM');

    // Select discipline
    await page.selectOption('select:near(text="Discipline")', 'ELECTRICAL');

    // Select action type
    await page.click('button:has-text("Set Property")');

    // Set condition: asset_type = MOTOR
    await page.selectOption('select:near(text="Asset Type")', 'MOTOR');

    // Set action: voltage = 600V
    await page.click('button:has-text("Add Property")');
    await page.fill('input[placeholder*="Property key"]', 'voltage');
    await page.fill('input[placeholder*="Property value"]', '600V');

    // Save rule
    await page.click('button:has-text("Create Rule")');

    // Wait for modal to close and table to refresh
    await page.waitForTimeout(2000);

    // Check if rule appears in table
    await expect(page.locator('text=E2E Test Rule')).toBeVisible();
  });

  test('should edit an existing rule', async ({ page }) => {
    // Wait for rules to load
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // Click edit button on first rule
    await page.click('table tbody tr:first-child button[title="Edit Rule"]');

    // Check if modal is visible
    await expect(page.locator('text=Edit Rule')).toBeVisible();

    // Change rule name
    const nameInput = page.locator('input[placeholder*="Rule Name"]');
    await nameInput.clear();
    await nameInput.fill('Updated Rule Name E2E');

    // Save rule
    await page.click('button:has-text("Update Rule")');

    // Wait for update
    await page.waitForTimeout(2000);

    // Check if updated name appears in table
    await expect(page.locator('text=Updated Rule Name E2E')).toBeVisible();
  });

  test('should toggle rule active status', async ({ page }) => {
    // Wait for rules to load
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // Find first active rule
    const activeRule = page.locator('table tbody tr:has(svg.text-green-500):first');

    // Click toggle button
    await activeRule.locator('button').first().click();

    // Wait for update
    await page.waitForTimeout(1000);

    // Check if status changed (green checkmark -> gray pause)
    const isPaused = await activeRule.locator('svg.text-gray-400').count();
    expect(isPaused).toBeGreaterThan(0);
  });

  test('should delete a rule', async ({ page }) => {
    // Create a test rule first
    await page.click('button:has-text("Create Rule")');
    await page.fill('input[placeholder*="Rule Name"]', 'Rule To Delete');
    await page.selectOption('select:near(text="Source")', 'PROJECT');
    await page.click('button:has-text("Set Property")');
    await page.selectOption('select:near(text="Asset Type")', 'PUMP');
    await page.click('button:has-text("Add Property")');
    await page.fill('input[placeholder*="Property key"]', 'test');
    await page.fill('input[placeholder*="Property value"]', 'delete');
    await page.click('button:has-text("Create Rule")');
    await page.waitForTimeout(2000);

    // Find the rule
    const ruleRow = page.locator('tr:has-text("Rule To Delete")');

    // Listen for confirm dialog
    page.on('dialog', dialog => dialog.accept());

    // Click delete button
    await ruleRow.locator('button[title="Delete Rule"]').click();

    // Wait for deletion
    await page.waitForTimeout(2000);

    // Check if rule is gone
    await expect(page.locator('text=Rule To Delete')).not.toBeVisible();
  });

  test('should preview rule before saving', async ({ page }) => {
    // Open create modal
    await page.click('button:has-text("Create Rule")');

    // Fill in rule
    await page.fill('input[placeholder*="Rule Name"]', 'Preview Test Rule');
    await page.click('button:has-text("Set Property")');
    await page.selectOption('select:near(text="Asset Type")', 'MOTOR');
    await page.click('button:has-text("Add Property")');
    await page.fill('input[placeholder*="Property key"]', 'manufacturer');
    await page.fill('input[placeholder*="Property value"]', 'Rockwell');

    // Click preview button
    await page.click('button:has-text("Preview")');

    // Check if preview is visible
    await expect(page.locator('text=Preview Test Rule')).toBeVisible();
    await expect(page.locator('text=Asset type is "MOTOR"')).toBeVisible();
    await expect(page.locator('text=Set Properties')).toBeVisible();
    await expect(page.locator('text=manufacturer')).toBeVisible();

    // Switch back to edit mode
    await page.click('button:has-text("Edit")');

    // Check if form is visible again
    await expect(page.locator('input[placeholder*="Rule Name"]')).toBeVisible();
  });

  test('should display stats correctly', async ({ page }) => {
    // Check if stats cards are visible
    await expect(page.locator('text=Total Rules')).toBeVisible();
    await expect(page.locator('text=Active Rules')).toBeVisible();
    await expect(page.locator('text=Total Executions')).toBeVisible();
    await expect(page.locator('text=Success Rate')).toBeVisible();

    // Check if numbers are displayed
    const totalRules = await page.locator('text=Total Rules').locator('..').locator('div.text-2xl').textContent();
    expect(parseInt(totalRules || '0')).toBeGreaterThanOrEqual(0);
  });

  test('should validate required fields', async ({ page }) => {
    // Open create modal
    await page.click('button:has-text("Create Rule")');

    // Try to save without filling required fields
    await page.click('button:has-text("Create Rule")');

    // Check if error messages are displayed
    await expect(page.locator('text=Rule name is required')).toBeVisible();
  });
});

test.describe('Rule Condition Builder', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.click('text=Rules Management');
    await page.click('button:has-text("Create Rule")');
  });

  test('should build condition with property filters', async ({ page }) => {
    // Select asset type
    await page.selectOption('select:near(text="Asset Type")', 'PUMP');

    // Add property filter
    await page.click('button:has-text("Add Filter")');

    // Fill in filter
    await page.fill('input[placeholder="Property key"]', 'pump_type');
    await page.selectOption('select', 'Equals');
    await page.fill('input[placeholder="Value"]', 'CENTRIFUGAL');

    // Check if preview button works
    await page.click('button:has-text("Preview")');

    // Verify condition is shown in preview
    await expect(page.locator('text=Asset type is "PUMP"')).toBeVisible();
    await expect(page.locator('text=pump_type')).toBeVisible();
  });

  test('should remove property filter', async ({ page }) => {
    // Select asset type
    await page.selectOption('select:near(text="Asset Type")', 'TANK');

    // Add property filter
    await page.click('button:has-text("Add Filter")');
    await page.fill('input[placeholder="Property key"]', 'capacity');

    // Remove the filter
    await page.click('button[title="Remove filter"]', { force: true });

    // Check if filter is removed
    const filterInputs = await page.locator('input[placeholder="Property key"]').count();
    expect(filterInputs).toBe(0);
  });
});

test.describe('Rule Action Builder', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.click('text=Rules Management');
    await page.click('button:has-text("Create Rule")');
  });

  test('should build CREATE_CHILD action', async ({ page }) => {
    // Select action type
    await page.click('button:has-text("Create Child Asset")');

    // Fill in child type
    await page.fill('input[placeholder*="MOTOR"]', 'MOTOR');

    // Set naming convention
    await page.fill('input[placeholder*="{parent_tag}"]', '{parent_tag}-M');

    // Select relationship
    await page.selectOption('select:near(text="Relationship Type")', 'powers');

    // Add property to inherit
    await page.click('button:has-text("Add Property"):first');
    await page.fill('input[placeholder*="Property name"]', 'area');

    // Add new property
    await page.locator('button:has-text("Add Property")').nth(1).click();
    await page.fill('input[placeholder="Property key"]', 'motor_type');
    await page.fill('input[placeholder="Property value"]', 'Electric');

    // Verify action in preview
    await page.click('button:has-text("Preview")');
    await expect(page.locator('text=Create')).toBeVisible();
    await expect(page.locator('text=MOTOR')).toBeVisible();
  });

  test('should build SET_PROPERTY action', async ({ page }) => {
    // Select action type
    await page.click('button:has-text("Set Property")');

    // Add property
    await page.click('button:has-text("Add Property")');
    await page.fill('input[placeholder*="Property key"]', 'voltage');
    await page.fill('input[placeholder*="Property value"]', '600V');

    // Verify action in preview
    await page.click('button:has-text("Preview")');
    await expect(page.locator('text=Set Properties')).toBeVisible();
    await expect(page.locator('text=voltage')).toBeVisible();
    await expect(page.locator('text=600V')).toBeVisible();
  });
});
