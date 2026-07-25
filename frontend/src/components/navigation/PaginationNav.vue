<script setup lang="ts">
import { formatNumber } from '@/utils/formatters';

const props = defineProps<{
  page: number;
  totalPages: number;
  total: number;
}>();

const emit = defineEmits<{
  'page-requested': [page: number];
}>();

function requestPage(page: number): void {
  if (page >= 1 && page <= props.totalPages && page !== props.page) {
    emit('page-requested', page);
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
