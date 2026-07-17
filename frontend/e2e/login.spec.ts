import { test, expect } from '@playwright/test';

test.describe('NCERT Math Assistant E2E', () => {
  test('should load the login page and prompt for sign in', async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await expect(page).toHaveTitle(/Vite \+ React/i);
    await expect(page.locator('text=Advanced Math Assistant')).toBeVisible();
    await expect(page.locator('button:has-text("Sign in with Google")')).toBeVisible();
  });
});
