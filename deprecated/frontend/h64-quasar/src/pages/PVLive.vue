<template>
  <q-page padding>
    <h6>Live photovoltaic values:</h6>
    <table>
      <thead>
        <tr>
          <th></th>
          <th>Inverter</th>
          <th>Heat pump</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>Last timestamp</th>
          <td>{{ timestampString(inverter_data.values.faster.time) }}</td>
          <td>{{ timestampString(heatpump_data.values.values2.time) }}</td>
        </tr>
        <tr>
          <th>Status</th>
          <td>{{ inverter_data.status.type + (inverter_data.status.msg.length > 0 ? ('(' + inverter_data.status.msg + ')') : '') }}</td>
          <td>{{ heatpump_data.status }}</td>
        </tr>
      </tbody>
    </table>

    <div class="row">
      <value-display label="PV production" :value="`${inverter_data.values.faster.pv1_power + inverter_data.values.faster.pv2_power} W`" />
      <value-display label="Grid power" :value="`${inverter_data.values.faster.total_grid_power} W`" />
      <value-display label="Battery power" :value="`${inverter_data.values.faster.battery_power} W`" />
      <value-display label="Total load (house + heat pump)" :value="`${inverter_data.values.faster.total_load_power} W`" />
      <value-display label="House load" :value="`${Math.round(inverter_data.values.faster.total_load_power - heatpump_data.values.power)} W`" />
      <value-display label="Heat pump load" :value="`${Math.round(heatpump_data.values.power)} W`" />
      <value-display label="Battery SoC" :value="`${inverter_data.values.slow.battery_soc}%`" />
    </div>
  </q-page>
</template>

<style scoped>
table {
  border-collapse: collapse;
  margin-bottom: 10px;
}
table th, table td {
  padding: 5px;
  border: 1px solid #ccc;
}
</style>

<script setup lang="ts">
import { ref } from 'vue';
import ValueDisplay from 'components/ValueDisplay.vue';
import { InverterData, emptyInverterData } from 'components/typesd/inverter-data';
import { HeatPumpData, emptyHeatPumpData } from 'components/typesd/heat-pump-data';

const RECONNECT_INTERVAL = 10;

const inverter_data = ref<InverterData>(emptyInverterData);
const heatpump_data = ref<HeatPumpData>(emptyHeatPumpData);

function timestampString(timestamp: string) {
  const date = new Date(timestamp + 'Z');
  const date_str = date.toLocaleString('de-DE', {
    dateStyle: 'medium', timeStyle: 'medium'
  });
  return date_str;
}

function connectToInverterWebSocketServer() {
  let socket = new WebSocket('wss://inverterdata.h64.viridian-project.org');
  socket.onmessage = function (e) {
    // console.log('inverter_data:', JSON.parse(e.data));
    inverter_data.value = JSON.parse(e.data);
  }
  socket.onclose = function () {
    console.warn('Socket is closed. Reconnect will be attempted in 10 seconds.');
    setTimeout(function () {
      socket = connectToInverterWebSocketServer();
    }, RECONNECT_INTERVAL * 1000);
  }
  return socket;
}

function connectToHeatPumpWebSocketServer() {
  let socket = new WebSocket('wss://heatpumpdata.h64.viridian-project.org');
  socket.onmessage = function (e) {
    // console.log('heatpump_data:', JSON.parse(e.data));
    heatpump_data.value = JSON.parse(e.data);
  }
  socket.onclose = function () {
    console.warn('Socket is closed. Reconnect will be attempted in 10 seconds.');
    setTimeout(function () {
      socket = connectToHeatPumpWebSocketServer();
    }, RECONNECT_INTERVAL * 1000);
  }
  return socket;
}

connectToInverterWebSocketServer();
connectToHeatPumpWebSocketServer();
</script>
