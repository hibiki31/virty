import type { Page } from '@playwright/test';
import { expect, test, accessToken } from './fixtures';
import { installStoredLocale } from './locale';
import { playwrightBaseURL } from './base-url';

const publickey = 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6MDEyMzQ1';
type User = { username: string; scopes: { name: string }[]; projects: []; publickeys: { name: string; publickey: string }[] };
const member = (): User => ({ username: 'alice', scopes: [{ name: 'user' }, { name: 'future.scope' }], projects: [], publickeys: [] });

async function installUsers(page: Page) {
  const users = new Map<string, User>([['operator', { ...member(), username: 'operator', scopes: [{ name: 'admin' }] }]]);
  const state = { failCreate: true, failDelete: true, failKeys: true, failPassword: true, writes: [] as { path: string; body: Record<string, unknown> }[] };
  await page.route('**/api/users**', async route => {
    const request = route.request();
    const path = decodeURIComponent(new URL(request.url()).pathname);
    const method = request.method();
    const body = method === 'PUT' || method === 'POST' ? request.postDataJSON() : {};
    if (method !== 'GET') state.writes.push({ path, body });
    const failure = (code: string, status = 409) => route.fulfill({ status, json: { detail: { code, message: code } } });
    if (path === '/api/users/scopes') return route.fulfill({ json: ['user', 'admin', 'vm.create'] });
    if (path === '/api/users/me') return route.fulfill({ json: { ...member(), id: 'operator', username: 'operator', scopes: ['user'], publickeys: [{ name: 'laptop', publickey }] } });
    if (path === '/api/users/me/publickeys') {
      if (state.failKeys) { state.failKeys = false; return failure('service_unavailable', 503); }
      return route.fulfill({ json: { ...member(), id: 'operator', username: 'operator', scopes: ['user'], publickeys: body.publickeys } });
    }
    if (path === '/api/users/me/password') {
      if (state.failPassword) { state.failPassword = false; return failure('password_reauthentication_failed', 403); }
      return route.fulfill({ status: 204 });
    }
    if (path.startsWith('/api/users/detail/')) return route.fulfill({ json: users.get(path.split('/').pop()!) });
    if (path.endsWith('/reset-password')) return route.fulfill({ status: 204 });
    if (path === '/api/users' && method === 'GET') return route.fulfill({ json: { count: users.size, data: [...users.values()] } });
    if (path === '/api/users' && method === 'POST') {
      if (state.failCreate) { state.failCreate = false; return failure('user_exists', 400); }
      const user = { ...body, projects: [] } as User;
      users.set(user.username, user);
      return route.fulfill({ json: user });
    }
    const name = path.split('/').pop()!;
    if (method === 'PUT') {
      const user = { ...users.get(name)!, ...body };
      users.set(name, user);
      return route.fulfill({ json: user });
    }
    if (method === 'DELETE') {
      if (state.failDelete) { state.failDelete = false; return failure('last_project_member_required'); }
      users.delete(name);
      return route.fulfill({ json: 1 });
    }
    return route.fallback();
  });
  return { state, users };
}

