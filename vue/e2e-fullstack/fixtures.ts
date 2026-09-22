import {
  test as base,
  expect,
  type APIRequestContext,
  type Page,
  type Response,
} from "@playwright/test";
import type { components } from "../src/api/openapi";

export type Task = components["schemas"]["Task"];
export type User = { username: string; password: string };
type NamedProject = { id: string; name: string };
export type Seed = {
  users: Record<"admin" | "member" | "outsider", User>;
  projects: Record<"alpha" | "beta", NamedProject>;
  vms: Record<"alpha" | "beta", { uuid: string; name: string }>;
  resources: {
    nodeName: string;
    storageUuid: string;
    storageName: string;
    networkUuid: string;
    networkName: string;
    storagePoolId: number;
    storagePoolName: string;
    networkPoolId: number;
    networkPoolName: string;
    flavorId: number;
    flavorName: string;
    imageName: string;
    imagePath: string;
  };
};

type Diagnostic = {
  operation?: string;
  method?: string;
  path?: string;
  status?: number;
  taskId?: string;
  state?: string | null;
  errorCode?: string | null;
  exceptionType?: string | null;
  frames?: { file: string; line: number }[];
};

type TaskDiagnostic = Pick<Diagnostic, "exceptionType" | "frames">;

export class Fullstack {
  readonly diagnostics: Diagnostic[] = [];
  private readonly diagnosedTasks = new Set<string>();

  constructor(readonly page: Page, readonly request: APIRequestContext) {
    page.on("response", response => {
      const path = new URL(response.url()).pathname.replace(/\/vnc\/[^/]+/, "/vnc/[redacted]");
      if (path.startsWith("/api/")) {
        this.diagnostics.push({ method: response.request().method(), path, status: response.status() });
      }
    });
  }

  async reset(seed: boolean): Promise<Seed> {
    let result: Seed | undefined;
    await expect.poll(async () => {
      const response = await this.request.post("/api/__e2e/reset", { data: { seed }, timeout: 20_000 });
      const status = response.status();
      if (status === 200) result = await response.json() as Seed;
      else if (status !== 409) throw new Error(`E2E初期化に失敗しました (HTTP ${status})`);
      await response.dispose();
      return status;
    }, { message: "workerの完了を待ってDBを独立した前提状態へ戻す", timeout: 30_000, intervals: [250, 500, 1_000] }).toBe(200);
    return result!;
  }

  async control<T>(path: string, data: Record<string, unknown>): Promise<T> {
    const response = await this.request.post(`/api/__e2e/${path}`, { data });
    expect(response.status(), `E2E制御 ${path}`).toBe(200);
    const result = await response.json() as T;
    await response.dispose();
    return result;
  }

  async login(user: User, path = "/vms", options: { adminMode?: boolean } = {}): Promise<void> {
    await this.page.goto(path);
    await expect(this.page).toHaveURL(/\/login\?redirect=/);
    await this.enterCredentials(user);
    await this.expectPath(path);
    if (options.adminMode) await this.enableAdminMode();
  }

  async expectPath(path: string): Promise<void> {
    const destination = new URL(path, this.page.url());
    // redirect query内の/vmsなどを現在のpathnameと誤認しない。
    await expect(this.page).toHaveURL(url =>
      url.pathname === destination.pathname &&
      url.search === destination.search &&
      url.hash === destination.hash,
    );
  }

  async enableAdminMode(): Promise<void> {
    const mode = this.page.getByTestId("admin-mode-switch").locator("input");
    await expect(mode).not.toBeChecked();
    const originalURL = this.page.url();
    // 実UIで切り替え、documentの再読込と認証復元を待ってから元の画面へ戻る。
    await Promise.all([
      this.page.waitForEvent("load", { timeout: 15_000 }),
      mode.click(),
    ]);
    await this.expectPath("/");
    await expect(mode).toBeChecked();
    await this.page.goto(originalURL);
    await this.expectPath(originalURL);
    await expect(mode).toBeChecked();
  }

  async enterCredentials(user: User): Promise<void> {
    await this.page.getByTestId("login-username").locator("input").fill(user.username);
    // 認証入力の例外へ入力値を転記しない。
    try {
      await this.page.getByTestId("login-password").locator("input").fill(user.password);
    } catch {
      throw new Error("ログインのpassword入力に失敗しました");
    }
    const submitted = this.page.waitForResponse(response => new URL(response.url()).pathname === "/api/auth" && response.request().method() === "POST");
    await this.page.getByTestId("login-submit").click();
    await submitted;
  }

