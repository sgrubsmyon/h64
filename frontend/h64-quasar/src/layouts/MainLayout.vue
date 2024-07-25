<template>
  <q-layout view="hHh lpR fFf">

    <q-header elevated class="bg-primary text-white" height-hint="98">
      <q-toolbar>
        <q-toolbar-title>
          <q-avatar>
            <img src="src/assets/H64_Logo_For_Dark.svg">
          </q-avatar>
          H64
        </q-toolbar-title>
      </q-toolbar>

      <q-tabs align="left">
        <q-route-tab to="/page1" label="Page One" />
        <q-route-tab to="/page2" label="Page Two" />
        <q-route-tab to="/page3" label="Page Three" />
      </q-tabs>
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