for (const locale of ['en', 'ja'] as const) {
  test(`${locale}: user作成・編集・再設定・削除と失敗からの再試行`, async ({ authenticatedPage: page }) => {
    await installStoredLocale(page, locale);
    await page.setViewportSize({ width: locale === 'ja' ? 375 : 1024, height: 900 });
    const { state, users } = await installUsers(page);
    await page.goto('/users');
    await page.getByTestId('user-create').click();
    const dialog = page.getByRole('dialog');
    await expect(dialog.getByTestId('user-name').locator('input')).toBeEnabled();
    await page.keyboard.press('Escape');
    await expect(dialog).not.toBeVisible();
    await expect(page.getByTestId('user-create')).toBeFocused();
    await page.getByTestId('user-create').click();
    await dialog.getByTestId('user-name').locator('input').fill('alice');
    await dialog.getByTestId('new-password').locator('input').fill('Virty-Test_2026!');
    await dialog.getByTestId('confirm-password').locator('input').fill('Virty-Test_2026!');
    await dialog.getByTestId('add-public-key').click();
    await dialog.getByTestId('key-name-0').locator('input').fill('laptop');
    await dialog.getByTestId('key-value-0').locator('textarea').first().fill(publickey);
    await dialog.getByTestId('user-submit').click();
    await expect(dialog.getByTestId('user-error')).toContainText(locale === 'ja' ? 'すでに存在' : 'already exists');
    await expect(dialog.getByTestId('user-name').locator('input')).toHaveValue('alice');
    await dialog.getByTestId('user-submit').click();
    await expect(dialog).not.toBeVisible();
    expect(users.get('alice')!.publickeys[0].name).toBe('laptop');
    users.get('alice')!.scopes.push({ name: 'future.scope' });
    await page.getByTestId('user-edit-alice').click();
    await expect(dialog.getByTestId('user-name').locator('input')).toHaveAttribute('readonly');
    await dialog.getByTestId('key-name-0').locator('input').fill('workstation');
    page.once('dialog', prompt => prompt.dismiss());
    await page.keyboard.press('Escape');
    await expect(dialog).toBeVisible();
    await dialog.getByTestId('user-submit').click();
    await expect(dialog).not.toBeVisible();
    expect(users.get('alice')!.scopes).toContainEqual({ name: 'future.scope' });
    expect(users.get('alice')!.publickeys[0].name).toBe('workstation');
    const row = page.locator('tr').filter({ has: page.getByTestId('user-edit-alice') });
    await row.getByRole('button', { name: locale === 'ja' ? 'パスワード再設定' : 'Reset password' }).click();
    await dialog.getByTestId('new-password').locator('input').fill('Virty-New_2026!');
    await dialog.getByTestId('confirm-password').locator('input').fill('Virty-New_2026!');
    await dialog.getByTestId('user-submit').click();
    await expect(dialog).not.toBeVisible();
    expect(state.writes.some(write => write.path.endsWith('/alice/reset-password'))).toBe(true);
    await page.getByTestId('user-delete-alice').click();
    await dialog.getByTestId('user-delete-confirm').locator('input').check();
    await dialog.getByTestId('user-submit').click();
    await expect(dialog.getByTestId('user-error')).toBeVisible();
    await dialog.getByTestId('user-submit').click();
    await expect(dialog).not.toBeVisible();
    await expect(page.getByTestId('user-edit-alice')).toHaveCount(0);
    await expect(page.getByTestId('user-delete-operator')).toBeDisabled();
  });
}

test('非管理者の本人設定、日英切替、文字拡大、公開鍵とpassword変更', async ({ authenticatedPage: page, context }) => {
  const payload = Buffer.from(JSON.stringify({ sub: 'operator', scopes: ['user', 'vm.create'], projects: [], exp: 4102444800 })).toString('base64url');
  await context.addCookies([{ name: 'accessToken', url: playwrightBaseURL, value: `${accessToken.split('.')[0]}.${payload}.signature` }]);
  const { state } = await installUsers(page);
  await installStoredLocale(page, 'en');
  await page.setViewportSize({ width: 375, height: 900 });
  await page.goto('/account');
  await expect(page.getByTestId('key-name-0').locator('input')).toHaveValue('laptop');
  await page.getByTestId('locale-switcher-compact').click();
  await page.getByTestId('locale-switcher-option-ja').click();
  await expect(page).toHaveTitle('Virty - アカウント設定');
  await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
  await expect(page.getByTestId('account-save-keys')).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
  expect(overflow).toBe(false);
  await page.getByTestId('key-name-0').locator('input').fill('new-laptop');
  page.once('dialog', prompt => prompt.dismiss());
  await page.getByRole('button', { name: 'ログアウト', exact: true }).click();
  await expect(page).toHaveURL(/\/account$/);
  expect((await context.cookies()).some(cookie => cookie.name === 'accessToken')).toBe(true);
  await page.getByTestId('account-save-keys').click();
  await expect(page.getByTestId('account-keys-error')).toBeVisible();
  await expect(page.getByTestId('key-name-0').locator('input')).toHaveValue('new-laptop');
  await page.getByTestId('account-save-keys').click();
  await expect(page.getByTestId('account-save-keys')).toBeDisabled();
  expect(state.writes.filter(write => write.path.endsWith('/publickeys')).every(write => Object.keys(write.body).join() === 'publickeys')).toBe(true);
  await page.getByTestId('current-password').locator('input').fill('Wrong-Test_2026!');
  await page.getByTestId('new-password').locator('input').fill('Virty-New_2026!');
  await page.getByTestId('confirm-password').locator('input').fill('Virty-New_2026!');
  await page.getByTestId('account-change-password').click();
  await expect(page.getByTestId('account-password-error')).toBeVisible();
  await expect(page).toHaveURL(/\/account$/);
  await page.getByTestId('current-password').locator('input').fill('Virty-Test_2026!');
  await page.getByTestId('account-change-password').click();
  await expect(page).toHaveURL(/\/login$/);
  expect((await context.cookies()).some(cookie => cookie.name === 'accessToken')).toBe(false);
});
