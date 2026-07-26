<script setup lang="ts">
import { computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import EmptyState from '@/components/feedback/EmptyState.vue';
import ErrorState from '@/components/feedback/ErrorState.vue';
import LoadingState from '@/components/feedback/LoadingState.vue';
import PaginationNav from '@/components/navigation/PaginationNav.vue';
import SubjectListItem from '@/components/subject/SubjectListItem.vue';
import { useSearchRequest } from '@/composables/use-search-request';
import { parseSearchRoute } from '@/router/route-params';
import type { SearchRequest } from '@/types/api-requests';
import { buildSearchQuery } from '@/utils/query-params';

const route = useRoute();
const router = useRouter();
const searchRequest = useSearchRequest();
const parsedRoute = computed(() => parseSearchRoute(route.query));

function toRouteQuery(request: SearchRequest): Record<string, string> {
  return Object.fromEntries(new URLSearchParams(buildSearchQuery(request)));
}

function handlePageRequested(page: number): void {
  if (parsedRoute.value.status !== 'valid') {
    return;
  }

  window.scrollTo({ top: 0 });
  void router.push({
    name: 'search',
    query: toRouteQuery({ ...parsedRoute.value.value, page }),
  });
}

watch(
  parsedRoute,
  (routeState) => {
    if (routeState.status === 'invalid') {
      searchRequest.cancel();
      return;
    }

    void searchRequest.load(routeState.value);
  },
  { immediate: true },
);
</script>

<template>
  <main class="app-container space-y-8 py-10 sm:py-16">
    <ErrorState
      v-if="parsedRoute.status === 'invalid'"
      :can-retry="false"
      message="地址中的搜索参数无效，请检查后重试。"
      title="搜索参数无效"
    />

    <template v-else>
      <section aria-labelledby="search-title" class="space-y-2">
        <h1 id="search-title" class="text-3xl font-bold tracking-tight">搜索作品</h1>
        <p v-if="searchRequest.data.value" class="text-base-content/70" aria-live="polite">
          “{{ searchRequest.data.value.meta.q }}”共找到
          {{ searchRequest.data.value.pagination.total }} 项结果。
        </p>
      </section>

      <LoadingState v-if="searchRequest.loading.value" label="正在搜索作品" variant="page" />

      <ErrorState
        v-else-if="searchRequest.error.value"
        message="暂时无法搜索作品，请稍后重试。"
        title="搜索失败"
        @retry-requested="searchRequest.retry"
      />

      <EmptyState
        v-else-if="searchRequest.data.value && searchRequest.data.value.items.length === 0"
        description="请尝试使用其他关键词搜索。"
        title="没有匹配的作品"
      />

      <section v-else-if="searchRequest.data.value" aria-label="搜索结果" class="space-y-4">
        <div class="space-y-4">
          <article
            v-for="subject in searchRequest.data.value.items"
            :key="subject.bgm_id"
            class="space-y-2"
          >
            <SubjectListItem :subject="subject" />
          </article>
        </div>
        <PaginationNav
          :page="searchRequest.data.value.pagination.page"
          :total="searchRequest.data.value.pagination.total"
          :total-pages="searchRequest.data.value.pagination.total_pages"
          @page-requested="handlePageRequested"
        />
      </section>
    </template>
  </main>
</template>
