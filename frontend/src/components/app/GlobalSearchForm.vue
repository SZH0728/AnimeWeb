<script setup lang="ts">
import { ref } from 'vue';

const emit = defineEmits<{
  'search-submitted': [keyword: string];
}>();

const keyword = ref('');
const isEmpty = ref(false);

function handleSubmit(): void {
  const normalizedKeyword = keyword.value.trim();
  isEmpty.value = normalizedKeyword.length === 0;
  if (!isEmpty.value) {
    emit('search-submitted', normalizedKeyword);
  }
}
</script>

<template>
  <form class="w-full" role="search" @submit.prevent="handleSubmit">
    <label class="sr-only" for="global-search">搜索动画作品</label>
    <div class="flex gap-2">
      <input
        id="global-search"
        v-model="keyword"
        :aria-describedby="isEmpty ? 'global-search-error' : undefined"
        :aria-invalid="isEmpty"
        class="input w-full"
        name="q"
        placeholder="搜索动画作品"
        type="search"
      />
      <button class="btn shrink-0" type="submit">搜索</button>
    </div>
    <p v-if="isEmpty" id="global-search-error" class="text-error mt-2 text-sm" role="alert">
      请输入要搜索的作品名称。
    </p>
  </form>
</template>
