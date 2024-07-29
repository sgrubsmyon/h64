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
          <q-route-tab to="/weather/live" label="Weather" icon="thermostat" />
          <q-route-tab to="/pv/live" label="PV" icon="solar_power" />
        </q-tabs>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>

  </q-layout>
</template>

<script setup lang="ts">
// import { ref } from 'vue';

defineOptions({
  name: 'MainLayout'
});

// const tabsShown = ref(false);

// function toggleTabsShown () {
//   tabsShown.value = !tabsShown.value;
// }
</script>
