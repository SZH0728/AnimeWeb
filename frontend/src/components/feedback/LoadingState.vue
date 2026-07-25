<script setup lang="ts">
type LoadingStateVariant = 'page' | 'list' | 'detail';

withDefaults(
  defineProps<{
    variant?: LoadingStateVariant;
    label?: string;
  }>(),
  {
    variant: 'list',
    label: '正在加载内容',
  },
);
</script>

<template>
  <section :class="['space-y-3', variant === 'page' ? 'py-12' : 'py-4']" role="status">
    <span class="sr-only">{{ label }}</span>
    <div aria-hidden="true" class="space-y-3">
      <div v-if="variant === 'page'" class="skeleton h-8 w-2/5"></div>
      <div :class="['skeleton', variant === 'detail' ? 'aspect-[2/3] w-36' : 'h-24 w-full']"></div>
      <div class="skeleton skeleton-text w-4/5"></div>
      <div class="skeleton skeleton-text w-3/5"></div>
    </div>
  </section>
</template>
