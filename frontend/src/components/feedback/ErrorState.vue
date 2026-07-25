<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string;
    message?: string;
    retryLabel?: string;
    canRetry?: boolean;
  }>(),
  {
    title: '加载失败',
    message: '暂时无法获取内容，请稍后重试。',
    retryLabel: '重试',
    canRetry: true,
  },
);

const emit = defineEmits<{
  'retry-requested': [];
}>();
</script>

<template>
  <section class="alert alert-error alert-vertical sm:alert-horizontal items-center" role="alert">
    <div class="flex-1 text-left">
      <h2 class="font-semibold">{{ title }}</h2>
      <p class="text-sm">{{ message }}</p>
    </div>

    <button
      v-if="canRetry"
      class="btn btn-sm w-full sm:w-auto sm:justify-self-end"
      type="button"
      @click="emit('retry-requested')"
    >
      {{ retryLabel }}
    </button>
  </section>
</template>
