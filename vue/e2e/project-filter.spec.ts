import { expect, test } from './fixtures'
import { installStoredLocale } from './locale'

const projectTitle = 'Project E2E (#a1b2c3)'

for (const resource of ['vms', 'nodes', 'storages', 'images', 'networks']) {
  test(`${resource}: App barの選択と解除で一覧を更新する`, async ({ authenticatedPage: page }) => {
    await page.goto(`/${resource}?nameLike=demo`)
    const selector = page.locator('header').getByRole('textbox', { name: 'Project', exact: true })
    await expect(selector).toBeVisible()
    await expect(page.locator('main').getByRole('textbox', { name: 'Project', exact: true })).toHaveCount(0)

    const filtered = page.waitForRequest(request => {
      const url = new URL(request.url())
      return url.pathname === `/api/${resource}` && url.searchParams.get('projectId') === 'a1b2c3'
    })
    await selector.focus()
    await selector.press('Enter')
    await page.getByRole('option', { name: projectTitle }).click()
    await filtered
    await expect(page).toHaveURL(new RegExp(`/${resource}\\?nameLike=demo&projectId=a1b2c3$`))

    const cleared = page.waitForRequest(request => {
      const url = new URL(request.url())
      return url.pathname === `/api/${resource}` && !url.searchParams.has('projectId')
    })
    await page.locator('header').getByRole('button', { name: 'Clear Project' }).click()
    await cleared
    await expect(page).toHaveURL(new RegExp(`/${resource}\\?nameLike=demo$`))
  })
}

test('サイドナビゲーション・再読込・履歴でProject選択を保持する', async ({ authenticatedPage: page }) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto('/vms?projectId=a1b2c3')
  await expect(page.locator('header')).toContainText(projectTitle)
  await page.getByRole('link', { name: 'Nodes', exact: true }).click()
  await expect(page).toHaveURL(/\/nodes\?projectId=a1b2c3$/)
  await page.reload()
  await expect(page.locator('header')).toContainText(projectTitle)
  await page.getByRole('link', { name: 'Projects', exact: true }).click()
  await expect(page.locator('header').getByRole('textbox', { name: 'Project', exact: true })).toHaveCount(0)
  await page.getByRole('link', { name: 'Storage', exact: true }).click()
  await expect(page).toHaveURL(/\/storages\?projectId=a1b2c3$/)
  await page.goBack()
  await page.goBack()
  await expect(page).toHaveURL(/\/nodes\?projectId=a1b2c3$/)
  await expect(page.locator('header')).toContainText(projectTitle)
})

for (const width of [375, 600, 1440]) {
  test(`${width}px: 長い日本語Project名でもApp barの操作を表示する`, async ({ authenticatedPage: page }) => {
    await installStoredLocale(page, 'ja')
    await page.setViewportSize({ width, height: 900 })
    const title = '長いプロジェクト名と識別子を確認するための共同管理環境'
    await page.route('**/api/projects?*', route => route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({ count: 1, data: [{ id: 'a1b2c3', name: title }] }),
    }))
    await page.goto('/nodes?projectId=a1b2c3')
    const bar = page.locator('header')
    const selector = bar.getByRole('textbox', { name: 'プロジェクト', exact: true })
    await expect(selector).toBeVisible()
    await expect(bar).toContainText(`${title} (#a1b2c3)`)
    await expect(bar.getByRole('button', { name: 'ログアウト', exact: true })).toBeVisible()
    const bounds = await selector.boundingBox()
    expect(bounds).not.toBeNull()
    expect(bounds!.x).toBeGreaterThanOrEqual(0)
    expect(bounds!.x + bounds!.width).toBeLessThanOrEqual(width)
    await selector.focus()
    await selector.press('Enter')
    await expect(page.getByRole('option', { name: `${title} (#a1b2c3)` })).toBeVisible()
    await selector.press('Escape')
    await expect(selector).toBeFocused()
    const fieldBounds = await selector.evaluate(element => {
      const field = element.closest('.v-input')!.getBoundingClientRect()
      const header = element.closest('header')!.getBoundingClientRect()
      return { top: field.top - header.top, bottom: header.bottom - field.bottom }
    })
    expect(fieldBounds.top).toBeGreaterThanOrEqual(0)
    expect(fieldBounds.bottom).toBeGreaterThanOrEqual(0)
  })
}
