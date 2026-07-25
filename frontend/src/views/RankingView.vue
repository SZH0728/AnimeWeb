<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const ranking = computed(() => route.meta.ranking);
</script>

<template>
  <section aria-labelledby="ranking-title" class="app-container py-16 sm:py-24">
    <h1 id="ranking-title" class="text-3xl font-bold tracking-tight">{{ ranking?.title }}</h1>
    <p class="text-base-content/70 mt-4">{{ ranking?.description }}</p>
  </section>
</template>
