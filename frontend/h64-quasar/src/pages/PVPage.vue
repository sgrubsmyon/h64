<template>
   <q-page>
    
    <router-view />
    
    <q-footer>
      <q-tabs elevated
          inline-label
          outside-arrows
          mobile-arrows
          class="bg-secondary text-white shadow-2"
        >
          <q-route-tab to="/pv/overview" icon="dashboard" label="Overview" />
          <q-route-tab to="/pv/live" icon="alarm" label="Live Data" />
          <q-route-tab to="/pv/archive" icon="archive" label="Archive" />
        </q-tabs>
    </q-footer>
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
export default defineComponent({
  name: 'PVPage'
});
</script>
