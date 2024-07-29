<script setup lang="ts">
import { ref } from 'vue';
import ValueDisplay from 'components/ValueDisplay.vue';

const values = ref({
  time: '',
  model: '',
  id: NaN,
  channel: NaN,
  battery_ok: NaN,
  sensor_type: NaN,
  wind_max_m_s: NaN,
  wind_avg_m_s: NaN,
  wind_dir_deg: NaN,
  rain_mm: NaN,
  mic: '',
  temperature_C: NaN,
  humidity: NaN,
});

const socket = new WebSocket('wss://weatherdata.h64.viridian-project.org');
socket.onmessage = function (e) {
  console.log(JSON.parse(e.data).values);
  values.value = JSON.parse(e.data).values;
}
</script>

<template>
  <q-page padding>
    <h6>Current weather values:</h6>
    <p>Letzte Aktualisierung: {{ values.time }}</p>

    <div class="row">
      <value-display label="Temperature (outside)" :value="`${values.temperature_C} °C`" />
      <value-display label="Humidity (outside)" :value="`${values.humidity}%`" />
      <value-display label="Wind Average" :value="`${values.wind_avg_m_s} m/s`" />
      <value-display label="Wind Gust" :value="`${values.wind_max_m_s} m/s`" />
      <value-display label="Wind Direction" :value="`${values.wind_dir_deg}°`" />
      <value-display label="Total Rainfall since last reset" :value="`${values.rain_mm} Liter`" />
    </div>
  </q-page>
</template>