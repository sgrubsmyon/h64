<template>
  <q-layout view="hHh lpr fFf">
    
    <q-header elevated class="bg-primary text-white" height-hint="98">
      <q-toolbar>
        <q-toolbar-title>
          <q-img
            src="~assets/H64_Logo_For_Dark.svg"
            style="height: 40px; width: 40px;"
            fit="contain"
          />
          H64
        </q-toolbar-title>
        <q-space />
        <q-tabs shrink> <!-- shrink property because child of QToolbar-->
          <q-route-tab to="/" label="Dashboard" icon="home" />
          <q-route-tab :to="`/weather/${last_visited_page.weather}`" label="Weather" icon="thermostat" />
          <q-route-tab :to="`/pv/${last_visited_page.pv}`" label="PV" icon="solar_power" />
        </q-tabs>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>

  </q-layout>
</template>

<script setup lang="ts">
import { watch } from 'vue';
import { ref } from 'vue';
import { useRoute } from 'vue-router';

defineOptions({
  name: 'MainLayout'
});

const last_visited_page = ref({
  weather: 'live',
  pv: 'live',
});

const route = useRoute();

watch(route, () => {
  const fp = route.fullPath;
  if (fp.startsWith('/weather')) {
    last_visited_page.value.weather = fp.replace('/weather/', '');
  }
  if (fp.startsWith('/pv')) {
    last_visited_page.value.pv = fp.replace('/pv/', '');
  }
});
</script>
