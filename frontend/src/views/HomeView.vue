<script setup lang="ts">
import { computed, onMounted } from 'vue';

import { appConfig } from '@/app/config';
import EmptyState from '@/components/feedback/EmptyState.vue';
import ErrorState from '@/components/feedback/ErrorState.vue';
import LoadingState from '@/components/feedback/LoadingState.vue';
import SubjectListItem from '@/components/subject/SubjectListItem.vue';
import { useHomeRequest } from '@/composables/use-home-request';
import { formatSeason } from '@/utils/formatters';
import { buildSeasonQuery } from '@/utils/query-params';

const homeRequest = useHomeRequest();

const latestSeasonLink = computed(() => {
  const latestSeason = homeRequest.data.value?.latest_season;
  if (latestSeason === null || latestSeason === undefined) {
    return null;
  }

  return {
    name: 'seasons',
    query: Object.fromEntries(
      new URLSearchParams(
        buildSeasonQuery({
          year: latestSeason.year,
          season: latestSeason.season,
          minTotal: appConfig.defaultMinTotal,
          page: appConfig.defaultPage,
          pageSize: appConfig.defaultPageSize,
        }),
      ),
    ),
  };
});

onMounted((): void => {
  void homeRequest.load(undefined);
});
</script>

<template>
  <main class="app-container space-y-10 py-10 sm:py-16">
    <LoadingState v-if="homeRequest.loading.value" label="正在加载首页内容" variant="list" />

    <ErrorState
      v-else-if="homeRequest.error.value"
      message="暂时无法获取首页内容，请稍后重试。"
      title="首页加载失败"
      @retry-requested="homeRequest.retry"
    />

    <div v-else-if="homeRequest.data.value" class="space-y-10">
      <section aria-labelledby="latest-season-title" class="space-y-5">
        <div class="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 id="latest-season-title" class="text-2xl font-bold tracking-tight">最新季度</h2>
            <p class="text-base-content/70 mt-1 text-sm">查看最近一季动画的评分快照。</p>
          </div>
          <RouterLink v-if="latestSeasonLink" :to="latestSeasonLink" class="btn btn-sm">
            查看完整目录
          </RouterLink>
        </div>

        <template v-if="homeRequest.data.value.latest_season">
          <p class="text-base-content/70 text-sm">
            {{ homeRequest.data.value.latest_season.year }} 年{{
              formatSeason(homeRequest.data.value.latest_season.season)
            }}，共 {{ homeRequest.data.value.latest_season.subject_count }} 部作品。
          </p>
          <div v-if="homeRequest.data.value.latest_season.items.length > 0" class="space-y-4">
            <SubjectListItem
              v-for="subject in homeRequest.data.value.latest_season.items"
              :key="subject.bgm_id"
              :subject="subject"
            />
          </div>
          <EmptyState v-else description="该季度暂时没有可展示的作品。" title="暂无最新季度预览" />
        </template>
        <EmptyState v-else description="暂时没有可用于首页展示的最新季度。" title="暂无最新季度" />
      </section>

      <div class="grid gap-10 md:grid-cols-2">
        <section aria-labelledby="top-score-title" class="space-y-5">
          <div class="flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 id="top-score-title" class="text-2xl font-bold tracking-tight">高分榜预览</h2>
              <p class="text-base-content/70 mt-1 text-sm">按最新评分整理的热门作品。</p>
            </div>
            <RouterLink :to="{ name: 'ranking-top-score' }" class="btn btn-sm"
              >查看完整榜单</RouterLink
            >
          </div>
          <div v-if="homeRequest.data.value.top_score.items.length > 0" class="space-y-4">
            <SubjectListItem
              v-for="subject in homeRequest.data.value.top_score.items"
              :key="subject.bgm_id"
              :subject="subject"
            />
          </div>
          <EmptyState v-else description="暂时没有可展示的高分作品。" title="暂无高分榜预览" />
        </section>

        <section aria-labelledby="most-rated-title" class="space-y-5">
          <div class="flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 id="most-rated-title" class="text-2xl font-bold tracking-tight">最多评分预览</h2>
              <p class="text-base-content/70 mt-1 text-sm">获得最多评分的作品快照。</p>
            </div>
            <RouterLink :to="{ name: 'ranking-most-rated' }" class="btn btn-sm"
              >查看完整榜单</RouterLink
            >
          </div>
          <div v-if="homeRequest.data.value.most_rated.items.length > 0" class="space-y-4">
            <SubjectListItem
              v-for="subject in homeRequest.data.value.most_rated.items"
              :key="subject.bgm_id"
              :subject="subject"
            />
          </div>
          <EmptyState v-else description="暂时没有可展示的评分数据。" title="暂无最多评分预览" />
        </section>
      </div>
    </div>
  </main>
</template>
