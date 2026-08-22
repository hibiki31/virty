export type TaskPollingSnapshot = {
  count: number;
  hash: string;
  uuids: string[];
};

export type TaskPollerOptions = {
  isAuthenticated: () => boolean;
  onSnapshot: (snapshot: TaskPollingSnapshot, previousCount: number) => void;
  request: (
    referenceHash: string,
    signal: AbortSignal,
  ) => Promise<TaskPollingSnapshot>;
  maxBackoffMs?: number;
  successIntervalMs?: number;
};

export type TaskPoller = {
  isRunning: () => boolean;
  start: () => void;
  stop: () => void;
};

type TaskSnapshotEffects = {
  notifyReload: () => void;
  setTaskCount: (count: number) => void;
  setTaskUuids: (uuids: string[]) => void;
  triggerReload: () => void;
};

export function applyTaskPollingSnapshot(
  snapshot: TaskPollingSnapshot,
  previousCount: number,
  autoReload: boolean,
  effects: TaskSnapshotEffects,
): void {
  effects.setTaskUuids(snapshot.uuids);

  if (autoReload && previousCount > snapshot.count) {
    effects.notifyReload();
    effects.triggerReload();
  }

  effects.setTaskCount(snapshot.count);
}

/**
 * incomplete taskを単一requestずつpollする。停止時は待機timerと実行中requestを取り消す。
 */
export function createTaskPoller({
  isAuthenticated,
  maxBackoffMs = 30_000,
  onSnapshot,
  request,
  successIntervalMs = 1_000,
}: TaskPollerOptions): TaskPoller {
  let abortController: AbortController | undefined;
  let failureDelayMs = successIntervalMs;
  let inFlight = false;
  let previousCount = 0;
  let referenceHash = "";
  let stopped = true;
  let timer: ReturnType<typeof setTimeout> | undefined;

  const schedule = (delayMs: number): void => {
    if (stopped) return;
    timer = setTimeout(() => void pollOnce(), delayMs);
  };

  const pollOnce = async (): Promise<void> => {
    if (stopped || inFlight) return;

    if (!isAuthenticated()) {
      schedule(successIntervalMs);
      return;
    }

    inFlight = true;
    abortController = new AbortController();
    let nextDelayMs = successIntervalMs;

    try {
      const snapshot = await request(referenceHash, abortController.signal);
      if (stopped) return;

      onSnapshot(snapshot, previousCount);
      previousCount = snapshot.count;
      referenceHash = snapshot.hash;
      failureDelayMs = successIntervalMs;
    } catch (error) {
      if (stopped || (error instanceof DOMException && error.name === "AbortError")) {
        return;
      }

      nextDelayMs = failureDelayMs;
      failureDelayMs = Math.min(failureDelayMs * 2, maxBackoffMs);
    } finally {
      inFlight = false;
      abortController = undefined;
      schedule(nextDelayMs);
    }
  };

  return {
    isRunning: () => !stopped,
    start() {
      if (!stopped) return;

      stopped = false;
      failureDelayMs = successIntervalMs;
      void pollOnce();
    },
    stop() {
      stopped = true;
      if (timer !== undefined) {
        clearTimeout(timer);
        timer = undefined;
      }
      abortController?.abort();
    },
  };
}
