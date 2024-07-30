<template>
  <q-page padding>
    <h6>Live photovoltaic values:</h6>
    <p>Last timestamp: {{ values.faster.time }}</p>

    <div class="row">
      <value-display label="PV production" :value="`${values.faster.pv1_power + values.faster.pv2_power} W`" />
      <value-display label="Grid power" :value="`${values.faster.total_grid_power} W`" />
      <value-display label="Battery power" :value="`${values.faster.battery_power} W`" />
      <value-display label="Residential load" :value="`${values.faster.total_load_power} W`" />
      <value-display label="Battery SoC" :value="`${values.slow.battery_soc}%`" />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ValueDisplay from 'components/ValueDisplay.vue';

const RECONNECT_INTERVAL = 10;

const values = ref({
  slow: {
    time: '',
    daily_pv_production: NaN,
    total_pv_production: NaN,
    daily_load_energy_consumption: NaN,
    total_load_energy_consumption: NaN,
    daily_energy_bought: NaN,
    daily_energy_sold: NaN,
    total_energy_bought: NaN,
    total_energy_sold: NaN,
    battery_soc: NaN,
    battery_daily_charge: NaN,
    battery_daily_discharge: NaN,
    battery_total_charge: NaN,
    battery_total_discharge: NaN,
    dc_temperature: NaN,
    ac_temperature: NaN,
    battery_temperature: NaN,
    battery_voltage: NaN,
    active_power_regulation: NaN
  },
  fast: {
    time: '',
    load_voltage_l1: NaN,
    load_voltage_l2: NaN,
    load_voltage_l3: NaN,
    grid_voltage_l1: NaN,
    grid_voltage_l2: NaN,
    grid_voltage_l3: NaN,
    ct_internal_power_l1: NaN,
    ct_internal_power_l2: NaN,
    ct_internal_power_l3: NaN,
    ct_external_power_l1: NaN,
    ct_external_power_l2: NaN,
    ct_external_power_l3: NaN,
    inverter_power_l1: NaN,
    inverter_power_l2: NaN,
    inverter_power_l3: NaN,
    current_l1: NaN,
    current_l2: NaN,
    current_l3: NaN,
    battery_current: NaN
  },
  faster: {
    time: '',
    total_load_power: NaN,
    total_grid_power: NaN,
    load_power_l1: NaN,
    load_power_l2: NaN,
    load_power_l3: NaN,
    pv1_power: NaN,
    pv2_power: NaN,
    pv1_voltage: NaN,
    pv2_voltage: NaN,
    pv1_current: NaN,
    pv2_current: NaN,
    battery_power: NaN
  }
});

function connectToWebSocketServer() {
  let socket = new WebSocket('wss://inverterdata.h64.viridian-project.org');
  socket.onmessage = function (e) {
    // console.log(JSON.parse(e.data).values);
    values.value = JSON.parse(e.data).values;
  }
  socket.onclose = function () {
    console.warn('Socket is closed. Reconnect will be attempted in 10 seconds.');
    setTimeout(function () {
      socket = connectToWebSocketServer();
    }, RECONNECT_INTERVAL * 1000);
  }
  return socket;
}

connectToWebSocketServer();
</script>
