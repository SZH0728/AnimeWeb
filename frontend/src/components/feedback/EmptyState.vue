<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
}>();
</script>

<template>
  <section class="rounded-box bg-base-200 px-6 py-10 text-center">
    <h2 class="text-lg font-semibold">{{ title }}</h2>
    <p v-if="description" class="mt-2 text-sm opacity-75">{{ description }}</p>
  </section>
</template>
