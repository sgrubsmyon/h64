<template>
  <q-card dark bordered class="my-card q-mr-md q-mb-md">
    <q-card-section>
      <div class="text-h6">{{ label }}</div>
    </q-card-section>

    <q-separator dark inset />

    <q-card-section>
      <div class="text-h2">{{ value }}</div>
    </q-card-section>
  </q-card>
</template>

<style scoped>
  .my-card {
    width: 100%;
    max-width: 350px;
  }
</style>

<script setup lang="ts">
  interface Props {
    label: string;
    value: string;
  };

  withDefaults(defineProps<Props>(), {
    label: '',
    value: '-'
  });
</script>
