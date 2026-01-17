import { runIdle } from '@/lib/idle';

function getApiOrigin(): string | null {
  const apiUrl = (import.meta.env.VITE_API_URL || '').trim();
  if (!apiUrl) return null;
  try {
    return new URL(apiUrl).origin;
  } catch {
    return null;
  }
}

function ensureLink(rel: string, href: string, crossOrigin?: string) {
  const selector = `link[rel="${rel}"][href="${href}"]`;
  if (document.head.querySelector(selector)) return;

  const link = document.createElement('link');
  link.rel = rel;
  link.href = href;
  if (crossOrigin !== undefined) {
    link.crossOrigin = crossOrigin;
  }
  document.head.appendChild(link);
}

export function initPreconnect(): void {
  if (typeof window === 'undefined') return;

  const origin = getApiOrigin();
  if (!origin) return;

  const start = () => {
    ensureLink('dns-prefetch', origin);
    ensureLink('preconnect', origin, '');
  };

  if (document.readyState === 'complete') {
    runIdle(start, 1200);
    return;
  }

  window.addEventListener(
    'DOMContentLoaded',
    () => {
      runIdle(start, 1200);
    },
    { once: true }
  );
}

