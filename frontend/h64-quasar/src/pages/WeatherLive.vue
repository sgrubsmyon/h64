<script setup lang="ts">
import { ref } from 'vue';
import ValueDisplay from 'components/ValueDisplay.vue';

const values = ref({
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

    <div class="row">
      <value-display id="temperature" label="Temperature (outside)" :value="`${values.temperature_C} °C`" />
      <value-display id="temperature" label="Humidity (outside)" :value="`${values.humidity}%`" />
    </div>
  </q-page>
</template>

<style>
.my-card {
  width: 100%;
  max-width: 350px;
}
</style>