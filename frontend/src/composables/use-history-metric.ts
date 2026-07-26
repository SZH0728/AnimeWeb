import { computed, ref, type ComputedRef, type DeepReadonly, type Ref } from 'vue';

import type { RatingHistoryPoint } from '@/api/api-contract';

export type HistoryMetric = 'score' | 'total' | 'rank';

export interface HistoryMetricState {
  readonly metric: Ref<HistoryMetric>;
  readonly points: ComputedRef<readonly DeepReadonly<RatingHistoryPoint>[]>;
  selectMetric(metric: HistoryMetric): void;
}

export function useHistoryMetric(
  items: ComputedRef<readonly DeepReadonly<RatingHistoryPoint>[]>,
): HistoryMetricState {
  const metric = ref<HistoryMetric>('score');
  const points = computed(() => items.value);

  function selectMetric(nextMetric: HistoryMetric): void {
    metric.value = nextMetric;
  }

  return { metric, points, selectMetric };
}
