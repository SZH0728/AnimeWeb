<script setup lang="ts">
import { computed, watch } from 'vue';
import { useRoute } from 'vue-router';

import { ApiError } from '@/api/api-error';
import EmptyState from '@/components/feedback/EmptyState.vue';
import ErrorState from '@/components/feedback/ErrorState.vue';
import LoadingState from '@/components/feedback/LoadingState.vue';
import RatingHistorySection from '@/components/history/RatingHistorySection.vue';
import SubjectMetadata from '@/components/subject/SubjectMetadata.vue';
import { useRatingHistoryRequest } from '@/composables/use-rating-history-request';
import { useSubjectDetailRequest } from '@/composables/use-subject-detail-request';
import { parsePositiveBgmId } from '@/router/route-params';

const route = useRoute();
const detailRequest = useSubjectDetailRequest();
const historyRequest = useRatingHistoryRequest();
const parsedRoute = computed(() => parsePositiveBgmId(route.params));
const isSubjectNotFound = computed(
  () => detailRequest.error.value instanceof ApiError && detailRequest.error.value.status === 404,
);

watch(
  parsedRoute,
  (routeState): void => {
    if (routeState.status === 'invalid') {
      detailRequest.cancel();
      historyRequest.cancel();
      return;
    }

    void detailRequest.load(routeState.value);
    void historyRequest.load(routeState.value);
  },
  { immediate: true },
);
</script>

<template>
  <div class="app-container space-y-8 py-10 sm:py-16">
    <ErrorState
      v-if="parsedRoute.status === 'invalid'"
      :can-retry="false"
      message="地址中的条目编号无效，请检查后重试。"
      title="条目参数无效"
    />

    <LoadingState
      v-else-if="detailRequest.loading.value && detailRequest.data.value === null"
      label="正在加载条目详情"
      variant="detail"
    />

    <ErrorState
      v-else-if="isSubjectNotFound"
      :can-retry="false"
      message="未找到对应的条目。"
      title="条目不存在"
    />

    <ErrorState
      v-else-if="detailRequest.error.value"
      message="暂时无法获取条目详情，请稍后重试。"
      title="条目加载失败"
      @retry-requested="detailRequest.retry"
    />

    <template v-else-if="detailRequest.data.value">
      <SubjectMetadata :subject="detailRequest.data.value" />

      <section aria-labelledby="rating-history-region-title" class="space-y-4">
        <h2 id="rating-history-region-title" class="sr-only">评分历史</h2>
        <LoadingState
          v-if="historyRequest.loading.value && historyRequest.data.value === null"
          label="正在加载评分历史"
        />

        <ErrorState
          v-else-if="historyRequest.error.value"
          message="暂时无法获取评分历史，请稍后重试。"
          title="评分历史加载失败"
          @retry-requested="historyRequest.retry"
        />

        <EmptyState
          v-else-if="historyRequest.data.value && historyRequest.data.value.items.length === 0"
          description="该条目暂时没有可展示的历史评分记录。"
          title="暂无评分历史"
        />

        <RatingHistorySection
          v-else-if="historyRequest.data.value"
          :history="historyRequest.data.value"
        />
      </section>
    </template>
  </div>
</template>
