<script setup lang="ts">
type LoadingStateVariant = 'page' | 'list' | 'detail' | 'home';

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
      <template v-if="variant === 'home'">
        <div class="space-y-5">
          <div class="space-y-2">
            <div class="skeleton h-9 w-2/5"></div>
            <div class="skeleton h-5 w-3/5"></div>
          </div>
          <div class="space-y-3">
            <div class="skeleton h-7 w-36"></div>
            <div class="skeleton h-24 w-full"></div>
            <div class="skeleton h-24 w-full"></div>
          </div>
          <div class="grid gap-10 md:grid-cols-2">
            <div v-for="index in 2" :key="index" class="space-y-3">
              <div class="skeleton h-7 w-32"></div>
              <div class="skeleton h-24 w-full"></div>
              <div class="skeleton h-24 w-full"></div>
            </div>
          </div>
        </div>
      </template>

      <div v-else-if="variant === 'detail'" class="flex flex-col gap-6 sm:flex-row">
        <div class="skeleton aspect-2/3 w-36 shrink-0"></div>
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
