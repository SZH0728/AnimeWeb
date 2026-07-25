<script setup lang="ts">
import { computed, ref, watch } from 'vue';

import type { SeasonName, SeasonSummary } from '@/api/api-contract';
import { formatSeason } from '@/utils/formatters';

export type SeasonCatalogFilterValue = Readonly<{
  year: number;
  season: SeasonName;
  minTotal: number;
}>;

const props = withDefaults(
  defineProps<{
    availableSeasons: readonly SeasonSummary[];
    initialYear: number;
    initialSeason: SeasonName;
    initialMinTotal: number;
    idPrefix?: string;
    disabled?: boolean;
  }>(),
  {
    idPrefix: 'season-catalog-filter',
    disabled: false,
  },
);

const emit = defineEmits<{
  confirmed: [value: SeasonCatalogFilterValue];
}>();

const draftYear = ref<number | null>(null);
const draftSeason = ref<SeasonName | null>(null);
const draftMinTotal = ref('');
const minTotalError = ref('');

const availableYears = computed(() => {
  const years = new Set<number>();
  for (const season of props.availableSeasons) {
    years.add(season.year);
  }
  return [...years];
});
const seasonsForDraftYear = computed(() =>
  draftYear.value === null
    ? []
    : props.availableSeasons.filter((season) => season.year === draftYear.value),
);
const canSubmit = computed(
  () =>
    !props.disabled &&
    draftYear.value !== null &&
    draftSeason.value !== null &&
    seasonsForDraftYear.value.length > 0,
);

function normalizeSelection(year: number, season: SeasonName): void {
  const firstAvailableSeason = props.availableSeasons[0];
  if (firstAvailableSeason === undefined) {
    draftYear.value = null;
    draftSeason.value = null;
    return;
  }

  const seasonsForYear = props.availableSeasons.filter((item) => item.year === year);
  const selectedSeason = seasonsForYear.find((item) => item.season === season);
  const fallbackSeason = seasonsForYear[0] ?? firstAvailableSeason;

  draftYear.value = fallbackSeason.year;
  draftSeason.value = selectedSeason?.season ?? fallbackSeason.season;
}

function handleYearChanged(event: Event): void {
  const target = event.target;
  if (!(target instanceof HTMLSelectElement)) {
    return;
  }

  const year = Number(target.value);
  if (!Number.isSafeInteger(year) || !availableYears.value.includes(year)) {
    return;
  }

  normalizeSelection(year, draftSeason.value ?? props.initialSeason);
}

function handleSeasonChanged(event: Event): void {
  const target = event.target;
  if (!(target instanceof HTMLSelectElement)) {
    return;
  }

  const selectedSeason = seasonsForDraftYear.value.find((season) => season.season === target.value);
  if (selectedSeason) {
    draftSeason.value = selectedSeason.season;
  }
}

function handleSubmit(): void {
  if (!/^\d+$/.test(draftMinTotal.value)) {
    minTotalError.value = '请输入大于或等于 0 的整数。';
    return;
  }

  const minTotal = Number(draftMinTotal.value);
  if (!Number.isSafeInteger(minTotal) || minTotal < 0) {
    minTotalError.value = '请输入大于或等于 0 的整数。';
    return;
  }

  const selectedSeason = props.availableSeasons.find(
    (item) => item.year === draftYear.value && item.season === draftSeason.value,
  );
  if (!selectedSeason) {
    return;
  }

  minTotalError.value = '';
  emit('confirmed', { year: selectedSeason.year, season: selectedSeason.season, minTotal });
}

watch(
  () =>
    [
      props.availableSeasons,
      props.initialYear,
      props.initialSeason,
      props.initialMinTotal,
    ] as const,
  ([, year, season, minTotal]) => {
    normalizeSelection(year, season);
    draftMinTotal.value = String(minTotal);
    minTotalError.value = '';
  },
  { immediate: true },
);
</script>

<template>
  <section aria-label="季度目录筛选" class="rounded-box bg-base-200 p-4 sm:p-6">
    <form class="flex flex-col gap-4 md:flex-row md:items-center" @submit.prevent="handleSubmit">
      <!-- 年份 -->
      <div class="flex w-full flex-col gap-1 md:flex-1 md:flex-row md:items-center md:gap-2">
        <label class="shrink-0 text-sm font-medium whitespace-nowrap" :for="`${idPrefix}-year`"
          >年份</label
        >
        <select
          :id="`${idPrefix}-year`"
          :disabled="disabled || availableYears.length === 0"
          :value="draftYear ?? ''"
          class="select select-lg w-full min-w-0 flex-1"
          @change="handleYearChanged"
        >
          <option v-if="availableYears.length === 0" value="">暂无可选年份</option>
          <option v-for="year in availableYears" :key="year" :value="year">{{ year }}年</option>
        </select>
      </div>

      <!-- 季度 -->
      <div class="flex w-full flex-col gap-1 md:flex-1 md:flex-row md:items-center md:gap-2">
        <label class="shrink-0 text-sm font-medium whitespace-nowrap" :for="`${idPrefix}-season`"
          >季度</label
        >
        <select
          :id="`${idPrefix}-season`"
          :disabled="disabled || seasonsForDraftYear.length === 0"
          :value="draftSeason ?? ''"
          class="select select-lg w-full min-w-0 flex-1"
          @change="handleSeasonChanged"
        >
          <option v-if="seasonsForDraftYear.length === 0" value="">暂无可选季度</option>
          <option v-for="season in seasonsForDraftYear" :key="season.season" :value="season.season">
            {{ formatSeason(season.season) }}
          </option>
        </select>
      </div>

      <!-- 最低评价人数 -->
      <div class="flex w-full flex-col gap-1 md:flex-1 md:flex-row md:items-center md:gap-2">
        <label class="shrink-0 text-sm font-medium whitespace-nowrap" :for="`${idPrefix}-min-total`"
          >最低评价人数</label
        >
        <div class="flex w-full min-w-0 flex-1 flex-col gap-1">
          <input
            :id="`${idPrefix}-min-total`"
            v-model="draftMinTotal"
            :aria-describedby="minTotalError ? `${idPrefix}-min-total-error` : undefined"
            :aria-invalid="Boolean(minTotalError)"
            :disabled="disabled || availableYears.length === 0"
            class="input input-sm w-full min-w-0"
            inputmode="numeric"
            min="0"
            name="min-total"
            step="1"
            type="number"
          />
          <p
            v-if="minTotalError"
            :id="`${idPrefix}-min-total-error`"
            class="text-error text-sm"
            role="alert"
          >
            {{ minTotalError }}
          </p>
        </div>
      </div>

      <!-- 提交按钮：改用 btn-lg 保持对齐 -->
      <button
        class="btn btn-primary btn-lg w-full shrink-0 md:w-auto"
        :disabled="!canSubmit"
        type="submit"
      >
        应用
      </button>
    </form>
  </section>
</template>