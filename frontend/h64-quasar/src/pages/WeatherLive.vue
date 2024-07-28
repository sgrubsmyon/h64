<script setup lang="ts">
import { ref } from 'vue';

const values = ref({
  temperature_C: NaN,
  humidity: NaN,
})
</script>

<template>
  <q-page padding>
    <h6>Current weather values:</h6>

    <div class="row">
      <q-card dark bordered class="my-card q-mr-md">
        <q-card-section>
          <div class="text-h6">Temperature (outside)</div>
        </q-card-section>

        <q-separator dark inset />

        <q-card-section>
          <div class="text-h1">{{ values.temperature_C }} °C</div>
        </q-card-section>
      </q-card>

      <q-card dark bordered class="my-card">
        <q-card-section>
          <div class="text-h6">Humidity (outside)</div>
        </q-card-section>

        <q-separator dark inset />

        <q-card-section>
          <div class="text-h1">{{ values.humidity }}%</div>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<style>
.my-card {
  width: 100%;
  max-width: 350px;
}
</style>