  async logout(): Promise<void> {
    // logoutは200ms後にdocumentをreloadするため、旧documentのlogin formを操作しない。
    await Promise.all([
      this.page.waitForEvent("load", { timeout: 15_000 }),
      this.page.getByRole("button", { name: "Log out", exact: true }).click(),
    ]);
    await expect(this.page).toHaveURL(/\/login\?redirect=/);
    await expect(this.page.getByTestId("login-submit")).toBeVisible();
  }

  async api<T>(path: string, method = "GET", body?: unknown): Promise<{ status: number; data: T }> {
    // tokenはbrowser内に保ち、runnerの引数・diagnosticsへ渡さない。
    return this.page.evaluate(async ({ path, method, body }) => {
      const cookie = document.cookie.split("; ").find(value => value.startsWith("accessToken="));
      const token = cookie ? decodeURIComponent(cookie.slice("accessToken=".length)) : "";
      const response = await fetch(path, {
        method,
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: AbortSignal.timeout(10_000),
      });
      return { status: response.status, data: await response.json() as T };
    }, { path, method, body });
  }

  async tasks(response: Response): Promise<Task[]> {
    expect(response.status(), "画面操作でtaskを登録する").toBe(200);
    const tasks = await response.json() as Task[];
    expect(tasks.length).toBeGreaterThan(0);
    for (const task of tasks) this.recordTask(task);
    return tasks;
  }

  recordTask(task: Task): void {
    this.diagnostics.push({ taskId: task.uuid, state: task.status, errorCode: task.errorCode });
  }

  async diagnoseTask(task: Task): Promise<void> {
    if (task.status !== "error" || this.diagnosedTasks.has(task.uuid)) return;
    this.diagnosedTasks.add(task.uuid);
    const response = await this.request.get(`/api/__e2e/tasks/${task.uuid}/diagnostic`, { timeout: 10_000 });
    expect(response.status(), "task例外の安全な診断情報を取得する").toBe(200);
    const diagnostic = await response.json() as TaskDiagnostic;
    // backendが抽出した例外型とsource位置だけを保存し、task.log本文は渡さない。
    this.diagnostics.push({
      taskId: task.uuid,
      exceptionType: diagnostic.exceptionType,
      frames: diagnostic.frames?.map(frame => ({ file: frame.file, line: frame.line })),
    });
    await response.dispose();
  }

  async waitTask(task: Task, expected: "finish" | "error" = "finish"): Promise<Task> {
    let latest = task;
    await expect.poll(async () => {
      const result = await this.api<Task>(`/api/tasks/${task.uuid}`);
      expect(result.status, "task状態の取得").toBe(200);
      latest = result.data;
      this.recordTask(latest);
      await this.diagnoseTask(latest);
      return latest.status;
    }, { message: `task ${task.uuid} が ${expected} になる`, timeout: 30_000, intervals: [250, 500, 1_000] }).toBe(expected);
    return latest;
  }

  async selectProject(project: NamedProject): Promise<void> {
    const selector = this.page.locator("header").getByRole("textbox", { name: "Project", exact: true });
    await selector.focus();
    await selector.press("Enter");
    await this.page.getByRole("option", { name: `${project.name} (#${project.id})`, exact: true }).click();
    await expect(this.page).toHaveURL(new RegExp(`projectId=${project.id}`));
  }
}

export const test = base.extend<{ fullstack: Fullstack; seed: Seed; initialized: boolean }>({
  initialized: [true, { option: true }],
  fullstack: async ({ page, request }, use, testInfo) => {
    const fullstack = new Fullstack(page, request);
    await page.addInitScript(() => localStorage.setItem("virty:locale", "en"));
    try {
      await use(fullstack);
    } finally {
      // cookie・認証画面・task logの自動snapshotを残さず、pollも停止する。
      await page.goto("about:blank");
      await page.context().clearCookies();
      await testInfo.attach("診断用のHTTP状態とtask状態", {
        body: JSON.stringify(fullstack.diagnostics, null, 2),
        contentType: "application/json",
      });
      await fullstack.reset(false);
    }
  },
  seed: [async ({ fullstack, initialized }, use) => {
    await use(await fullstack.reset(initialized));
  }, { auto: true }],
});

export { expect };
