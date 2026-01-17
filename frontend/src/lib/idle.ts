type RequestIdleCallback = (callback: () => void, options?: { timeout: number }) => number;

export function runIdle(callback: () => void, timeoutMs: number) {
  const ric = (window as unknown as { requestIdleCallback?: RequestIdleCallback })
    .requestIdleCallback;
  if (typeof ric === 'function') {
    ric(callback, { timeout: timeoutMs });
    return;
  }
  window.setTimeout(callback, timeoutMs);
}
