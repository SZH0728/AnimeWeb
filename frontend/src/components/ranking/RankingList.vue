<script setup lang="ts">
import type { RankingItem } from '@/api/api-contract';
import type { RankingType } from '@/types/api-requests';

import RankingListItem from './RankingListItem.vue';

defineProps<{
  items: readonly RankingItem[];
  rankingType: RankingType;
}>();
</script>

<template>
  <ol class="space-y-3">
    <li v-for="item in items" :key="item.subject.bgm_id">
      <RankingListItem :item="item" :ranking-type="rankingType" />
    </li>
  </ol>
</template>
