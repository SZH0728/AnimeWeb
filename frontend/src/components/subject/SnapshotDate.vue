<script setup lang="ts">
import type { ApiDate } from '@/api/api-contract';
import { formatApiDate } from '@/utils/formatters';

defineProps<{
  date: ApiDate;
}>();
</script>

<template>
  <p class="text-sm opacity-70">
    快照日期：<time :datetime="date">{{ formatApiDate(date) }}</time>
  </p>
</template>
