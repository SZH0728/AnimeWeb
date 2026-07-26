<script setup lang="ts">
import { computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { appConfig } from '@/app/config';
import EmptyState from '@/components/feedback/EmptyState.vue';
import ErrorState from '@/components/feedback/ErrorState.vue';
import LoadingState from '@/components/feedback/LoadingState.vue';
import MinTotalFilter from '@/components/filters/MinTotalFilter.vue';
import PaginationNav from '@/components/navigation/PaginationNav.vue';
import { useRankingRequest } from '@/composables/use-ranking-request';
import { parseRankingRoute } from '@/router/route-params';
import type { MostRatedRankingRequest, TopScoreRankingRequest } from '@/types/api-requests';
import {
  buildMostRatedRankingQuery,
  buildTopScoreRankingQuery,
} from '@/utils/query-params';
import RankingListItem from '@/components/ranking/RankingListItem.vue';

const route = useRoute();
const router = useRouter();
const rankingRequest = useRankingRequest();
const ranking = computed(() => route.meta.ranking);
const parsedRoute = computed(() => {
  const rankingConfig = ranking.value;
  return rankingConfig === undefined
    ? { status: 'invalid' as const }
    : parseRankingRoute(route.query, rankingConfig.type);
});
const canUseMinTotalFilter = computed(
  () =>
    ranking.value?.supportsMinTotal === true &&
    parsedRoute.value.status === 'valid' &&
    parsedRoute.value.value.type === 'top_score',
);

function toRouteQuery(
  request: TopScoreRankingRequest | MostRatedRankingRequest,
): Record<string, string> {
  const rankingConfig = ranking.value;
  if (rankingConfig === undefined) {
    return {};
  }

  const query =
    'minTotal' in request
      ? buildTopScoreRankingQuery(request)
      : buildMostRatedRankingQuery(request);

  return Object.fromEntries(new URLSearchParams(query));
}

function navigateToRanking(request: TopScoreRankingRequest | MostRatedRankingRequest): void {
  const rankingConfig = ranking.value;
  if (rankingConfig === undefined) {
    return;
  }

  window.scrollTo({ top: 0 });
  void router.push({ name: route.name, query: toRouteQuery(request) });
}

function handlePageRequested(page: number): void {
  if (parsedRoute.value.status !== 'valid') {
    return;
  }

  navigateToRanking({ ...parsedRoute.value.value.request, page });
}

function handleMinTotalChanged(minTotal: number): void {
  if (
    !canUseMinTotalFilter.value ||
    !Number.isSafeInteger(minTotal) ||
    minTotal < 0 ||
    parsedRoute.value.status !== 'valid' ||
    parsedRoute.value.value.type !== 'top_score'
  ) {
    return;
  }

  navigateToRanking({
    minTotal,
    page: appConfig.defaultPage,
    pageSize: parsedRoute.value.value.request.pageSize,
  });
}

watch(
  parsedRoute,
  (routeState) => {
    if (routeState.status === 'invalid') {
      rankingRequest.cancel();
      return;
    }

    void rankingRequest.load(routeState.value);
  },
  { immediate: true },
);
</script>

<template>
  <main class="app-container space-y-8 py-10 sm:py-16">
    <ErrorState
      v-if="parsedRoute.status === 'invalid'"
      :can-retry="false"
      message="地址中的榜单参数无效，请检查后重试。"
      title="榜单参数无效"
    />

    <template v-else-if="ranking">
      <section aria-labelledby="ranking-title" class="space-y-4">
        <div>
          <h1 id="ranking-title" class="text-3xl font-bold tracking-tight">{{ ranking.title }}</h1>
          <p class="text-base-content/70 mt-2">{{ ranking.description }}</p>
        </div>
        <MinTotalFilter
          v-if="canUseMinTotalFilter && parsedRoute.value.type === 'top_score'"
          :disabled="rankingRequest.loading.value"
          :model-value="parsedRoute.value.request.minTotal"
          @min-total-changed="handleMinTotalChanged"
        />
      </section>

      <LoadingState v-if="rankingRequest.loading.value" label="正在加载榜单" variant="page" />

      <ErrorState
        v-else-if="rankingRequest.error.value"
        message="暂时无法获取榜单，请稍后重试。"
        title="榜单加载失败"
        @retry-requested="rankingRequest.retry"
      />

      <EmptyState
        v-else-if="rankingRequest.data.value && rankingRequest.data.value.items.length === 0"
        description="暂时没有符合条件的作品。"
        title="暂无榜单数据"
      />

      <section v-else-if="rankingRequest.data.value" aria-label="榜单结果" class="space-y-4">
        <p class="text-base-content/70 text-sm" aria-live="polite">
          共 {{ rankingRequest.data.value.pagination.total }} 项结果
        </p>

        <ol class="space-y-3">
          <li v-for="item in rankingRequest.data.value.items" :key="item.subject.bgm_id">
            <RankingListItem :item="item" :ranking-type="ranking.type" />
          </li>
        </ol>

        <PaginationNav
          :page="rankingRequest.data.value.pagination.page"
          :total="rankingRequest.data.value.pagination.total"
          :total-pages="rankingRequest.data.value.pagination.total_pages"
          @page-requested="handlePageRequested"
        />
      </section>
    </template>
  </main>
</template>
