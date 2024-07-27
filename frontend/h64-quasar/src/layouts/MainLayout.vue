<template>
  <q-layout view="hHh lpR fFf">
    
    <q-page-container>
      <router-view />
    </q-page-container>
    
    <q-footer elevated class="bg-primary text-white" height-hint="98">
      <q-toolbar>
        <q-toolbar-title>
          <q-img
            src="src/assets/H64_Logo_For_Dark.svg"
            style="height: 40px; width: 40px;"
            fit="contain"
          />
          H64
        </q-toolbar-title>
        <q-space />
        <q-tabs shrink> <!-- shrink property because child of QToolbar-->
          <q-route-tab to="/page1" label="Page One" />
          <q-route-tab to="/page2" label="Page Two" />
          <q-route-tab to="/page3" label="Page Three" />
        </q-tabs>
      </q-toolbar>
    </q-footer>

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
