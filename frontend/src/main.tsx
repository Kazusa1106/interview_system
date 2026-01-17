import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { registerServiceWorker } from './pwa/register'
import { initWebVitals } from './perf/webVitals'
import { initPreconnect } from './perf/preconnect'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

if (import.meta.env.PROD) {
  registerServiceWorker()
}

initWebVitals()
initPreconnect()
