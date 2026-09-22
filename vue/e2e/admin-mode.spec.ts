import { accessToken, expect, test } from './fixtures';
import { playwrightBaseURL } from './base-url';
import { installStoredLocale, expectNoHorizontalOverflow } from './locale';

for (const [locale, width] of [['ja', 375], ['en', 1440]] as const) {
  test(`${locale}: モード切替で管理用readと操作・routeを切り替える`, async ({ api: _api, page, context }) => {
    // モード往復と再読込による復元を同じbrowser sessionで確認する。
    test.setTimeout(60_000);
    await context.addCookies([{ name: 'accessToken', url: playwrightBaseURL, value: accessToken }]);
    await installStoredLocale(page, locale);
    await page.setViewportSize({ width, height: 900 });
    await page.route('**/api/storages/pools?*', route => route.fulfill({ json: [] }));
    await page.route('**/api/networks/pools?*', route => route.fulfill({ json: [] }));
    const requests: URL[] = [];
    page.on('request', request => {
      const url = new URL(request.url());
      if (['/api/vms', '/api/dashboard', '/api/tasks/incomplete'].includes(url.pathname)) requests.push(url);
    });
    await page.goto('/vms');
    const mode = page.getByTestId('admin-mode-switch').locator('input');
    await expect(mode).not.toBeChecked();
    await expect(page.locator('header')).toContainText(locale === 'ja' ? '一般モード' : 'General mode');
    await expect(page.getByTestId('vm-admin-create-open')).toHaveCount(0);
    await expect.poll(() => requests.some(url => url.pathname === '/api/vms')).toBe(true);
    expect(requests.every(url => url.searchParams.get('admin') === 'false')).toBe(true);
    await expectNoHorizontalOverflow(page);

    await mode.focus();
    await mode.press('Space');
    await expect(page).toHaveURL(/\/$/);
    await expect(mode).toBeChecked();
    await expect(page.locator('header')).toContainText(locale === 'ja' ? '管理者権限モード' : 'Administrator mode');
    await page.goto('/vms');
    await expect(page.getByTestId('vm-admin-create-open')).toBeVisible();
    await expect.poll(() => requests.some(url => url.pathname === '/api/vms' && url.searchParams.get('admin') === 'true')).toBe(true);
    await expectNoHorizontalOverflow(page);

    await page.goto('/resource-pools');
    await expect(page).toHaveURL(/\/resource-pools$/);
    await mode.uncheck();
    await expect(page).toHaveURL(/\/$/);
    await expect(mode).not.toBeChecked();
    requests.length = 0;
    await page.goto('/vms');
    await expect(page.getByTestId('vm-admin-create-open')).toHaveCount(0);
    await expect.poll(() => requests.some(url => url.pathname === '/api/vms')).toBe(true);
    expect(requests.every(url => url.searchParams.get('admin') === 'false')).toBe(true);
    await page.goto('/resource-pools');
    await expect(page).toHaveURL(/\/$/);
  });
}

test('非管理者にはswitchも管理専用routeも提供しない', async ({ api: _api, page, context }) => {
  const payload = Buffer.from(JSON.stringify({ sub: 'member', scopes: ['user'], projects: [], exp: 4102444800 })).toString('base64url');
  await context.addCookies([{ name: 'accessToken', url: playwrightBaseURL, value: `${accessToken.split('.')[0]}.${payload}.signature` }]);
  await page.goto('/users');
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByTestId('admin-mode-switch')).toHaveCount(0);
});
