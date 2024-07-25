<script setup>
import pvIcon from '/icons/dah-solar-blackvelvet-410w.png'
import gridIcon from '/icons/electric-tower.png'
import batteryIcon from '/icons/battery.png'
import loadIcon from '/icons/house.png'
import inverterIcon from '/icons/sun-8-10-12k.png'

import CurrentPower from './CurrentPower.vue'
</script>

<template>
  <h2>Aktuelle Werte</h2>

  <CurrentPower />

  <div id="timestamp" class="card">
    <span>Letzte Aktualisierung:</span>
    <span class="timestamp"></span>
  </div>
  <div id="value-container">
    <div id="pv-power" class="dashboard-item">
      <span class="dashboard-label">PV</span>
      <span class="dashboard-value">--- W</span>
      <img :src="pvIcon" alt="PV power icon">
    </div>
    <div id="grid-power" class="dashboard-item">
      <span class="dashboard-label">Grid</span>
      <span class="dashboard-value">--- W</span>
      <img :src="gridIcon" alt="Grid power icon" class="icon-smaller">
    </div>
    <div id="battery-power" class="dashboard-item">
      <span class="dashboard-label">Battery</span>
      <span class="dashboard-value">--- W</span>
      <span class="dashboard-value dashboard-value-2nd">--%</span>
      <img :src="batteryIcon" alt="Battery power icon" class="icon-smaller">
    </div>
    <div id="load-power" class="dashboard-item">
      <span class="dashboard-label">Load</span>
      <span class="dashboard-value">--- W</span>
      <img :src="loadIcon" alt="Load power icon" class="icon-smaller">
    </div>
    <div id="inverter" class="dashboard-item">
      <img :src="inverterIcon" alt="Inverter icon">
      <span class="dashboard-label">Inverter</span>
    </div>
  </div>
  <h3>Details</h3>
  <div id="value-container-details" class="flex-container">
    <div id="pv1-power" class="flex-item dashboard-item">
      <span class="dashboard-value">--- W</span>
      <img :src="pvIcon" alt="PV power icon">
      <span class="dashboard-label">PV1 Power</span>
    </div>
    <div id="pv2-power" class="flex-item dashboard-item">
      <span class="dashboard-value">--- W</span>
      <img :src="pvIcon" alt="PV power icon">
      <span class="dashboard-label">PV2 Power</span>
    </div>
  </div>
</template>

<style scoped>
#value-container {
  display: grid;
  grid-template-areas:
    "upper-left . upper-right"
    ". grid-center ."
    "lower-left . lower-right";
  grid-template-columns: 150px auto 150px;
  grid-template-rows: 150px 150px 150px;
  margin: 20px;
}

#pv-power {
  grid-area: upper-left;
}

#grid-power {
  grid-area: upper-right;
}

#battery-power {
  grid-area: lower-left;
}

#load-power {
  grid-area: lower-right;
}

#inverter {
  grid-area: grid-center;
  justify-self: center;
}

.dashboard-item {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 160px;
  height: 160px;
  border: 1px #aaa solid;
  border-radius: 10px;
  /* box-shadow: 10px 5px 5px #aaa; */
  margin-right: 20px;
  margin-bottom: 20px;
}

.dashboard-item img {
  width: 80px;
  height: 80px;
}

.dashboard-value {
  font-size: x-large;
}

.dashboard-value-small {
  font-size: large;
}

#timestamp.dashboard-item {
  width: 300px;
  height: 70px;
}

.dashboard-item .icon-smaller {
  width: 75px;
  height: 75px;
}
</style>