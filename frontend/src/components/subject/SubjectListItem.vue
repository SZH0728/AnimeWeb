<script setup lang="ts">
import type { SubjectListItem as SubjectListItemData } from '@/api/api-contract';
import { formatApiDate, formatSeason } from '@/utils/formatters';

import CoverImage from './CoverImage.vue';
import LatestRatingSummary from './LatestRatingSummary.vue';

defineProps<{
  subject: SubjectListItemData;
}>();
</script>

<template>
  <article class="rounded-box bg-base-200 p-4 shadow-sm">
    <div class="flex gap-4">
      <RouterLink
        :aria-label="`查看${subject.name}详情`"
        :to="{ name: 'subject-detail', params: { bgmId: subject.bgm_id } }"
        class="w-24 shrink-0 sm:w-28"
      >
        <CoverImage :alt="`${subject.name}封面`" :cover-url="subject.cover_url" />
      </RouterLink>
      <div class="min-w-0 flex-1 space-y-3">
        <div>
          <RouterLink
            :to="{ name: 'subject-detail', params: { bgmId: subject.bgm_id } }"
            class="link text-lg font-semibold break-words"
          >
            {{ subject.name }}
          </RouterLink>
          <p v-if="subject.translation" class="mt-1 text-sm break-words opacity-75">
            {{ subject.translation }}
          </p>
        </div>
        <p
          v-if="subject.air_date || (subject.year && subject.season)"
          class="flex flex-wrap gap-x-3 gap-y-1 text-sm opacity-75"
        >
          <span v-if="subject.air_date">首播：{{ formatApiDate(subject.air_date) }}</span>
          <span v-if="subject.year && subject.season"
            >{{ subject.year }}年{{ formatSeason(subject.season) }}</span
          >
        </p>
        <ul v-if="subject.tags.length > 0" class="flex flex-wrap gap-1" aria-label="标签">
          <li v-for="tag in subject.tags" :key="tag" class="badge badge-sm">{{ tag }}</li>
        </ul>
      </div>
    </div>
    <div class="border-base-300 mt-4 border-t pt-3 lg:ml-32">
      <LatestRatingSummary :rating="subject.latest_rating" />
    </div>
  </article>
</template>
