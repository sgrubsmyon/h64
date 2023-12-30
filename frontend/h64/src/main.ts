import './style.css'
import h64Logo from '/h64-logo.svg'
import h64LogoDark from '/h64-logo-for-dark.svg'
import { setupCounter } from './counter.ts'

document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
  <div>
    <a href="/">
      <img src="${h64LogoDark}" class="logo" alt="H64 logo" />
    </a>
    <h1>H64</h1>
    <div class="card">
      <button id="counter" type="button"></button>
    </div>
    <p class="read-the-docs">
      Click on the Vite and TypeScript logos to learn more
    </p>
  </div>
`

setupCounter(document.querySelector<HTMLButtonElement>('#counter')!)
