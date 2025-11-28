import { test, expect } from '@playwright/test';

test('full user journey', async ({ page }) => {
    test.setTimeout(60000);

    // 1. Register and Login
    await test.step('Register and Login', async () => {
        await page.goto('/');

        // Go to Register
        await page.getByText('Need an account? Register').click();

        // Fill Registration Form
        const timestamp = Date.now();
        const email = `testuser_${timestamp}@example.com`;
        await page.getByLabel('Full Name').fill('Test User');
        await page.getByLabel('Email').fill(email);
        await page.getByLabel('Password').fill('password123');

        // Handle Alert
        page.on('dialog', dialog => dialog.accept());
        await page.getByRole('button', { name: 'Register' }).click();

        // Login
        await page.getByLabel('Email').fill(email);
        await page.getByLabel('Password').fill('password123');
        await page.getByRole('button', { name: 'Login' }).click();
    });

    // 2. Create Client and Project
    await test.step('Create Client and Project', async () => {
        // Create Client
        await page.getByText('+ New Client').click();
        await page.getByPlaceholder('Client Name').fill('E2E Test Client');
        await page.getByRole('button', { name: 'Save' }).click();

        // Wait for client to appear
        await expect(page.getByText('E2E Test Client')).toBeVisible();

        // Select Client
        await page.getByText('E2E Test Client').click();

        // Create Project
        await page.getByText('+ New Project').click();
        await page.getByPlaceholder('Project Name').fill('E2E Test Project');
        await page.getByRole('button', { name: 'Save' }).click();

        // Wait for project to appear
        await expect(page.getByText('E2E Test Project')).toBeVisible();

        // Select Project
        await page.getByText('E2E Test Project').click();
    });

    // 3. Verify Dashboard and Navigation
    await test.step('Verify Dashboard and Navigation', async () => {
        // Should be on Dashboard
        await expect(page.getByText('Project Overview: E2E Test Project')).toBeVisible();

        // Navigate to Engineering Explorer
        const engineeringLink = page.getByText('Engineering', { exact: false });
        if (await engineeringLink.isVisible()) {
            await engineeringLink.click();
        } else {
            // Fallback: try to find it or fail
            await expect(engineeringLink).toBeVisible();
        }

        // Verify Asset Grid
        await expect(page.getByText('Export CSV')).toBeVisible();
    });
});
