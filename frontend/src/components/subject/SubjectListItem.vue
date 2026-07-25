<script setup lang="ts">
import type { SubjectListItem as SubjectListItemData } from '@/api/api-contract';
import { formatApiDate } from '@/utils/formatters';

import CoverImage from './CoverImage.vue';
import LatestRatingSummary from './LatestRatingSummary.vue';

type SubjectListItemProps = Omit<SubjectListItemData, 'tags'> & {
  tags: readonly string[];
};

defineProps<{
  subject: SubjectListItemProps;
}>();
</script>

<template>
  <article class="rounded-box bg-base-200 hover:bg-base-300 shadow-sm transition-colors">
    <RouterLink
      :to="{ name: 'subject-detail', params: { bgmId: subject.bgm_id } }"
      :aria-label="`查看${subject.name}详情`"
      class="group block p-4 text-inherit no-underline"
    >
      <div class="grid grid-cols-[6rem_1fr] gap-x-4 sm:grid-cols-[7rem_1fr]">
        <div class="w-24 shrink-0 sm:row-span-2 sm:w-28">
          <CoverImage :alt="`${subject.name}封面`" :cover-url="subject.cover_url" />
        </div>

        <div class="min-w-0 space-y-2.5">
          <div class="space-y-1">
            <div class="flex items-baseline justify-between gap-2">
              <h3 class="min-w-0 text-lg font-semibold break-words">
                {{ subject.name }}
              </h3>

              <span
                v-if="subject.air_date"
                class="hidden shrink-0 text-sm opacity-75 sm:inline-block"
              >
                {{ formatApiDate(subject.air_date) }}
              </span>
            </div>

            <p v-if="subject.translation" class="text-sm wrap-break-word opacity-75">
              {{ subject.translation }}
            </p>

            <p v-if="subject.air_date" class="text-sm opacity-75 sm:hidden">
              {{ formatApiDate(subject.air_date) }}
            </p>
          </div>

          <ul
            v-if="subject.tags.length > 0"
            class="flex scrollbar-none flex-nowrap gap-1 overflow-x-auto sm:flex-wrap"
            aria-label="标签"
          >
            <li v-for="tag in subject.tags" :key="tag" class="badge badge-sm shrink-0">
              {{ tag }}
            </li>
          </ul>
        </div>

        <div class="border-base-300 col-span-2 mt-4 border-t pt-3 sm:col-span-1 sm:mt-2.5">
          <LatestRatingSummary :rating="subject.latest_rating" />
        </div>
      </div>
    </RouterLink>
  </article>
</template>
