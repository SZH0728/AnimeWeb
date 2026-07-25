<script setup lang="ts">
import type { RankingItem } from '@/api/api-contract';
import type { RankingType } from '@/types/api-requests';
import { formatNumber } from '@/utils/formatters';

import CoverImage from '@/components/subject/CoverImage.vue';
import LatestRatingSummary from '@/components/subject/LatestRatingSummary.vue';

defineProps<{
  item: RankingItem;
  rankingType: RankingType;
}>();
</script>

<template>
  <article class="rounded-box bg-base-200 p-4 shadow-sm">
    <div class="flex gap-3 md:items-center">
      <p class="text-primary w-16 shrink-0 text-center text-sm font-semibold">
        本站第 {{ item.position }} 名
      </p>
      <RouterLink
        :aria-label="`查看${item.subject.name}详情`"
        :to="{ name: 'subject-detail', params: { bgmId: item.subject.bgm_id } }"
        class="w-20 shrink-0"
      >
        <CoverImage :alt="`${item.subject.name}封面`" :cover-url="item.subject.cover_url" />
      </RouterLink>
      <div class="min-w-0 flex-1">
        <RouterLink
          :to="{ name: 'subject-detail', params: { bgmId: item.subject.bgm_id } }"
          class="link text-lg font-semibold break-words"
        >
          {{ item.subject.name }}
        </RouterLink>
        <p v-if="item.subject.translation" class="mt-1 text-sm break-words opacity-75">
          {{ item.subject.translation }}
        </p>
        <p class="mt-2 text-sm font-medium">
          {{ rankingType === 'top_score' ? '评分' : '评价人数' }}：
          {{ rankingType === 'top_score' ? item.metric_value : formatNumber(item.metric_value) }}
        </p>
      </div>
    </div>
    <div class="border-base-300 mt-4 border-t pt-3 md:ml-36">
      <LatestRatingSummary compact :rating="item.subject.latest_rating" />
    </div>
  </article>
</template>
