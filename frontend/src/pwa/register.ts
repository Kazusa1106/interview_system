import { Workbox } from 'workbox-window';
import { runIdle } from '@/lib/idle';

export function registerServiceWorker(): void {
  if (!('serviceWorker' in navigator)) return;

  const register = () => {
    const wb = new Workbox('/sw.js');

    wb.addEventListener('waiting', () => {
      void wb.messageSkipWaiting();
    });

    wb.addEventListener('activated', (event) => {
      if (event.isUpdate) {
        window.location.reload();
      }
    });

    void wb.register();
  };

  window.addEventListener('load', () => {
    runIdle(register, 2000);
  });
}

