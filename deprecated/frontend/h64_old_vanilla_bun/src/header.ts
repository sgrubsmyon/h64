import './main.css'

// import h64Logo from '/h64-logo.svg'
import h64LogoDark from '/h64-logo-for-dark.svg'

document.querySelector<HTMLElement>('header')!.innerHTML = `
  <h1>
    <a href="/">
      <img src="${h64LogoDark}" class="logo" alt="H64 logo" />
      H64
    </a>
  </h1>
`