<template>
  <q-card dark bordered class="my-card q-mr-md">
    <q-card-section>
      <div class="text-h6">{{ label }}</div>
    </q-card-section>

    <q-separator dark inset />

    <q-card-section>
      <div class="text-h1">{{ value }}</div>
    </q-card-section>
  </q-card>
</template>

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
