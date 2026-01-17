import { onCLS, onINP, onLCP, onTTFB, type Metric } from 'web-vitals';
import { runIdle } from '@/lib/idle';

function getEndpoint(): string | null {
  const value = (import.meta.env.VITE_WEB_VITALS_ENDPOINT || '').trim();
  return value ? value : null;
}

type WebVitalsPayload = {
  id: string;
  name: Metric['name'];
  value: number;
  rating: Metric['rating'];
  delta: number;
  navigationType?: Metric['navigationType'];
  urlPath: string;
  timestamp: number;
};

function toPayload(metric: Metric): WebVitalsPayload {
  return {
    id: metric.id,
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
    delta: metric.delta,
    navigationType: metric.navigationType,
    urlPath: window.location.pathname,
    timestamp: Date.now(),
  };
}

function send(endpoint: string, payload: WebVitalsPayload): void {
  const body = JSON.stringify(payload);

  if (navigator.sendBeacon) {
    const blob = new Blob([body], { type: 'application/json' });
    navigator.sendBeacon(endpoint, blob);
    return;
  }

  void fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body,
    keepalive: true,
  }).catch(() => undefined);
}

export function initWebVitals(): void {
  if (typeof window === 'undefined') return;

  const endpoint = getEndpoint();

  const report = (metric: Metric) => {
    if (!endpoint) return;

    try {
      send(endpoint, toPayload(metric));
    } catch {
      // Silent fail
    }
  };

  const start = () => {
    onCLS(report);
    onINP(report);
    onLCP(report);
    onTTFB(report);
  };

  if (document.readyState === 'complete') {
    runIdle(start, 2000);
    return;
  }

  window.addEventListener(
    'load',
    () => {
      runIdle(start, 2000);
    },
    { once: true }
  );
}
