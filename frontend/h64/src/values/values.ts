// import { setupCounter } from '../counter.ts'
import { setupWebSocket } from './ws-client'

import './values.css'

import pvIcon from '/icons/dah-solar-blackvelvet-410w.png'
import gridIcon from '/icons/electric-tower.png'
import batteryIcon from '/icons/battery.png'
import loadIcon from '/icons/house.png'
import inverterIcon from '/icons/sun-8-10-12k.png'

document.querySelector<HTMLDivElement>('#current-values')!.innerHTML = `
  <!-- <button id="counter" type="button"></button> -->

  <h2>Aktuelle Werte</h2>
    <div id="timestamp" class="card">
      <span>Letzte Aktualisierung:</span>
      <span class="timestamp"></span>
    </div>
    <div id="value-container">
        <div id="pv-power" class="dashboard-item">
            <span class="dashboard-label">PV</span>
            <span class="dashboard-value">--- W</span>
            <img src="${pvIcon}" alt="PV power icon">
        </div>
        <div id="grid-power" class="dashboard-item">
            <span class="dashboard-label">Grid</span>
            <span class="dashboard-value">--- W</span>
            <img src="${gridIcon}" alt="Grid power icon" class="icon-smaller">
        </div>
        <div id="battery-power" class="dashboard-item">
            <span class="dashboard-label">Battery</span>
            <span class="dashboard-value">--- W</span>
            <span class="dashboard-value dashboard-value-2nd">--%</span>
            <img src="${batteryIcon}" alt="Battery power icon" class="icon-smaller">
        </div>
        <div id="load-power" class="dashboard-item">
            <span class="dashboard-label">Load</span>
            <span class="dashboard-value">--- W</span>
            <img src="${loadIcon}" alt="Load power icon" class="icon-smaller">
        </div>
        <div id="inverter" class="dashboard-item">
            <img src="${inverterIcon}" alt="Inverter icon">
            <span class="dashboard-label">Inverter</span>
        </div>
    </div>
    <h3>Details</h3>
    <div id="value-container-details" class="flex-container">
        <div id="pv1-power" class="flex-item dashboard-item">
            <span class="dashboard-value">--- W</span>
            <img src="${pvIcon}" alt="PV power icon">
            <span class="dashboard-label">PV1 Power</span>
        </div>
        <div id="pv2-power" class="flex-item dashboard-item">
            <span class="dashboard-value">--- W</span>
            <img src="${pvIcon}" alt="PV power icon">
            <span class="dashboard-label">PV2 Power</span>
        </div>
    </div>
`

// setupCounter(document.querySelector<HTMLButtonElement>('#counter')!)
setupWebSocket()
