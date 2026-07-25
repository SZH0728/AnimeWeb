<script setup lang="ts">
import { computed } from 'vue';

import type { SeasonSummary } from '@/api/api-contract';
import { formatNumber, formatSeason } from '@/utils/formatters';

const props = withDefaults(
  defineProps<{
    seasons: readonly SeasonSummary[];
    selected: SeasonSummary | null;
    id?: string;
    disabled?: boolean;
  }>(),
  {
    id: 'season-selector',
    disabled: false,
  },
);

const emit = defineEmits<{
  'season-selected': [season: SeasonSummary];
}>();

const selectedKey = computed(() =>
  props.selected ? `${props.selected.year}-${props.selected.season}` : '',
);

function handleSelection(event: Event): void {
  const target = event.target;
  if (!(target instanceof HTMLSelectElement)) {
    return;
  }

  const season = props.seasons.find((item) => `${item.year}-${item.season}` === target.value);
  if (season) {
    emit('season-selected', season);
  }
}
</script>

<template>
  <div class="flex w-full flex-col gap-1 sm:w-auto">
    <label class="text-sm font-medium" :for="id">季度</label>
    <select
      :id="id"
      :disabled="disabled || seasons.length === 0"
      :value="selectedKey"
      class="select w-full sm:w-auto"
      @change="handleSelection"
    >
      <option v-if="seasons.length === 0" value="">暂无可选季度</option>
      <option
        v-for="season in seasons"
        :key="`${season.year}-${season.season}`"
        :value="`${season.year}-${season.season}`"
      >
        {{ season.year }}年{{ formatSeason(season.season) }}（{{
          formatNumber(season.subject_count)
        }}
        部）
      </option>
    </select>
  </div>
</template>
