<script setup lang="ts">
import * as echarts from 'echarts';
import { nextTick, onBeforeUnmount, ref, watch, type DeepReadonly } from 'vue';

import type { RatingHistoryPoint } from '@/api/api-contract';
import type { HistoryMetric } from '@/composables/use-history-metric';

const props = defineProps<{
  metric: HistoryMetric;
  items: readonly DeepReadonly<RatingHistoryPoint>[];
}>();

const chartElement = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;
let resizeObserver: ResizeObserver | null = null;

const metricLabels: Readonly<Record<HistoryMetric, string>> = {
  score: '评分',
  total: '评价人数',
  rank: 'Bangumi 综合排名',
};

function updateChart(): void {
  if (chart === null || props.items.length === 0) {
    return;
  }

  chart.setOption(
    {
      animation: false,
      grid: { top: 44, right: 20, bottom: 64, left: 52, containLabel: true },
      tooltip: {
        trigger: 'axis',
      },
      xAxis: {
        type: 'category',
        data: props.items.map((item) => item.date),
        axisLabel: { rotate: 35 },
      },
      yAxis: {
        type: 'value',
        name: metricLabels[props.metric],
        inverse: props.metric === 'rank',
      },
      series: [
        {
          type: 'line',
          name: metricLabels[props.metric],
          data: props.items.map((item) => item[props.metric]),
          connectNulls: false,
          showSymbol: false,
        },
      ],
    },
    { notMerge: true },
  );
}

async function initializeChart(): Promise<void> {
  await nextTick();
  if (chartElement.value === null || props.items.length === 0) {
    return;
  }

  chart ??= echarts.init(chartElement.value);
  resizeObserver ??= new ResizeObserver((): void => {
    chart?.resize();
  });
  resizeObserver.observe(chartElement.value);
  updateChart();
}

watch(
  () => [props.metric, props.items] as const,
  (): void => {
    void initializeChart();
    updateChart();
  },
  { immediate: true },
);

onBeforeUnmount((): void => {
  resizeObserver?.disconnect();
  chart?.dispose();
  resizeObserver = null;
  chart = null;
});
</script>

<template>
  <div
    ref="chartElement"
    aria-label="评分历史趋势图"
    class="h-80 w-full min-w-0"
    role="img"
  />
</template>
