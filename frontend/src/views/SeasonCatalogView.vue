<script setup lang="ts">
import { computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { appConfig } from '@/app/config';
import EmptyState from '@/components/feedback/EmptyState.vue';
import ErrorState from '@/components/feedback/ErrorState.vue';
import LoadingState from '@/components/feedback/LoadingState.vue';
import SeasonCatalogFilter, {
  type SeasonCatalogFilterValue,
} from '@/components/filters/SeasonCatalogFilter.vue';
import PaginationNav from '@/components/navigation/PaginationNav.vue';
import SubjectListItem from '@/components/subject/SubjectListItem.vue';
import { useSeasonsRequest } from '@/composables/use-seasons-request';
import { useSubjectListRequest } from '@/composables/use-subject-list-request';
import { parseSeasonCatalogRoute } from '@/router/route-params';
import type { SubjectListRequest } from '@/types/api-requests';
import { formatSeason } from '@/utils/formatters';
import { buildSeasonQuery } from '@/utils/query-params';

const route = useRoute();
const router = useRouter();
const seasonsRequest = useSeasonsRequest();
const subjectsRequest = useSubjectListRequest();

const parsedRoute = computed(() => parseSeasonCatalogRoute(route.query));
const availableSeasons = computed(() => seasonsRequest.data.value?.items ?? []);
const hasAvailableSeasons = computed(() => availableSeasons.value.length > 0);
const hasAvailableRouteSelection = computed(() => {
  const routeState = parsedRoute.value;
  return (
    routeState.status === 'valid' &&
    availableSeasons.value.some(
      (season) => season.year === routeState.value.year && season.season === routeState.value.season,
    )
  );
});
const canUseCatalogControls = computed(
  () => hasAvailableRouteSelection.value && !seasonsRequest.loading.value,
);

function toRouteQuery(request: SubjectListRequest): Record<string, string> {
  return Object.fromEntries(new URLSearchParams(buildSeasonQuery(request)));
}

function navigateToCatalog(request: SubjectListRequest): void {
  window.scrollTo({ top: 0 });
  void router.push({ name: 'seasons', query: toRouteQuery(request) });
}

function handleFilterConfirmed(value: SeasonCatalogFilterValue): void {
  const routeState = parsedRoute.value;
  const isAvailableSeason = availableSeasons.value.some(
    (season) => season.year === value.year && season.season === value.season,
  );
  if (
    routeState.status !== 'valid' ||
    !Number.isSafeInteger(value.year) ||
    value.year < 1000 ||
    value.year > 9999 ||
    !Number.isSafeInteger(value.minTotal) ||
    value.minTotal < 0 ||
    !isAvailableSeason
  ) {
    return;
  }

  navigateToCatalog({
    year: value.year,
    season: value.season,
    minTotal: value.minTotal,
    page: appConfig.defaultPage,
    pageSize: routeState.value.pageSize,
  });
}

function handlePageRequested(page: number): void {
  if (parsedRoute.value.status !== 'valid') {
    return;
  }

  navigateToCatalog({ ...parsedRoute.value.value, page });
}

watch(
  [
    parsedRoute,
    () => seasonsRequest.data.value,
    () => seasonsRequest.loading.value,
    () => seasonsRequest.error.value,
  ],
  ([routeState, seasonsData, isLoading, seasonsError]) => {
    if (routeState.status === 'invalid') {
      subjectsRequest.cancel();
      return;
    }

    if (isLoading || seasonsError !== null || seasonsData === null) {
      subjectsRequest.cancel();
      return;
    }

    if (seasonsData.items.length === 0) {
      subjectsRequest.cancel();
      return;
    }

    if (routeState.status === 'selection-required') {
      subjectsRequest.cancel();
      const firstSeason = seasonsData.items[0];
      if (firstSeason === undefined) {
        return;
      }

      void router.replace({
        name: 'seasons',
        query: toRouteQuery({
          year: firstSeason.year,
          season: firstSeason.season,
          minTotal: routeState.value.minTotal,
          page: routeState.value.page,
          pageSize: routeState.value.pageSize,
        }),
      });
      return;
    }

    if (!hasAvailableRouteSelection.value) {
      subjectsRequest.cancel();
      return;
    }

    void subjectsRequest.load(routeState.value);
  },
  { immediate: true },
);

onMounted((): void => {
  void seasonsRequest.load(undefined);
});
</script>

<template>
  <div class="app-container space-y-8 py-10 sm:py-16">
    <div class="space-y-2">
      <h1 class="text-3xl font-bold tracking-tight sm:text-4xl">季度目录</h1>
      <p class="text-base-content/70">按季度和最低评价人数浏览作品评分快照。</p>
    </div>

    <ErrorState
      v-if="parsedRoute.status === 'invalid'"
      :can-retry="false"
      message="地址中的季度目录参数无效，请检查后重试。"
      title="目录参数无效"
    />

    <LoadingState
      v-else-if="seasonsRequest.loading.value && seasonsRequest.data.value === null"
      label="正在加载可选季度"
      variant="page"
    />

    <ErrorState
      v-else-if="seasonsRequest.error.value"
      message="暂时无法获取可选季度，请稍后重试。"
      title="季度加载失败"
      @retry-requested="seasonsRequest.retry"
    />

    <EmptyState
      v-else-if="!hasAvailableSeasons"
      description="暂时没有可供浏览的季度，因此不会加载作品目录。"
      title="暂无可选季度"
    />

    <ErrorState
      v-else-if="parsedRoute.status === 'valid' && !hasAvailableRouteSelection"
      :can-retry="false"
      message="该季度当前不可用，请从可选季度中重新选择。"
      title="季度不可用"
    />

    <template v-else-if="parsedRoute.status === 'valid'">
      <SeasonCatalogFilter
        :available-seasons="availableSeasons"
        :disabled="!canUseCatalogControls"
        :initial-min-total="parsedRoute.value.minTotal"
        :initial-season="parsedRoute.value.season"
        :initial-year="parsedRoute.value.year"
        @confirmed="handleFilterConfirmed"
      />

      <section aria-labelledby="season-subjects-title" class="space-y-5">
        <div>
          <p v-if="subjectsRequest.data.value" class="text-base-content/70 mt-1 text-sm">
            {{ subjectsRequest.data.value.meta.year }} 年{{
              formatSeason(subjectsRequest.data.value.meta.season)
            }}，共 {{ subjectsRequest.data.value.pagination.total }} 项结果
          </p>
        </div>

        <LoadingState v-if="subjectsRequest.loading.value" label="正在加载季度作品" />

        <ErrorState
          v-else-if="subjectsRequest.error.value"
          message="暂时无法获取季度作品，请稍后重试。"
          title="目录加载失败"
          @retry-requested="subjectsRequest.retry"
        />

        <EmptyState
          v-else-if="subjectsRequest.data.value && subjectsRequest.data.value.items.length === 0"
          description="请调整季度或最低评价人数后重试。"
          title="没有符合条件的作品"
        />

        <template v-else-if="subjectsRequest.data.value">
          <div class="space-y-4">
            <SubjectListItem
              v-for="subject in subjectsRequest.data.value.items"
              :key="subject.bgm_id"
              :subject="subject"
            />
          </div>
          <PaginationNav
            :page="subjectsRequest.data.value.pagination.page"
            :total="subjectsRequest.data.value.pagination.total"
            :total-pages="subjectsRequest.data.value.pagination.total_pages"
            @page-requested="handlePageRequested"
          />
        </template>
      </section>
    </template>
  </div>
</template>
