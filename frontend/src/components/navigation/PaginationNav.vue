<script setup lang="ts">
import { ref, watch } from 'vue';
import { formatNumber } from '@/utils/formatters';

const props = defineProps<{
  page: number;
  totalPages: number;
  total: number;
}>();

const emit = defineEmits<{
  'page-requested': [page: number];
}>();

// 本地输入的页码状态
const inputPage = ref<number | string>(props.page);

// 监听外部 props.page 的变化，同步更新输入框的值
watch(
  () => props.page,
  (newPage) => {
    inputPage.value = newPage;
  },
  { immediate: true },
);

function requestPage(page: number): void {
  if (page >= 1 && page <= props.totalPages && page !== props.page) {
    emit('page-requested', page);
  }
}

function handleBlur(): void {
  let target = Number(inputPage.value);

  if (isNaN(target) || inputPage.value === '') {
    target = props.page;
  }

  target = Math.floor(target);

  if (target < 1) {
    target = 1;
  }

  if (target > props.totalPages) {
    target = props.totalPages;
  }

  inputPage.value = target;
  requestPage(target);
}

function handleEnter(event: KeyboardEvent): void {
  if (event.target instanceof HTMLInputElement) {
    event.target.blur();
  }
}
</script>

<template>
  <nav
    v-if="totalPages > 1"
    aria-label="分页"
    class="flex flex-wrap items-center justify-between gap-3"
  >
    <p class="text-sm opacity-75">
      共 {{ formatNumber(total) }} 项，第 {{ page }} / {{ totalPages }} 页
    </p>
    <div class="join" role="group" aria-label="分页操作">
      <button
        class="btn join-item btn-sm"
        type="button"
        :disabled="page === 1"
        @click="requestPage(1)"
      >
        首页
      </button>
      <button
        class="btn join-item btn-sm"
        type="button"
        :disabled="page === 1"
        @click="requestPage(page - 1)"
      >
        上一页
      </button>

      <!-- 页码跳转输入框 -->
      <input
        v-model="inputPage"
        type="number"
        min="1"
        :max="totalPages"
        class="input input-bordered join-item input-sm w-16 [appearance:textfield] text-center focus:outline-none"
        aria-label="跳转页码"
        @blur="handleBlur"
        @keydown.enter="handleEnter"
      />

      <button
        class="btn join-item btn-sm"
        type="button"
        :disabled="page === totalPages"
        @click="requestPage(page + 1)"
      >
        下一页
      </button>
      <button
        class="btn join-item btn-sm"
        type="button"
        :disabled="page === totalPages"
        @click="requestPage(totalPages)"
      >
        末页
      </button>
    </div>
  </nav>
</template>
