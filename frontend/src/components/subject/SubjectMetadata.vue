<script setup lang="ts">
import type { SubjectDetail } from '@/api/api-contract';
import CoverImage from '@/components/subject/CoverImage.vue';
import LatestRatingSummary from '@/components/subject/LatestRatingSummary.vue';
import { formatApiDate, formatSeason } from '@/utils/formatters';

defineProps<{
  subject: SubjectDetail;
}>();
</script>

<template>
  <article class="card card-border bg-base-200">
    <div class="card-body gap-6 sm:grid sm:grid-cols-[minmax(12rem,16rem)_1fr]">
      <div class="mx-auto max-w-50 sm:mx-0 sm:max-w-none">
        <CoverImage :alt="subject.name" :cover-url="subject.cover_url" />
      </div>

      <div class="space-y-6">
        <header class="space-y-2">
          <h1 id="subject-detail-title" class="text-3xl font-bold tracking-tight sm:text-4xl">
            {{ subject.name }}
          </h1>
          <p v-if="subject.translation" class="text-base-content/70 text-lg">
            {{ subject.translation }}
          </p>
          <a
            :href="subject.url"
            class="btn btn-primary btn-outline btn-sm mt-2 shrink-0"
            rel="noopener noreferrer"
            target="_blank"
          >
            在 Bangumi 查看条目
          </a>
        </header>

        <dl class="grid gap-x-6 gap-y-4 sm:grid-cols-2">
          <div v-if="subject.aliases.length > 0" class="space-y-1 sm:col-span-2">
            <dt class="text-base-content/70 text-sm">别名</dt>
            <dd>{{ subject.aliases.join(' / ') }}</dd>
          </div>
          <div v-if="subject.air_date">
            <dt class="text-base-content/70 text-sm">首播日期</dt>
            <dd>
              <time :datetime="subject.air_date">{{ formatApiDate(subject.air_date) }}</time>
            </dd>
          </div>
          <div v-if="subject.year !== null || subject.season !== null">
            <dt class="text-base-content/70 text-sm">季度</dt>
            <dd>
              <template v-if="subject.year !== null">{{ subject.year }} 年</template>
              <template v-if="subject.season !== null">{{ formatSeason(subject.season) }}</template>
            </dd>
          </div>
          <div v-if="subject.tags.length > 0" class="space-y-2 sm:col-span-2">
            <dt class="text-base-content/70 text-sm">标签</dt>
            <dd class="flex flex-wrap gap-2">
              <span v-for="tag in subject.tags" :key="tag" class="badge badge-outline">{{
                tag
              }}</span>
            </dd>
          </div>
        </dl>

        <section class="space-y-2" aria-labelledby="latest-rating-title">
          <h2 id="latest-rating-title" class="text-xl font-semibold">最新评分</h2>
          <LatestRatingSummary :rating="subject.latest_rating" />
        </section>

        <section v-if="subject.summary" class="space-y-2" aria-labelledby="subject-summary-title">
          <h2 id="subject-summary-title" class="text-xl font-semibold">简介</h2>
          <p class="text-base-content/80 leading-7 whitespace-pre-line">{{ subject.summary }}</p>
        </section>
      </div>
    </div>
  </article>
</template>
