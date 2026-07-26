<script setup lang="ts">
import { computed, type DeepReadonly } from 'vue';

import type { RatingHistoryResponse } from '@/api/api-contract';
import RatingHistoryChart from '@/components/history/RatingHistoryChart.vue';
import { useHistoryMetric, type HistoryMetric } from '@/composables/use-history-metric';

const props = defineProps<{
  history: DeepReadonly<RatingHistoryResponse>;
}>();

const items = computed(() => props.history.items);
const { metric, points, selectMetric } = useHistoryMetric(items);

const tabs: readonly { readonly metric: HistoryMetric; readonly label: string }[] = [
  { metric: 'score', label: '评分' },
  { metric: 'total', label: '评价人数' },
  { metric: 'rank', label: '综合排名' },
];

function tabId(tabMetric: HistoryMetric): string {
  return `rating-history-tab-${tabMetric}`;
}
</script>

<template>
  <section aria-labelledby="rating-history-title" class="card card-border bg-base-200">
    <div class="card-body space-y-5">
      <header class="space-y-1">
        <h2 id="rating-history-title" class="card-title text-2xl">评分历史</h2>
      </header>

      <div aria-label="选择历史指标" class="tabs tabs-box bg-base-300" role="tablist">
        <button
          v-for="tab in tabs"
          :id="tabId(tab.metric)"
          :key="tab.metric"
          :aria-controls="`rating-history-panel-${tab.metric}`"
          :aria-selected="metric === tab.metric"
          :class="['tab', { 'tab-active': metric === tab.metric }]"
          :tabindex="metric === tab.metric ? 0 : -1"
          role="tab"
          type="button"
          @click="selectMetric(tab.metric)"
        >
          {{ tab.label }}
        </button>
      </div>

      <div
        :id="`rating-history-panel-${metric}`"
        :aria-labelledby="tabId(metric)"
        role="tabpanel"
      >
        <RatingHistoryChart :items="points" :metric="metric" />
      </div>
    </div>
  </section>
</template>
