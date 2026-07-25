<script setup lang="ts">
import type { LatestRating } from '@/api/api-contract';
import { formatNumber, formatOptionalNumber } from '@/utils/formatters';

import SnapshotDate from './SnapshotDate.vue';

withDefaults(
  defineProps<{
    rating: LatestRating | null;
    compact?: boolean;
  }>(),
  {
    compact: false,
  },
);
</script>

<template>
  <section :class="compact ? 'space-y-1 text-sm' : 'space-y-2'" aria-label="最新评分">
    <p v-if="rating === null" class="font-medium">暂无评分</p>
    <template v-else>
      <dl
        :class="
          compact ? 'flex flex-wrap gap-x-3 gap-y-1' : 'grid grid-cols-1 gap-1 sm:grid-cols-3'
        "
      >
        <div>
          <dt class="text-sm opacity-70">评分</dt>
          <dd class="font-semibold">{{ formatOptionalNumber(rating.score) }}</dd>
        </div>
        <div>
          <dt class="text-sm opacity-70">评价人数</dt>
          <dd class="font-semibold">{{ formatNumber(rating.total) }}</dd>
        </div>
        <div>
          <dt class="text-sm opacity-70">Bangumi 综合排名</dt>
          <dd class="font-semibold">{{ formatOptionalNumber(rating.rank) }}</dd>
        </div>
      </dl>
      <SnapshotDate :date="rating.date" />
    </template>
  </section>
</template>
