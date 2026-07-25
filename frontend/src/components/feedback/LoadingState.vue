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
    <div aria-hidden="true">
      <div v-if="variant === 'detail'" class="flex flex-col gap-6 sm:flex-row">
        <div class="skeleton aspect-[2/3] w-36 flex-shrink-0"></div>
        <div class="flex-1 space-y-3">
          <div class="skeleton h-24 w-full"></div>
          <div class="skeleton h-5 w-4/5"></div>
          <div class="skeleton h-5 w-3/5"></div>
        </div>
      </div>

      <div v-else class="space-y-3">
        <div v-if="variant === 'page'" class="skeleton h-8 w-2/5"></div>
        <div class="skeleton h-24 w-full"></div>
        <div class="skeleton h-5 w-4/5"></div>
        <div class="skeleton h-5 w-3/5"></div>
      </div>
    </div>
  </section>
</template>
