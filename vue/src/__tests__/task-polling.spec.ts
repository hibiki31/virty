import {
  applyTaskPollingSnapshot,
  createTaskPoller,
} from "@/composables/taskPolling";
import { flushPromises } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

describe("incomplete task poller", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("count減少時だけauto reloadを一回triggerする", () => {
    const state = { count: 2, taskUuids: [] as string[] };
    const effects = {
      notifyReload: vi.fn(),
      setTaskCount: vi.fn((count: number) => {
        state.count = count;
      }),
      setTaskUuids: vi.fn((uuids: string[]) => {
        state.taskUuids = uuids;
      }),
      triggerReload: vi.fn(),
    };

    applyTaskPollingSnapshot(
      { count: 1, hash: "hash", uuids: ["task-1"] },
      2,
      true,
      effects,
    );
    expect(effects.triggerReload).toHaveBeenCalledOnce();
    expect(effects.notifyReload).toHaveBeenCalledOnce();
    expect(state).toEqual({ count: 1, taskUuids: ["task-1"] });

    applyTaskPollingSnapshot(
      { count: 0, hash: "next", uuids: [] },
      1,
      false,
      effects,
    );
    expect(effects.triggerReload).toHaveBeenCalledOnce();
  });

  it("成功後は1秒待ち、hashと前回countを次のcycleへ渡す", async () => {
    const request = vi
      .fn()
      .mockResolvedValueOnce({ count: 2, hash: "hash-1", uuids: ["a", "b"] })
      .mockResolvedValueOnce({ count: 1, hash: "hash-2", uuids: ["b"] });
    const onSnapshot = vi.fn();
    const poller = createTaskPoller({
      isAuthenticated: () => true,
      onSnapshot,
      request,
    });

    poller.start();
    await flushPromises();
    expect(request).toHaveBeenCalledTimes(1);
    expect(request.mock.calls[0][0]).toBe("");
    expect(onSnapshot).toHaveBeenNthCalledWith(
      1,
      { count: 2, hash: "hash-1", uuids: ["a", "b"] },
      0,
    );

    await vi.advanceTimersByTimeAsync(999);
    expect(request).toHaveBeenCalledTimes(1);
    await vi.advanceTimersByTimeAsync(1);
    await flushPromises();

    expect(request.mock.calls[1][0]).toBe("hash-1");
    expect(onSnapshot).toHaveBeenNthCalledWith(
      2,
      { count: 1, hash: "hash-2", uuids: ["b"] },
      2,
    );
    poller.stop();
  });

  it("未認証中はrequestせず、同時requestを一つに制限する", async () => {
    let authenticated = false;
    let resolveRequest!: (value: { count: number; hash: string; uuids: string[] }) => void;
    const pending = new Promise<{ count: number; hash: string; uuids: string[] }>(
      (resolve) => {
        resolveRequest = resolve;
      },
    );
    const request = vi.fn().mockReturnValue(pending);
    const poller = createTaskPoller({
      isAuthenticated: () => authenticated,
      onSnapshot: vi.fn(),
      request,
    });

    poller.start();
    await vi.advanceTimersByTimeAsync(5_000);
    expect(request).not.toHaveBeenCalled();

    authenticated = true;
    await vi.advanceTimersByTimeAsync(1_000);
    expect(request).toHaveBeenCalledOnce();
    await vi.advanceTimersByTimeAsync(10_000);
    expect(request).toHaveBeenCalledOnce();

    resolveRequest({ count: 0, hash: "hash", uuids: [] });
    await flushPromises();
    await vi.advanceTimersByTimeAsync(1_000);
    expect(request).toHaveBeenCalledTimes(2);
    poller.stop();
  });

  it("失敗を1秒から最大30秒まで指数backoffする", async () => {
    const request = vi.fn().mockRejectedValue(new Error("unavailable"));
    const poller = createTaskPoller({
      isAuthenticated: () => true,
      onSnapshot: vi.fn(),
      request,
    });

    poller.start();
    await flushPromises();
    expect(request).toHaveBeenCalledTimes(1);

    for (const [index, delay] of [1_000, 2_000, 4_000, 8_000, 16_000, 30_000, 30_000].entries()) {
      await vi.advanceTimersByTimeAsync(delay - 1);
      expect(request).toHaveBeenCalledTimes(index + 1);
      await vi.advanceTimersByTimeAsync(1);
      await flushPromises();
      expect(request).toHaveBeenCalledTimes(index + 2);
    }

    poller.stop();
  });

  it("stopで待機timerと実行中requestをcancelする", async () => {
    let requestSignal: AbortSignal | undefined;
    const request = vi.fn((_: string, signal: AbortSignal) => {
      requestSignal = signal;
      return new Promise<never>((_, reject) => {
        signal.addEventListener("abort", () => {
          reject(new DOMException("aborted", "AbortError"));
        });
      });
    });
    const poller = createTaskPoller({
      isAuthenticated: () => true,
      onSnapshot: vi.fn(),
      request,
    });

    poller.start();
    expect(poller.isRunning()).toBe(true);
    poller.stop();
    await flushPromises();

    expect(requestSignal?.aborted).toBe(true);
    expect(poller.isRunning()).toBe(false);
    await vi.advanceTimersByTimeAsync(60_000);
    expect(request).toHaveBeenCalledOnce();
  });
});
