<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{
  coverUrl: string | null;
  alt: string;
}>();

const hasLoadError = ref(false);

watch(
  () => props.coverUrl,
  () => {
    hasLoadError.value = false;
  },
);

function handleImageError(): void {
  hasLoadError.value = true;
}
</script>

<template>
  <div class="rounded-box bg-base-200 aspect-[2/3] overflow-hidden">
    <img
      v-if="coverUrl && !hasLoadError"
      :alt="alt"
      :src="coverUrl"
      class="h-full w-full object-cover"
      @error="handleImageError"
    />
    <div
      v-else
      class="flex h-full w-full items-center justify-center px-3 text-center text-sm opacity-70"
      role="img"
      :aria-label="`${alt}暂无封面`"
    >
      暂无封面
    </div>
  </div>
</template>
